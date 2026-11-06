from celery import group

from tasks import get_nth_word, random_number

numbers = group(random_number.s() for _ in range(10)).apply_async().get(timeout=30)
words = group(get_nth_word.s(n) for n in numbers).apply_async().get(timeout=120)

for n, word in zip(numbers, words):
    print(f"{n:>3}: {word if word else '(artykuł za krótki)'}")
