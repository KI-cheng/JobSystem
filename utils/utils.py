import json
import math
from collections import Counter
import numpy
import random
import pandas as pd
import datetime
from sqlalchemy import create_engine

con = create_engine('mysql+pymysql://root:123456@localhost:3306/boss')

df = pd.read_sql('select * from jobs_info', con=con)


def type_list(type):
    type = list(df[type].values)
    # 去掉空值
    for i in range(len(type) - 1, -1, -1):
        if type[i] == '':
            type.pop(i)
    type = list(map(lambda x: x.split(' '), type))
    the_list = []
    for i in type:
        for j in i:
            the_list.append(j)
    return the_list


def get_home_data():  # 四个标签内的数据
    today = str(datetime.date.today())
    condition = df['publish_date'].str.contains(today)
    # 今日新增职位
    new_jobs = len(df[condition].values)
    # 总职位
    all_jobs = len(df.values)

    # 占比最高行业
    total = df.groupby('categories').size().sum()
    max = df.groupby('categories').size().max()
    idx = df.groupby('categories').size().idxmax()
    max_category = idx
    ratio = str(int(max / total * 100)) + '%'

    # 招聘企业总数
    cp = len(set(df['company_name'].values))

    return new_jobs, all_jobs, max_category, ratio, cp


def get_trend_data():  # 职位薪资增长趋势模型
    trend_data = []
    today = str(datetime.date.today())
    time_list = list(pd.date_range(end=today, periods=30))
    time_list = list(map(str, time_list))
    for time in time_list:
        time = time.split(' ')[0]
        condition = df['publish_date'].str.contains(time)
        position = len(df[condition].values)
        # 跳过缺失值，只对纯数值行列计算
        pd.set_option('display.precision', 2)
        salary = df[condition]['salary'].mean(skipna=True, numeric_only=True)
        salary = numpy.nan_to_num(salary)
        dic = {
            'period': time,
            'positions': position,
            'salary': int(salary),
        }
        if position != 0:
            trend_data.append(dic)
    # print(trend_data)
    return trend_data


def get_industry_data():
    now = datetime.date.today()
    the_month = f'{now.year}-{now.month:02d}'
    last_month = ''
    if now.month != 1:
        last_month = f'{now.year}-{now.month - 1:02d}'
    else:
        last_month = f'{now.year - 1}-12'
    # 先写好时间条件
    condition_now = df['publish_date'].str.contains(the_month)
    condition_last = df['publish_date'].str.contains(last_month)
    industry_data = ''
    # 计算每个组的大小，并按降序排序
    now_group = df[condition_now].groupby('categories').size().sort_values(ascending=False)
    now = df[condition_now].groupby('categories')
    last = df[condition_last].groupby('categories')
    for i in range(0, 8):
        # 找到索引名称
        index = now_group.index[i]
        # 获取这个月的数据个数
        now_group_len = len(now.get_group(index))
        # 获取上个月的数据个数
        last_group_len = len(last.get_group(index))

        if now_group_len > last_group_len:  # 增加了
            present = f'<th scope="row">{i + 1}</th><td>{index}</td><td><span class="label label-success">{now_group_len}' \
                      f'</span></td><td><h5>{str(int((now_group_len - last_group_len) / last_group_len * 100))}%' \
                      f'<i class="fa fa-level-up"></i></h5></td>'
        elif last_group_len > now_group_len:  # 减少了
            present = f'<th scope="row">{i + 1}</th><td>{index}</td><td><span class="label label-danger">{now_group_len}' \
                      f'</span></td><td><h5 class="down">{str(int((1 - now_group_len / last_group_len) * 100))}%' \
                      f'<i class="fa fa-level-down"></i></h5></td>'
        else:  # 保持不变
            present = f'<th scope="row">{i + 1}</th><td>{index}</td><td><span class="label label-info">{now_group_len}' \
                      f'</span></td><td><h5>---<i></i></h5></td>'
        industry_data += f'<tr>{present}</tr>'
    # print(industry_data)
    return industry_data


def get_degree_data():
    # 先进行分组
    ag = df.groupby('degree')
    degree_num = []
    degree_salary = []
    for i in range(0, 5):
        index = ag.size().index[i]
        index_group = ag.get_group(index)
        num = len(index_group)
        dic = {
            'value': num,
            'name': index
        }
        degree_num.append(dic)
        salary = index_group['salary'].mean()
        dic2 = {
            'value': round(numpy.nan_to_num(salary), 2),
            'name': index
        }
        degree_salary.append(dic2)
    return degree_num, degree_salary


