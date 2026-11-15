import os
import random
import secrets
import string
import sys
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA_DIR = os.getenv("DATA_DIR", "/data")
STRINGS_PATH = os.path.join(DATA_DIR, "random_strings")


def get_session(app_name: str) -> SparkSession:
    spark_master_url = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")
    return (
        SparkSession.builder
        .appName(app_name)
        .master(spark_master_url)
        .getOrCreate()
    )


def stop(spark: SparkSession) -> None:
    """Zatrzymuje sesje; opcjonalnie czeka, zeby mozna bylo obejrzec Spark UI (:4040)."""
    wait = int(os.getenv("UI_WAIT_SECONDS", "0"))
    if wait > 0:
        print(f"Spark UI available at http://localhost:4040 for {wait}s ...")
        time.sleep(wait)
    spark.stop()


def partition_seed(base_seed: int, partition_index: int) -> int:
    """Niezalezne ziarno dla partycji.

    base_seed jest losowany raz (na driverze) z kryptograficznego zrodla entropii,
    wiec kazde uruchomienie daje inne liczby. Indeks partycji jest doklejany
    w dolnych 32 bitach, wiec dwie rozne partycje NIGDY nie dostana tego samego
    ziarna (odwzorowanie (base_seed, idx) -> seed jest roznowartosciowe).
    """
    return (base_seed << 32) | partition_index


def example() -> None:
    spark = get_session("Example app")

    df = spark.createDataFrame(
        data=[
            (1, "Alice"),
            (2, "Bob"),
            (3, "Charlie"),
        ],
        schema=["id", "name"],
    )

    df.show()

    print(f"Total rows: {df.count()}")

    stop(spark)


# ---------------------------------------------------------------- Zadanie 6.2

def generate_numbers(total: int = 10_000_000, partitions: int = 10) -> None:
    spark = get_session("Number generator app")
    sc = spark.sparkContext

    print(f"Spark version: {spark.version}")

    # lista 10 liczb - kazda mowi ile doubli ma wygenerowac dana partycja
    per_partition = [total // partitions] * partitions
    per_partition[-1] += total - sum(per_partition)

    base_seed = secrets.randbits(64)

    def gen(partition_index, iterator):
        rng = random.Random(partition_seed(base_seed, partition_index))
        for count in iterator:
            for _ in range(count):
                yield rng.random()

    numbers = (
        sc.parallelize(per_partition, partitions)
        .mapPartitionsWithIndex(gen)
        .cache()
    )

    stats = numbers.stats()
    sizes = numbers.glom().map(len).collect()
    # pierwsza liczba z kazdej partycji - powinny byc rozne
    firsts = numbers.mapPartitions(lambda it: [next(it, None)]).collect()

    print(f"Base seed:            {base_seed}")
    print(f"Partitions:           {numbers.getNumPartitions()}")
    print(f"Elements / partition: {sizes}")
    print(f"Stats:                {stats}")
    print(f"First value per partition: {firsts}")
    print(f"All partitions start differently: {len(set(firsts)) == len(firsts)}")

    numbers.unpersist()
    stop(spark)


# ---------------------------------------------------------------- Zadanie 6.3

def create_random_strings(
    count: int = int(os.getenv("STRINGS_COUNT", "1000000")),
    min_len: int = int(os.getenv("STRING_MIN_LEN", "5")),
    max_len: int = int(os.getenv("STRING_MAX_LEN", "50")),
    partitions: int = 10,
    path: str = STRINGS_PATH,
) -> None:
    if not 0 <= min_len <= max_len:
        raise ValueError(f"Invalid length range: [{min_len}, {max_len}]")

    spark = get_session("Create random strings app")
    sc = spark.sparkContext

    per_partition = [count // partitions] * partitions
    per_partition[-1] += count - sum(per_partition)

    base_seed = secrets.randbits(64)
    alphabet = string.ascii_letters + string.digits

    def gen(partition_index, iterator):
        rng = random.Random(partition_seed(base_seed, partition_index))
        for n in iterator:
            for _ in range(n):
                length = rng.randint(min_len, max_len)
                yield ("".join(rng.choices(alphabet, k=length)),)

    df = spark.createDataFrame(
        sc.parallelize(per_partition, partitions).mapPartitionsWithIndex(gen),
        schema="value string",
    )
    df.write.mode("overwrite").text(path)

    print(f"Saved {count} random strings (length {min_len}-{max_len}) to {path}")
    stop(spark)


def count_characters(path: str = STRINGS_PATH) -> None:
    spark = get_session("Count characters app")

    df = spark.read.text(path)
    result = df.agg(
        F.count("*").alias("strings"),
        F.sum(F.length("value")).alias("characters"),
        F.min(F.length("value")).alias("min_len"),
        F.max(F.length("value")).alias("max_len"),
    ).first()

    print(f"Read from {path}: {df.rdd.getNumPartitions()} partitions")
    print(f"Strings:    {result['strings']}")
    print(f"Characters: {result['characters']}")
    print(f"Length range found: [{result['min_len']}, {result['max_len']}]")

    stop(spark)


TASKS = {
    "example": example,
    "numbers": generate_numbers,
    "strings": create_random_strings,
    "count": count_characters,
}


def main():
    # bez argumentow - wszystkie zadania po kolei; np. `main.py strings count`
    selected = sys.argv[1:] or list(TASKS)
    for name in selected:
        print(f"\n===== {name} =====")
        TASKS[name]()


if __name__ == "__main__":
    main()
