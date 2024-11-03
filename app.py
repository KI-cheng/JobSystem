import datetime
import re

from flask import Flask, request, render_template, session, redirect, jsonify

from utils import query, utils, page_tool, Bayes

app = Flask(__name__)
app.secret_key = 'i love python'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('email'):
            return redirect('/home')
        return render_template('login.html')
    elif request.method == 'POST':
        request_form = dict(request.form)
        print(request_form)
        email = request_form['Email']
        password = request_form['Password']
        user = query.querys('select * from boss.user where email=%s and password=%s', [email, password], 'select')
        if len(user):
            session['email'] = email
            return redirect('/home')
        else:
            return render_template('login.html', state='error')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        request_form = dict(request.form)
        name = request_form['Name']
        email = request_form['Email']
        password = request_form['Password']
        password2 = request_form['Password2']
        if password != password2:
            return render_template('registration.html', state='pwd_error')
        users = query.querys('select * from user where email=%s', [email], 'select')
        if len(users):
            return render_template('registration.html', state='email_error')
        else:
            query.querys('insert into user(email,password,name) values(%s,%s,%s)', [email, password, name], 'no_select')
            return redirect('/login')


@app.route('/home', methods=['GET'])
def home():
    email = session.get('email')
    # 基础数据
    new_jobs, all_jobs, max_category, ratio, cp = utils.get_home_data()
    # 曲线图标
    trend_data = utils.get_trend_data()
    # 行业发展（右下角）
    # industry_data = utils.get_industry_data()
    # 学历要求
    degree_num, degree_salary = utils.get_degree_data()
    user = query.querys('select name from user where email = %s', [email], 'select')
    return render_template(
        'index.html',
        name=user[0][0],
        new_jobs=new_jobs,
        today=datetime.date.today(),
        all_jobs=all_jobs,
        max_category=max_category,
        ratio=ratio,
        cp=cp,
        trend_data=trend_data,
        # industry_data=industry_data,
        degree_num=degree_num,
        degree_salary=degree_salary,
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/')
def all():
    return redirect('/login')


@app.route('/accurate_table', methods=['GET'])
def accurate_table():
    if request.args.get('TOKEN', '') == '1':
        temp_list = {
            'degree': request.args.get('degree', ''),
            'categories': request.args.get('categories', ''),
            'area': request.args.get('area', ''),
            'source': request.args.get('source', '')
        }
        sql = "select * from jobs_info where 1=1"
        params = []
        for param in temp_list.keys():
            if temp_list[param] != '':
                sql += f' and {param} = %s'
                params.append(temp_list[param])

        type = request.args.get('type', '')
        context = request.args.get('context', '')
        if type != '' and context != '':
            sql += f' and {type} like %s'
            params.append('%' + context + '%')
        table_data = query.querys(sql, params, 'select')
    else:
        sql = "select * from jobs_info where 1=1"
        table_data = utils.get_table_data()
    pagination, table_data = page_tool.use_pagination(table_data)
    # 下拉框数据加载
    cities = utils.get_city()
    source = utils.get_source()
    return render_template('ac_table.html', table_data=table_data, pagination=pagination, cities=cities,
                           source=source)


@app.route('/map')
def map():
    map_data = utils.get_map_data()
    return render_template('map.html', map_data=map_data)


@app.route('/word_cloud')
def word_cloud():
    cloud_data = utils.get_cloud_data()
    return render_template('word_cloud.html', cloud_data=cloud_data)


@app.route('/realtime')
def realtime():
    return render_template('realtime.html')


@app.route('/get_realtime_data', methods=['POST'])
def get_realtime_data():
    return jsonify(data=utils.get_realtime_data())


@app.route('/trend')
def trend():
    trend_time, trend_salary, trend_position = utils.get_inclination()
    return render_template('trend.html', trend_time=trend_time, trend_salary=trend_salary,
                           trend_position=trend_position)


@app.route('/company_type')
def company_type():
    company = utils.get_company_data()
    return render_template('company_type.html', company=company)


@app.route('/bayes', methods=['GET'])
def bayes():
    y_test_label, y_pred_label, Acy, test, pred = Bayes.evaluate_model()
    cities = utils.get_city()
    print(y_test_label, y_pred_label)
    return render_template('bayes.html', cities=cities,
                           y_test_label=y_test_label, y_pred_label=y_pred_label, Acy=Acy, test=test, pred=pred)


@app.route('/predict', methods=['POST'])
def bayes_predict():
    data = dict(request.get_json())
    print(data)
    predict_data = Bayes.predict(data)
    return predict_data


@app.before_request
def before_request():
    pat = re.compile(r'^/static')
    if re.search(pat, request.path):
        return
    if request.path == "/login":
        return
    if request.path == '/register':
        return
    email = session.get('email')
    if email:
        return None

    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
