# -*- coding: utf-8 -*-
import os
import datetime

import jqdatasdk
import pandas as pd

from data.config import JQDATA_AUTH

jqdatasdk.auth(*JQDATA_AUTH)

pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

file_root = os.path.dirname(__file__)


def init_db():
    stocks = get_stocks()
    for stock in stocks:
        data = get_single_price(code=stock, frequency='daily')
        export_data(data, 'price', stock)


def get_stocks():
    """
     获取所有A股股票列表
    :return:
    """
    return list(jqdatasdk.get_all_securities(['stock']).index)


def get_index_list(index_symbol='000300.XSHG'):
    """
    获取指数成分股
    指数代码查询 www。joinquant.com/indexData
    """
    return jqdatasdk.get_index_stocks(index_symbol)


def get_single_price(code, frequency, start_date=None, end_date=None):
    """
    获取单个股票行情数据
    :param code:
    :param frequency:
    :param start_date:
    :param end_date:
    :return:
    """
    # 如果 start_date=None, 默认为从上市日期开始
    if start_date is None:
        start_date = jqdatasdk.get_security_info(code).start_date

    if end_date is None:
        end_date = datetime.datetime.today()

    return jqdatasdk.get_price(code, start_date=start_date, end_date=end_date,
                               frequency=frequency, panel=False)


def export_data(data, data_type, filename, mode='w'):
    """
    导出数据
    :param data:
    :param data_type:
    :param filename:
    :return:
    """
    file_path = f'{file_root}/{data_type}/{filename}.csv'
    data.index.names = ['date']
    if mode == 'a':
        data.to_csv(file_path, mode=mode, header=False)
        data = pd.read_csv(file_path)
        data = data.drop_duplicates('date')  # 针对日期去重，保留最后一个参数
        data.to_csv(file_path, index=False)
    else:
        data.to_csv(file_path)
    print(f'已成功存储到： {file_path}')


def get_csv_data(data_type, code, start_date, end_date, columns=None):
    """获取本地数据"""
    update_daily_price(code, data_type)
    file_path = f'{file_root}/{data_type}/{code}.csv'

    if columns is None:
        data = pd.read_csv(file_path, index_col='date')
    else:
        data = pd.read_csv(file_path, index_col='date', usecols=columns)

    return data[(data.index >= start_date) & (data.index <= end_date)]


def transfer_price_freq(data, time_freq):
    """
    将数据转化为指定周期
    :param data:
    :param time_freq:
    :return:
    """
    df = pd.DataFrame()
    df['open'] = data['open'].resample(time_freq).first()
    df['close'] = data['close'].resample(time_freq).last()
    df['high'] = data['high'].resample(time_freq).max()
    df['low'] = data['low'].resample(time_freq).min()

    return df


def get_single_finance(code, date, stat_date):
    """获取单个股票财务数据"""
    return jqdatasdk.get_fundamentals(
        jqdatasdk.query(jqdatasdk.indicator).filter(
            jqdatasdk.indicator.code == code),
        date=date, statDate=stat_date)


def get_single_valuation(code, date, stat_date):
    """获取单个股票估值数据"""
    return jqdatasdk.get_fundamentals(
        jqdatasdk.query(jqdatasdk.valuation).filter(
            jqdatasdk.valuation.code == code),
        date=date, statDate=stat_date)


def calculate_change_pct(data):
    """计算涨跌幅，（当前收盘价-前期收盘价）/前期收盘价"""
    data['close_pct'] = (data['close'] - data['close'].shift(1)) / data[
        'close'].shift(1)
    return data


def update_daily_price(stock_code, data_type):
    file_path = f'{file_root}/{data_type}/{stock_code}.csv'
    if os.path.exists(file_path):
        start_date = pd.read_csv(file_path, usecols=['date'])['date'].iloc[-1]
        data = get_single_price(stock_code, 'daily', start_date,
                                datetime.datetime.today())
        export_data(data, data_type, stock_code, 'a')
    else:
        data = get_single_price(stock_code, 'daily')
        export_data(data, data_type, stock_code)


if __name__ == '__main__':
    print(get_index_list())
