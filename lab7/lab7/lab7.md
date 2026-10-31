# Laboratorium 7

## Wykorzystanie Flink

### Linki

* [Flink Docs](https://nightlies.apache.org/flink/flink-docs-stable/)
* [PyFLink](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/python/overview/)

## Zadanie 7.0 

Przetestuj Flinka lokalnie:

* Zainstaluj wersję JDK obsługiwaną przez wybraną wersję Flinka (sprawdź dokumentację zgodności, nie zakładaj automatycznie JDK 21)
* Utwórz środowisko wirtualne (`python -m venv .venv`), aktywuj je (`source .venv/bin/activate`) i zainstaluj zależności `pip install apache-flink (dobierz kompatybilne wersje Pythona, Javy i PyFlinka)`
* Uruchom przykładową aplikację Flinkową  `python sample.py`

## Zadanie 7.1

Przygotuj środowisko do uruchomienia aplikacji Flink z zastosowaniem Dockera/Docker-Compose'a (zobacz: `https://nightlies.apache.org/flink/flink-docs-stable/docs/deployment/resource-providers/standalone/docker/`). Pamiętaj o zweryfikowaniu pobranej dystrybucji Flinka.

## Zadanie 7.2

Stwórz przykładową aplikację Flink, która wygeneruje 10 000 000 losowych liczb double oraz zapisze je do pliku

## Zadanie 7.3

Stwórz aplikację Flink, która wygeneruje 1 000 000 losowych stringów o losowej długości z zadanego (konfigurowalnego przedziału), następnie zapisz je na dysku. Stwórz kolejną aplikację która wczyta zapisane dane oraz policzy liczbe znaków.

## Zadanie 7.4

Zapoznaj się ze Web-UI Flinka, dodaj odpowiednie mapowanie portów do docker-compose.yml tak by uzyskać do niego dostęp. 

## Zadanie 7.5

Stwórz kolejną aplikację która policzy liczbę słów w zadanym dodatkowym źródle danych. Znajdź dowolne źródło oraz przygotuj skrypt bash który je pobierze oraz umożliwi przetwarzanie za pomocą przygotowanej aplikacji.
