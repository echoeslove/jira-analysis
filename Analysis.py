from datetime import datetime

import numpy as np
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Bar, Line, Page


def get_week_list():
    start = pd.Timestamp('2022-03-28').week
    end = pd.Timestamp(datetime.now()).week
    return start, end


def get_delay_list():
    """获取延期任务

    Returns:
        _type_: 延期任务 通过pandas生成的df
    """
    delay_sheet = pd.read_excel(io='./技术分汇总0523.xlsx',
                                sheet_name='jira-delay', header=0)
    delay_sheet['预估提测时间'] = pd.to_datetime(delay_sheet['预估提测时间'])
    delay_sheet_local = delay_sheet.groupby(
        [np.int16(delay_sheet['预估提测时间'].dt.isocalendar().week),
         delay_sheet['难度级别']]
    )['任务号'].agg('size').unstack()
    delay_sheet_local_2 = delay_sheet.groupby(
        [np.int16(delay_sheet['预估提测时间'].dt.isocalendar().week)]
    )['任务号'].agg('size')
    return delay_sheet_local, delay_sheet_local_2


def get_bug_list():
    """获取bug数据
    现在来源于excel
    根据创建日期和严重程度进行分组

    Returns:
        _type_: bug任务 通过pandas生成的df
    """
    bug_sheet = pd.read_excel(io='./技术分汇总0523.xlsx',
                              sheet_name='bug', header=0)
    bug_sheet['创建日期'] = pd.to_datetime(bug_sheet['创建日期'])
    bug_sheet_local = bug_sheet.groupby(
        [np.int16(bug_sheet['创建日期'].dt.isocalendar().week),
         bug_sheet['严重程度']]
    )['Key'].agg('size').unstack()
    bug_sheet_local_2 = bug_sheet.groupby(
        [np.int16(bug_sheet['创建日期'].dt.isocalendar().week)]
    )['Key'].agg('size')
    return bug_sheet_local, bug_sheet_local_2


def fill(df):
    start, end = get_week_list()
    arr = list(df.index)
    for i in range(start, end):
        if(i not in arr):
            df.loc[i] = {}
    df.reset_index()
    df = df.reindex(index=list(range(start, end)))
    return df


def fill_2(df):
    start, end = get_week_list()
    arr = list(df.index)
    for i in range(start, end):
        if(i not in arr):
            df.loc[i] = '0'
    df = df.reindex(index=list(range(start, end)))
    return df


def render_delay():
    """渲染延期图表

    Returns:
        _type_: 延期图表
    """
    # 延期图表
    delay_df, delay_df_2 = get_delay_list()
    delay_df = fill(delay_df)
    delay_df_2 = fill_2(delay_df_2)
    # 延期柱状图 按难易程度分类
    x_data = list(delay_df.index)
    y_data_easy = list(delay_df['简单'])
    y_data_normal = list(delay_df['一般'])
    delay_bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis('简单', y_data_easy)
        .add_yaxis('一般', y_data_normal)
        .set_global_opts(title_opts=opts.TitleOpts(title="延期汇总"))
    )
    # 延期折线图 统计数量
    x_data = list(map(str, delay_df_2.index))
    y_data = list(map(int, delay_df_2.values))
    delay_line = (
        Line()
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
        .add_xaxis(x_data)
        .add_yaxis(
            series_name="Total",
            y_axis=y_data,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
    )
    delay_bar.overlap(delay_line)
    delay_bar.render('delay.html')
    return delay_bar


def render_bug():
    """渲染bug图表

    Returns:
        _type_: bug图表
    """
    # bug图表
    bug_df, bug_df_2 = get_bug_list()
    # bug柱状图 按照严重程度分组
    x_data = list(bug_df.index)
    y_data_critical = list(bug_df['Critical'])
    y_data_major = list(bug_df['Major'])
    y_data_minor = list(bug_df['Minor'])
    y_data_trivial = list(bug_df['Trivial'])
    bug_bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis('Critical', y_data_critical)
        .add_yaxis('Major', y_data_major)
        .add_yaxis('Minor', y_data_minor)
        .add_yaxis('Trivial', y_data_trivial)
        .set_global_opts(title_opts=opts.TitleOpts(title="Bug汇总"))
    )
    # bug折线图 统计数量
    x_data = list(map(str, bug_df_2.index))
    y_data = list(map(int, bug_df_2.values))
    bug_line = (
        Line()
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
        .add_xaxis(x_data)
        .add_yaxis(
            series_name="Total",
            y_axis=y_data,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
    )

    # 汇总到一个图中
    bug_bar.overlap(bug_line)
    bug_bar.render('bug.html')
    return bug_bar


def render():
    """生成bug走势图

    Args:
        bug_df (_type_): 通过pandas生成的df
    """
    page = Page()
    page.add(render_delay(), render_bug())
    page.render('summary.html')


render()
