from celery import group

from tasks import random_number

results = group(random_number.s() for _ in range(100)).apply_async()
numbers = results.get(timeout=30)

print(f"Wygenerowano {len(numbers)} liczb:")
print(numbers)
