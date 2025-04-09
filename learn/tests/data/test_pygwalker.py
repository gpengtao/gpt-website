import pandas as pd
import pygwalker as pyg

# 读取 Excel 文件
df = pd.read_excel('/Users/pengtao.geng/Downloads/test_11111.xlsx')
df.head(10)

walk = pyg.walk(df)

print("1111111111111")
print(walk)
print("2222222222222")

