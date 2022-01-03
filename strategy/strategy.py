# -*- coding: utf-8 -*-
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import data.stock as st


def compose_signal(data):
    """整合信号"""
    data['buy_signal'] = np.where(
        (data['buy_signal'] == 1) & (data['buy_signal'].shift(1) == 1),
        0, data['buy_signal'])
    data['sell_signal'] = np.where(
        (data['sell_signal'] == -1) & (data['sell_signal'].shift(1) == -1),
        0, data['sell_signal'])

    data['signal'] = data['buy_signal'] + data['sell_signal']

    return data


def calculate_prof_pct(data):
    """计算单次收益率： 开仓、平仓（开仓的全部股数）"""
    data = data[data['signal'] != 0]
    data['profit_pct'] = (data['close'] - data['close'].shift(1)) / data[
        'close'].shift(1)
    return data[data['signal'] == -1]


def calculate_cum_prof(data):
    """计算累计收益率"""
    data['cum_prof'] = pd.DataFrame(1 + data['profit_pct']).cumprod() - 1
    return data


def week_period_strategy(code, frequency, start_date, end_date):
    """周期选股（周四买，周一卖）"""
    data = st.get_single_price(code, frequency, start_date, end_date)
    data['weekday'] = data.index.weekday
    # 周四买入
    data['buy_signal'] = np.where((data['weekday'] == 3), 1, 0)
    # 周一卖出
    data['sell_signal'] = np.where((data['weekday'] == 0), -1, 0)

    data = compose_signal(data)
    data = calculate_prof_pct(data)
    data = calculate_cum_prof(data)

    return data


if __name__ == '__main__':
    df = week_period_strategy('000001.XSHE', 'daily', None,
                              datetime.date.today())
    print(df[['close', 'signal', 'profit_pct', 'cum_prof']])
    print(df.describe())
    df['cum_prof'].plot()
    plt.show()
