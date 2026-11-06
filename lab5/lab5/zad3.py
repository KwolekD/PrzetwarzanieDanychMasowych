from celery import group

from tasks import write_word

words = "Litwo ojczyzno moja ty jesteś jak zdrowie ile cię trzeba cenić ten tylko się dowie kto cię stracił".split()

group(write_word.s(word) for word in words).apply_async().get(timeout=30)

print(f"Zapisano {len(words)} słów do output/poem.txt")
