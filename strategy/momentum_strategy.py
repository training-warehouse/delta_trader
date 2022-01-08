# -*- coding: utf-8 -*-
import data.stock as st
import strategy.base as stb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot


def get_data(index_symbol, start_date, end_date, columns):
    """获取股票收盘价数据，并拼接"""
    stocks = st.get_index_list(index_symbol)
    data_concat = pd.DataFrame()
    for code in stocks[:10]:
        data = st.get_csv_data('price', code, start_date, end_date, columns)
        data.columns = [code]
        # 拼接多个股票的收盘价
        data_concat = pd.concat([data_concat, data], axis=1)

    # print(data_concat.tail())
    return data_concat


def get_top_stocks(data, top_n):
    signals = pd.DataFrame(index=data.index, columns=data.columns)
    for index, row in data.iterrows():
        # 找出每行最大值，并转成0 1 信号
        signals.loc[index] = row.isin(row.nlargest(top_n)).astype(np.int8)
    return signals


def momentum(data_concat, shift_n=1, top_n=2):
    """动量选股策略"""
    data_concat.index = pd.to_datetime(data_concat.index)
    data_month = data_concat.resample('M').last()

    # 计算动量因子
    # 对数收益率 log（期末值/期初值）
    # 计算过去N个月的收益率 = 期末值/期初值 -1 = （期末-期初）/期初
    shift_return = (data_month / data_month.shift(shift_n)) - 1
    # print(shift_return.head())

    # 生成交易信号： 收益率拍前n的>赢家组合>买入1，排最后n个>输家>卖出-1
    buy_signals = get_top_stocks(shift_return, top_n)
    cell_signals = get_top_stocks(-1 * shift_return, top_n)
    signals = buy_signals - cell_signals
    print(signals)

    # 计算投资组合收益率
    return stb.calculate_portfolio_return(shift_return, signals, top_n * 2)


if __name__ == '__main__':
    data_concat = get_data('000300.XSHG', '2016-01-01', '2022-01-01',
                           ['date', 'close'])

    returns = momentum(data_concat)
    returns.plot()
    plot.show()
