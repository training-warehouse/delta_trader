# -*- coding: utf-8 -*-
import matplotlib.pyplot as plot
from scipy import stats

import data.stock as st
import strategy.ma_strategy as ma


def ttest(data_return):
    """
    对策略说明进行t检验
    :param strat_return: 单次收益率
    :return:
    """
    t, p = stats.ttest_1samp(data_return, 0, nan_policy='omit')

    # 判断是否与理论均值有显著性差异 α=0.05
    p_value = p / 2
    print('是否拒绝H0： 收益均值 = 0: ', p_value < 0.05)
    print('t-value', t)
    print('p-value', p_value)
    return t, p_value


if __name__ == '__main__':
    stocks = '000001.XSHE'

    # 循环获取数据
    df = st.get_single_price(stocks, 'daily', '2016-01-01', '2021-01-01')
    df = ma.ma_strategy(df)  # 调用双均线策略

    returns = df['profit_pct']

    # plot.hist(returns, bins=30)
    # plot.show()
    ttest(returns)
