import pandas as pd
from sqlalchemy import create_engine

con = create_engine('mysql+pymysql://root:123456@localhost:3306/boss')

df = pd.read_sql('select degree,categories,area,salary from jobs_info', con=con)


def calc_bayes(data):
    X = {
        'degree': data[0],
        'categories': data[1],
        'area': data[2]
    }

    y_num_set = df['salary'].value_counts(normalize=True).to_dict()  # 获取重复数据的相对频率
    p_dic = []

    for key in y_num_set.keys():  # 针对每个类别的频率都要计算其特征分量的乘积
        Py = y_num_set[key]
        for x_key in X.keys():
            value = X[x_key]
            p = df[x_key].value_counts(normalize=True)[value]
            Py *= p
        p_dic.append({
            'Y': key,
            'P': Py,
        })
    print(p_dic)
    return p_dic


def confirm_the_result(p_dic):
    max_key = max(p_dic, key=lambda x: x['P'])
    print(f"预测最可能的薪资是{max_key}")


if __name__ == '__main__':
    X = ['博士及以上', '计算机/网络/技术类', '北京']  # 一个简单的测试样例
    p_dic = calc_bayes(data=X)
    confirm_the_result(p_dic=p_dic)
