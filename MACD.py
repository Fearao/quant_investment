import talib
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
# plt.rcParams["font.family"] = "SimHei"
sns.set(font="SimHei")

# 显示所有的行
pd.set_option('display.max_rows', None)

df = pd.read_excel('stock_data.xlsx',  # 读取数据
                   sheet_name='上证指数',
                   # encoding='gbk',
                   skiprows=[0, 1, 2, 733, 734],
                   parse_dates=['date'],
                   index_col=0)  #这里index_col只能用0不能用['date]

close_price_ndarr = df.loc[:, 'close'].to_numpy()  # 将收盘价一列转为ndarray

diff, dea, macd = talib.MACD(close_price_ndarr, #用talib的库计算MACD值，返回diff, dea, macd
                                fastperiod=12,
                                slowperiod=26,
                                signalperiod=9)

df = pd.DataFrame({'diff': diff,
                   'dea': dea,
                   'my_macd': macd,
                   'close': df['close']},
                   index=df.index)

# 去除空缺值行
df = df.fillna(method='ffill')
df = df.dropna(how='any')

# 取diff值的前一天滑动
df['diff_1'] = df['diff'].shift()
df = df.dropna(how='any')

# 取dea值的前一天滑动
df['dea_1'] = df['dea'].shift()
df = df.dropna(how='any')

# 重新对列进行排序
df = df[['close', 'diff', 'diff_1', 'dea', 'dea_1']]

# 0值列来记录买卖金额
df['买卖金额'] = 0

# 遍历每一行
for index, row in df.iterrows():
    # 如果前一天的diff_1<dea_1,今天的diff>dea，则买入
    if (row['diff_1'] < row['dea_1']) & (row['diff'] > row['dea']):
        df.loc[index, '买卖金额'] = 1000
    # 如果前一天的diff_1>dea_1,今天的diff<dea，则买入
    elif (row['diff_1'] > row['dea_1']) & (row['diff'] < row['dea']):
        if (df['买卖金额'][:index].sum() >= 1000):
            df.loc[index, '买卖金额'] = -1000

# 手续费比率为0.2%
c_rate = 0.002

df['累计买卖净额'] = df['买卖金额'].cumsum()

# 每次买入的单位数量，扣除了手续费（此处手续费计算有近似）
df['每次买入数量'] = (df['买卖金额'] / df['close']) * (1 - c_rate)

# 累计买入数量净额，扣除了手续费（此处手续费计算有近似）
df['累计买入数量净额'] = df['每次买入数量'].cumsum()

# 平均成本
df['平均成本'] = df['累计买卖净额'] / df['累计买入数量净额']

df['市值'] = df['累计买入数量净额'] * df['close']

df['收益率'] = (df['close'] / df['平均成本'] - 1)

plot_list = ['close', 'diff', 'diff_1', 'dea', '买卖金额']

sns.lineplot(data=df[['收益率']])
plt.show()

# plt.savefig('卖出.png')

# df = df[plot_list]
# df.sort_values(by='买卖金额', axis=0, ascending=True, inplace=True)
# print(df)









