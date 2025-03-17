# Create your tests here.

# 时速配速转化
for speed in range(60, 201):
    speed = speed / 10
    total_time = 60.0 / speed
    minutes = int(total_time)
    remaining = total_time - minutes
    seconds = round(remaining * 60)

    # 格式化输出，确保秒数为两位数
    print(f"{speed} km/h = {minutes}:{seconds:02d} min/km")
