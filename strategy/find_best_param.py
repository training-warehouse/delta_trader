# -*- coding: utf-8 -*-
import strategy.ma_strategy as ma
import data.stock as st
import pandas as pd

res = []

stock = '000001.XSHE'
data = st.get_csv_data('price', stock, '2016-01-01', '2022-01-01')
params = [5, 10, 20, 60, 120, 250]

for short in params:
    for long in params:
        if long > short:
            data_res = ma.ma_strategy(data, short, long)

            # 获取周期参数及其累计收益率
            cum_profit = data_res['cum_profit'].iloc[-1]
            res.append([short, long, cum_profit])

res = pd.DataFrame(res, columns=['short_window', 'long_window', 'cum_profit'])
res = res.sort_values(by='cum_profit', ascending=False)
print(res)
