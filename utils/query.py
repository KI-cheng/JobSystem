from pymysql import *


def querys(sql, params, type='no_select'):
    conn = connect(host='localhost', port=3306, user='root', password='123456', database='boss', charset='utf8')
    cursor = conn.cursor()
    params = tuple(params)
    cursor.execute(sql, params)
    if type != 'no_select':
        data_list = cursor.fetchall()
        if conn:
            cursor.close()
            conn.close()
        return data_list
    else:
        conn.commit()
        if conn:
            cursor.close()
            conn.close()
        return "success"
