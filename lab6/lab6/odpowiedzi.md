# Laboratorium 6 – odpowiedzi

Uruchamianie:

```bash
docker compose up -d spark-master spark-worker          # klaster
docker compose logs -f                                  # logi (osobna konsola)
docker compose up spark-app                             # wszystkie zadania po kolei
docker compose run --rm spark-app python3 /app/main.py numbers         # tylko 6.2
docker compose run --rm spark-app python3 /app/main.py strings count   # tylko 6.3
```

## Zadanie 6.1

**Architektura** (Spark Standalone, tryb klient):

```
                    +-------------------------+
                    |  spark-master  :7077    |  <- menedzer klastra (Standalone)
                    |  Web UI        :8080    |     przydziela zasoby aplikacjom
                    +-----------+-------------+
                     rejestracja|  ^ zgloszenie aplikacji
            +-------------------+--+--------------+
            v                   v                 v
   +----------------+  +----------------+  +----------------+
   | spark-worker-1 |  | spark-worker-2 |  | spark-worker-3 |   1 rdzen, 2G RAM kazdy
   |   executor     |  |   executor     |  |   executor     |   -> uruchamiaja taski
   +-------^--------+  +-------^--------+  +-------^--------+
           |      taski / wyniki (bezposrednio z driverem)
           +-------------------+------------------+
                       +-------+--------+
                       |   spark-app    |  <- DRIVER (python3 main.py, SparkSession)
                       |   UI :4040     |     buduje DAG, dzieli na stage/taski
                       +----------------+
```

- `spark-master` – jeden master (`SPARK_MODE=master`), port 7077 dla klientow/workerow, 8080 – Web UI klastra.
- `spark-worker` – jedna usluga skalowana do 3 replik (`deploy.replicas: 3`), kazdy worker rejestruje się
  u mastera (`SPARK_MASTER_URL`) i oferuje 1 rdzen i 2 GB pamieci dla executorow → klaster ma 3 rdzenie.
- `spark-app` – kontener z driverem aplikacji. Driver laczy sie z masterem, master uruchamia executory na
  workerach, a nastepnie driver komunikuje sie z executorami bezposrednio (wysyla taski, odbiera wyniki).
- Wszystkie kontenery sa w jednej sieci compose, wiec rozwiązuja się po nazwach (`spark-master`).
- Dodany wolumen `./data:/data` na workerach i driverze – zapis/odczyt plikow (zad. 6.3) wykonuja executory
  na swoich lokalnych systemach plikow, wiec katalog musi byc wspolny (w produkcji: HDFS/S3).

**Obraz:** `bitnami/spark:latest` nie jest juz dostepny w Docker Hub (Bitnami w 2025 r. wycofal darmowe obrazy;
`failed to resolve reference "docker.io/bitnami/spark:latest": not found`). Uzyto archiwalnego repozytorium
z ustalonym tagiem: **`bitnamilegacy/spark:3.5.6`** – konkretna wersja zapewnia powtarzalnosc i zgodnosc
z `PYTHONPATH` (py4j `0.10.9.7` jest dostarczany ze Spark 3.5.x; `latest` wskazywalby Spark 4.x z inna wersja py4j).

**Wersja Sparka w logach:**

```
spark-master  | 26/11/12 00:49:14 INFO Master: Running Spark version 3.5.6
```

(aplikacja wypisuje tez `Spark version: 3.5.6` przez `spark.version`).

**Liczba workerow** – `docker compose ps` pokazuje 3 kontenery `lab6-spark-worker-{1,2,3}`
(Compose v2 respektuje `deploy.replicas`, `--scale` nie byl potrzebny).

## Zadanie 6.2

Implementacja: `generate_numbers()` w [main.py](main.py).

1. Na driverze tworzona jest lista 10 liczb `[1_000_000] * 10` – ile doubli ma wygenerowac kazda partycja.
2. `sc.parallelize(lista, 10)` rozprasza ja na 10 partycji (po jednym elemencie).
3. `mapPartitionsWithIndex(gen)` – funkcja dostaje `(indeks_partycji, iterator)`, tworzy wlasny generator
   i zamienia element `n` na `n` losowych doubli (generator leniwy – `yield`, bez trzymania listy w pamieci).

Wynik:

```
Elements / partition: [1000000, 1000000, ..., 1000000]
Stats: (count: 10000000, mean: 0.49992, stdev: 0.28873, max: 0.9999996, min: 1.24e-07)
All partitions start differently: True
```

(dla rozkladu U(0,1): srednia 0.5, odchylenie 1/√12 ≈ 0.2887 – zgodne).

**Inicjalizacja generatora:**

```python
base_seed = secrets.randbits(64)                 # raz, na driverze, z entropii systemu
seed = (base_seed << 32) | partition_index       # w kazdej partycji
rng = random.Random(seed)
```

