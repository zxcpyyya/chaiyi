import pandas as pd

# 读取Excel文件
df = pd.read_excel('dishes/新疆菜.xlsx')

# 选择需要相加的三列
df['rating'] = df[['tastescore', 'service', 'environment']].sum(axis=1) / 3
df['rating'] = df['rating'].round(1)
df = df.drop(columns=['tastescore', 'service', 'environment'])
# 将结果保存到新的Excel文件
df.to_excel('dishes/新疆菜.xlsx', index=False)