def get_table_data():
    return df.values


def get_city():
    d = df.groupby('area').size().sort_values(ascending=False)
    city_list = []
    for i in range(0, 35):
        city_list.append(d.index[i])
    return city_list


def get_source():
    d = df.groupby('source').size().sort_values(ascending=False)
    source_list = []
    for i in range(0, len(d)):
        source_list.append(d.index[i])
    return source_list


def get_company_scale():
    d = df.groupby('company_scale').size().sort_values(ascending=False)
    scale_list = []
    for i in range(0, len(d)):
        scale_list.append(d.index[i])
    return scale_list


def get_company_property():
    d = df.groupby('company_property').size().sort_values(ascending=False)
    property_list = []
    for i in range(0, len(d)):
        property_list.append(d.index[i])
    return property_list


def get_map_data():
    area = df.groupby('area')
    areas = area.size()
    map_data = []
    for i in range(0, len(areas)):
        name = areas.index[i]
        num = len(area.get_group(name))
        if name in ['香港', '澳门']:
            name += '特别行政区'
        elif name == '内蒙古':
            name += '自治区'
        elif name == '新疆':
            name += '维吾尔自治区'
        elif name == '广西':
            name += '壮族自治区'
        elif name == '西藏':
            name += '自治区'
        elif name == '宁夏':
            name += '回族自治区'
        elif name in ['北京', '天津', '上海', '重庆']:
            name += '市'
        else:
            name += '省'
        map_data.append({'name': name, 'value': num})
    return map_data


def get_cloud_data():
    welfare = type_list('welfare')
    count = Counter(welfare)  # 统计list的出现次数并生成词典
    cloud_data = []
    for key in count.keys():
        cloud_data.append({
            'name': key,
            'value': count[key]
        })
    return cloud_data


def get_realtime_data():
    today = str(datetime.date.today())
    condition = df['publish_date'].str.contains(today)
    result = df[condition].sample(n=10).values
    realtime_list = []
    for job in result:
        if len(job[1]) > 10:
            continue
        item = {
            'img': '../static/images/' + random.choice(
                ['a.png', 'b.png', 'c.png', 'd.png', 'e.png', 'f.png', 'g.png', ]),
            # 'img': '../static/images/tmall.ico',
            'info': f'获取到职位： {job[1]}',
            'size': 15,
            'href': f'/accurate_table?TOKEN=1&type=job_name&context={job[1]}',
            'close': False,
            'speed': random.randint(12, 20),
            'bottom': random.randint(100, 800),
            'old_ie_color': '#000000',
            'color': 'rgb(255,255,255)',
        }
        realtime_list.append(item)
    return realtime_list


def get_inclination():
    today = str(datetime.date.today())
    time_list = list(pd.date_range(end=today, periods=7))
    time_list = list(map(str, time_list))
    trend_time = []
    trend_salary = []
    trend_position = []
    for time in time_list:
        time = time.split(' ')[0]
        trend_time.append(time)
        d = df[df['publish_date'].str.contains(time)]
        trend_position.append(len(d.values))
        # 跳过缺失值，只对纯数值行列计算
        pd.set_option('display.precision', 2)
        salary = d['salary'].mean(skipna=True, numeric_only=True)
        salary = numpy.nan_to_num(salary)
        trend_salary.append(int(salary))
    return trend_time, trend_salary, trend_position


def get_company_data():
    all_data = [
        ['product', '1-49人', '50-99人', '100-499人', '500-999人', '1000人以上', '1000-4999人', '5000以上']
    ]
    for p in ['上市公司', '合资企业', '国有企业', '外商独资/外企代表处', '民营企业', '港澳台公司', '股份制企业',
              '其他']:
        t = [p]
        for s in ['1-49人', '50-99人', '100-499人', '500-999人', '1000人以上', '1000-4999人', '5000以上']:
            result = df.query('company_property==@p& company_scale==@s')
            pd.set_option('display.precision', 2)
            salary = result['salary'].mean(skipna=True, numeric_only=True)
            if math.isnan(salary):
                salary = 0
            else:
                salary = round(numpy.nan_to_num(salary), 2)
            t.append(salary)
        all_data.append(t)
    return all_data
