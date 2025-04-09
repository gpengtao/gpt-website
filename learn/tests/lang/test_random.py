import random
from datetime import datetime

"""
测试random.choice
"""
count = {"aaa": 0, "bbb": 0}
for i in range(100000):
    choice = random.choice(["aaa", "bbb"])
    count[choice] += 1

print(count)