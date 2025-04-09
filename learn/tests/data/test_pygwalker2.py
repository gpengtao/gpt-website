import pandas as pd
import pygwalker as pyg

# 读取 Excel 文件
df = pd.read_excel('/Users/pengtao.geng/Downloads/test_11111.xlsx')

# 绘图
pyg.walk(dataset=df, show_preview=False)
