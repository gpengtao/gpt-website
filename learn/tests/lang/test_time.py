import time
from datetime import timedelta, datetime

timestamp = time.time()
print(f"11111: {timestamp}")
print(f"22222: {int(timestamp * 1000)}")
print(f"33333: {int(timestamp)}")
print(f"44444: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

print(f"55555: {timedelta(days=1 / 24).total_seconds()}")
print(f"66666: {datetime.now()}")
print(f"77777: {(datetime.now() - timedelta(days=1)).strftime('%Y%m%d')}")
