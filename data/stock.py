# -*- coding: utf-8 -*-
import os

import jqdatasdk
import pandas as pd

from .config import JQDATA_AUTH

jqdatasdk.auth(*JQDATA_AUTH)

pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

file_root = os.path.dirname(__file__)


def get_stocks():
    """
     获取所有A股股票列表
    :return:
    """
    return list(jqdatasdk.get_all_securities(['stock']).index)


def get_single_price(code, frequency, start_date, end_date):
    """
    获取单个股票行情数据
    :param code:
    :param frequency:
    :param start_date:
    :param end_date:
    :return:
    """
    return jqdatasdk.get_price(code, start_date=start_date, end_date=end_date,
                               frequency=frequency)


def export_data(data, data_type, filename):
    """
    导出数据
    :param data:
    :param data_type:
    :param filename:
    :return:
    """
    file_path = f'{file_root}/{data_type}/{filename}.csv'
    data.index.names = ['date']
    data.to_csv(file_path)
    print(f'已成功存储到： {file_path}')


def get_csv_data(data_type, filename):
    file_path = f'{file_root}/{data_type}/{filename}.csv'
    return pd.read_csv(file_path)


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
