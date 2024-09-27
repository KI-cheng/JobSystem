from flask_paginate import get_page_parameter, Pagination
from flask import request


def use_pagination(table_data):
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # 每页显示的数据量
    per_page = 20
    # 分页处理
    pagination = Pagination(page=page, per_page=per_page, total=len(table_data))
    # 计算页码
    start = (page - 1) * per_page
    end = start + per_page
    table_data = table_data[start:end]

    return pagination, table_data
