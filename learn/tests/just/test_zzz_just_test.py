import random
from datetime import datetime

# 文件名，格式：年月日时分秒_微秒_2位随机数
username = "pengtao.geng"
username = username.replace(".", "")
timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
random_suffix = str(random.randint(10, 99))
filename = f"file_{username}_{timestamp}_{random_suffix}.xlsx"
print(filename)
