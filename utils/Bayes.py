from collections import Counter
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.naive_bayes import CategoricalNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score

# 创建数据库连接
con = create_engine('mysql+pymysql://root:123456@localhost:3306/boss')

# 从数据库中读取数据
df = pd.read_sql('select degree,categories,area,salary from jobs_info', con=con)

# 对薪资进行分箱处理h
binary = [0, 2000, 6000, 10000, 20000, np.inf]
df['salary'] = pd.cut(df['salary'], bins=binary, labels=False)

# 定义分类特征列
categorical_columns = ['degree', 'categories', 'area']

df[categorical_columns] = df[categorical_columns].astype('category')

# 使用OneHotEncoder对分类变量进行编码
enc = make_column_transformer(
    (OneHotEncoder(), categorical_columns)
)

# 拟合编码器并转换数据
X_train_encoded = enc.fit_transform(df[categorical_columns])
y_train = df['salary']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_train_encoded, y_train, test_size=0.2, random_state=42)

# 创建并训练模型
model = MultinomialNB()
model.fit(X_train.toarray(), y_train)

# 进行预测
y_pred = model.predict(X_test)


# 评估模型
def evaluate_model():
    Acy = accuracy_score(y_test, y_pred)
    print("Accuracy:", Acy)
    print(classification_report(y_test, y_pred, zero_division=1))

    # 输出测试集和预测集的薪资分布
    name = ['0-2000', '2000-6000', '6000-10000', '10000-20000', '20000以上']

    y_test_label = []
    y_pred_label = []
    test = []
    pred = []
    for i, bin_name in enumerate(name):
        y_test_in_bin = int((y_test == i).sum())
        y_pred_in_bin = int((y_pred == i).sum())
        y_test_label.append(y_test_in_bin)
        y_pred_label.append(y_pred_in_bin)
        test.append({'value': y_test_in_bin, 'name': bin_name})
        pred.append({'value': y_pred_in_bin, 'name': bin_name})

    # print("Test Data Distribution:")
    # print(y_test_label)
    # print("Predicted Data Distribution:")
    # print(y_pred_label)

    return y_test_label, y_pred_label, Acy, test, pred


def predict(data):
    X = pd.DataFrame([[data['degree'], data['categories'], data['area']]], columns=['degree', 'categories', 'area'])
    name = ['0-2000', '2000-6000', '6000-10000', '10000-20000', '20000以上']
    # 将单个数据点转换为DataFrame，以便与训练数据保持一致
    X_encoded = enc.transform(X)
    Y = model.predict(X_encoded.toarray())
    Y = int(str(Y)[1])
    return f"根据当前条件预测的薪资是：{name[Y]}"
