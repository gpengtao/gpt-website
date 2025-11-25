import json
import time

now = time.time()
print(now)
print(int(now))
print(hex(int(now)))

result = hex(int(now))[2:]
print(result)

values = json.dumps(None, ensure_ascii=False)
print(values)
