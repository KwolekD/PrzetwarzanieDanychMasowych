import os

from pyspark.sql import SparkSession


def get_session(app_name: str) -> SparkSession:
    spark_master_url = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")
    return (
        SparkSession.builder
        .appName(app_name)
        .master(spark_master_url)
        .getOrCreate()
    )


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

    spark.stop()


def generate_numbers() -> None:
    spark = get_session("Number generator app")

    spark.stop()


def create_random_strings() -> None:
    spark = get_session("Create random strings app")

    spark.stop()


def count_characters() -> None:
    spark = get_session("Number generator app")

    spark.stop()


def main():
    example()

    generate_numbers()

    create_random_strings()

    count_characters()


if __name__ == "__main__":
    main()

