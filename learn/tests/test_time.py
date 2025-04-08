import time
from datetime import timedelta

timestamp = time.time()
print(timestamp)
print(int(timestamp))

print(timedelta(days=1/24).total_seconds())