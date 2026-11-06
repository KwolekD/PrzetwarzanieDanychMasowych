from celery import chain, group

from tasks import get_nth_word, random_number, write_word

PIPELINES = 30

pipeline = chain(random_number.s(), get_nth_word.s(), write_word.s())
words = group(pipeline.clone() for _ in range(PIPELINES)).apply_async().get(timeout=300)

written = [word for word in words if word]
print(f"Zapisano {len(written)} z {PIPELINES} słów (reszta: za krótkie artykuły)")
print(" ".join(written))