- `base_seed` losowany kryptograficznie przy kazdym uruchomieniu → liczby sa za kazdym razem inne.
- Indeks partycji jest unikalny w obrebie RDD, a odwzorowanie `(base_seed, idx) → seed` jest roznowartosciowe
  (indeks zajmuje osobne, dolne 32 bity), wiec **dwie partycje nigdy nie dostana tego samego ziarna**.

**Dlaczego tak?**

- Funkcja mapujaca jest serializowana i wykonywana na executorach. Gdyby zainicjowac generator na driverze
  (lub uzyc stalego seeda), kazda partycja dostalaby **kopie tego samego stanu** generatora → identyczne
  ciagi liczb w kazdej partycji (10 × te same 1 000 000 liczb) – dane nie bylyby losowe ani niezalezne.
- Seed z czasu (`time.time()`) lub domyslny seed procesu tez jest zly – taski startujace w tej samej chwili
  albo w tym samym procesie Python workera (worker jest reuzywany) moga dostac to samo ziarno.
- Seed zalezny od indeksu partycji jest **deterministyczny dla danej partycji**: gdy task padnie i Spark
  go ponowi (lub przeliczy partycje z lineage po utracie cache), wygeneruje dokladnie te same liczby.
  Losowy seed w kazdym tasku psulby te gwarancje – ponownie przeliczona partycja mialaby inne dane
  (np. `count()` i `stats()` liczylyby rozne zbiory).

## Zadanie 6.3

Implementacja: `create_random_strings()` i `count_characters()` w [main.py](main.py) – dwie osobne
aplikacje Spark (osobne `SparkSession`, osobne wpisy w UI mastera).

- Konfiguracja przez zmienne srodowiskowe w `docker-compose.yml`: `STRINGS_COUNT=1000000`,
  `STRING_MIN_LEN=5`, `STRING_MAX_LEN=50`.
- Generowanie: ten sam schemat ziaren co w 6.2; dlugosc `randint(min, max)`, znaki z `[A-Za-z0-9]`.
- Zapis: `df.write.mode("overwrite").text("/data/random_strings")` → 10 plikow `part-0000X-*.txt` + `_SUCCESS`
  (jeden plik na partycje, kazdy zapisany przez executor, ktory ja policzyl).
- Odczyt i zliczanie: `spark.read.text(...)` + `sum(length(value))`.

Wynik:

```
Saved 1000000 random strings (length 5-50) to /data/random_strings
Read from /data/random_strings: 4 partitions
Strings:    1000000
Characters: 27512147
Length range found: [5, 50]
```

Oczekiwana liczba znakow ≈ 1 000 000 × (5+50)/2 = 27 500 000 – zgodne.
(Przy odczycie Spark sam dzieli pliki na partycje wg rozmiaru – stad 4, a nie 10.)

## Zadanie 6.4

Spark UI aplikacji wystawia driver na porcie **4040** (dodane `ports: 4040:4040` w `spark-app`).
Aplikacja konczy sie szybko, wiec UI znika razem z nia – aby je obejrzec, trzeba ja zatrzymac na chwile:

```bash
UI_WAIT_SECONDS=300 docker compose run --rm --service-ports spark-app python3 /app/main.py strings
```

i otworzyc <http://localhost:4040>. (UI mastera <http://localhost:8080> pokazuje tylko workery i liste
aplikacji – bez DAG.)

**Gdzie jest DAG:**

- **Jobs → kliknac job** (`text at ...`, job 0) → rozwinac **„DAG Visualization”** – DAG calego joba
  podzielony na stage (tu jeden: Stage 0), adres `http://localhost:4040/jobs/job/?id=0`.
- **Stages → kliknac stage** → „DAG Visualization” – DAG pojedynczego stage’a,
  `http://localhost:4040/stages/stage/?id=0&attempt=0`.
- **SQL / DataFrame → zapytanie** – plan fizyczny zapytania (WriteFiles, WholeStageCodegen).

DAG zapisu (zad. 6.3) w Stage 0:

```
parallelize            ParallelCollectionRDD [0]
  → mapPartitions      PythonRDD [1]            (funkcja gen w Pythonie)
  → map                MapPartitionsRDD [2..5]  (konwersja wierszy do DataFrame, WholeStageCodegen)
  → WriteFiles         MapPartitionsRDD [6]     (zapis plikow tekstowych)
```

Wszystko to jest jednym stage’em – brak operacji szerokich (shuffle), wiec kazda z 10 partycji jest liczona
i zapisywana przez jeden task niezaleznie. W aplikacji zliczajacej (`count`) DAG ma dwa stage – czesciowe
agregaty w kazdej partycji, potem shuffle (Exchange) i agregacja koncowa.
