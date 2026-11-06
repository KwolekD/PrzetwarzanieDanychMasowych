import random
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from celery_app import app

WIKI_URL = "https://pl.wikipedia.org/wiki/Special:Random"
HEADERS = {"User-Agent": "lab5-celery/1.0"}
POEM_PATH = Path("/data/poem.txt")
WORDS_PER_LINE = 5


@app.task
def random_number():
    return random.randint(0, 200)


def fetch_article_words():
    response = requests.get(WIKI_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.select("#mw-content-text p")
    text = " ".join(p.get_text() for p in paragraphs)
    return re.findall(r"[^\W\d_]+", text)


@app.task(
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    max_retries=3,
)
def get_nth_word(n):
    """Zwraca n-te słowo (numerowane od 1) losowego artykułu lub None, gdy artykuł jest za krótki."""
    if n < 1:
        raise ValueError("n musi być >= 1")

    words = fetch_article_words()
    if n > len(words):
        return None
    return words[n - 1]


@app.task
def write_word(word):
    if not word:
        return

    POEM_PATH.touch()
    word_count = len(POEM_PATH.read_text(encoding="utf-8").split())
    if word_count == 0:
        separator = ""
    elif word_count % WORDS_PER_LINE == 0:
        separator = "\n"
    else:
        separator = " "

    with POEM_PATH.open("a", encoding="utf-8") as f:
        f.write(separator + word)
    return word
