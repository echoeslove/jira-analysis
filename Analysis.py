from datetime import datetime

import numpy as np
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Bar, Line, Pie, Page


excel_dir = './技术分汇总0627.xlsx'
excel_name = '技术分汇总0627.xlsx'


def get_week_list():
    """获取2022/3/28到当前时间的周序号

    Returns:
        _type_: 开始的周序号，当前周序号
    """
    start = pd.Timestamp('2022-03-28').week
    end = pd.Timestamp(datetime.now()).week + 1
    return start, end


def get_excel_groupby_result(excel_dir, sheet_name, base_groupby_col,
                             groupby_col, target_col,
                             base_groupby_col_time=True):
    sheet = pd.read_excel(io=excel_dir,
                          sheet_name=sheet_name, header=0)
    # 日期类型处理
    if(base_groupby_col_time):
        sheet[base_groupby_col] = pd.to_datetime(sheet[base_groupby_col])
        if(groupby_col):
            sheet_local = sheet.groupby(
                [np.int16(sheet[base_groupby_col].dt.isocalendar().week),
                 sheet[groupby_col]]
            )[target_col].agg('size').unstack()
        else:
            sheet_local = sheet.groupby(
                [np.int16(sheet[base_groupby_col].dt.isocalendar().week)]
            )[target_col].agg('size')
    else:
        sheet_local = sheet.groupby(
            [sheet[base_groupby_col]]
        )[target_col].agg('size')
    return sheet_local


def get_delay_list():
    """获取延期任务

    Returns:
        _type_: 延期任务 通过pandas生成的df
    """
    delay_sheet = pd.read_excel(io=excel_dir,
                                sheet_name='jira-delay', header=0)
    delay_sheet['预估提测时间'] = pd.to_datetime(delay_sheet['预估提测时间'])
    # 根据预计提测时间和难度级别分类
    delay_sheet_local = delay_sheet.groupby(
        [np.int16(delay_sheet['预估提测时间'].dt.isocalendar().week),
         delay_sheet['难度级别']]
    )['任务号'].agg('size').unstack()
    # 根据预计提测时间分类
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
    bug_sheet = pd.read_excel(io=excel_dir,
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
    y_data_hard_low = list(delay_df['较难'])
    delay_bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis('较难', y_data_hard_low)
        .add_yaxis('一般', y_data_normal)
        .add_yaxis('简单', y_data_easy)
        .set_global_opts(title_opts=opts.TitleOpts(title="延期汇总")))
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


def render_delay_pie():
    delay_df_3 = get_excel_groupby_result(excel_dir=excel_dir,
                                          sheet_name='jira-delay',
                                          base_groupby_col='延期原因分类',
                                          groupby_col=None,
                                          target_col='任务号',
                                          base_groupby_col_time=False)
    delay_pie = (
        Pie()
        .add("",
             [list(z) for z in zip(list(delay_df_3.index), list(delay_df_3))],
             center=["40%", "50%"])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="延期原因分析"),
            legend_opts=opts.LegendOpts(pos_right="2%", orient="vertical"))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return delay_pie


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


def render_bug_per_pers(person_group):
    bug_sheet = pd.read_excel(io=excel_dir,
                              sheet_name='bug', header=0)
    bug_sheet['创建日期'] = pd.to_datetime(bug_sheet['创建日期'])
    bug_sheet_local = bug_sheet.groupby(
        [np.int16(bug_sheet['创建日期'].dt.isocalendar().week),
         bug_sheet['经办人']]
    )['Key'].count()
    bug_per_person = bug_sheet_local.unstack()
    x_data = list(map(str, bug_per_person.index))
    bug_top5_line = (
        Line()
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Bug趋势-"+person_group),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            legend_opts=opts.LegendOpts(pos_right="0", orient="vertical"),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(x_data)
    )
    person_sheet = pd.read_excel(io=excel_dir,
                                 sheet_name='team-member', header=0)
    persons = []
    for idx, row in person_sheet.iterrows():
        if (row['分组'] == person_group):
            persons.append(row['名称'])
    for col in bug_per_person.columns:
        for p in persons:
            if(p in col):
                y_data = list(bug_per_person[col])
                y_data = np.nan_to_num(y_data, nan=0)
                bug_top5_line.add_yaxis(
                    series_name=col,
                    y_axis=y_data,
                    symbol="emptyCircle",
                    is_symbol_show=True,
                    label_opts=opts.LabelOpts(is_show=True),)
    bug_top5_line.render("bug_top5.html")
    return bug_top5_line


def render():
    """生成bug走势图

    Args:
        bug_df (_type_): 通过pandas生成的df
    """
    page = Page()
    page.add(render_delay(),
             render_delay_pie(),
             render_bug(),
             render_bug_per_pers('平台'),
             render_bug_per_pers('数据'),
             render_bug_per_pers('营销中台'),
             render_bug_per_pers('运营'))
    page.render('summary.html')


def calculate_bug_score():
    bug_sheet = pd.read_excel(io=excel_dir,
                              sheet_name='bug', header=0)
    bug_sheet['创建日期'] = pd.to_datetime(bug_sheet['创建日期'])
    bug_sheet_local = bug_sheet.groupby(
        [np.int16(bug_sheet['创建日期'].dt.month),
         bug_sheet['严重程度'], bug_sheet['经办人']]
    )['Key'].agg('size').unstack()
    print(bug_sheet_local)
    members = []
    score = []
    for col in bug_sheet_local.columns:
        # print(col)
        bug_sheet_per_category = bug_sheet_local[col].unstack()
        # print(bug_sheet_local[col])
        score_list = np.nan_to_num(
            bug_sheet_per_category['Blocker'], nan=0)*8 +\
            np.nan_to_num(bug_sheet_per_category['Critical'], nan=0)*5 +\
            np.nan_to_num(bug_sheet_per_category['Major'], nan=0)*3 +\
            np.nan_to_num(bug_sheet_per_category['Minor'], nan=0)*1 +\
            np.nan_to_num(bug_sheet_per_category['Trivial'], nan=0) * 0.5
        member_score = []
        score_total = 0
        for i in score_list:
            s = 100 - i
            score_total += s
            member_score.append(s)
        score_total = score_total / len(score_list)
        print(bug_sheet_local[col].name + "\t" +
              str(score_total) + "\t" + str(member_score))
        members.append(bug_sheet_local[col].name)
        score.append(score_total)


render()
calculate_bug_score()
