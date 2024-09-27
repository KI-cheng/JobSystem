from time import sleep
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import seleniumwire.undetected_chromedriver as uc
from lxml import html
import json
import pymysql
import datetime, time

etree = html.etree


# 得到每一页的json数据，并存储到json文件里,返回json文件目录
def get_Page_Data(url):
    # ------------ 规避检测 ------------
    # 实例化对象
    option = uc.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 开启实验性功能
    # 去除特征值
    option.add_argument("--disable-blink-features=AutomationControlled")
    # 隐藏一下子
    option.add_argument('--headless')
    # 实例化谷歌
    driver = webdriver.Chrome(options=option)
    # 获取页面源码
    driver.get(url)
    try:
        flag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'pre')))
    except:
        return 'error'
    page_text = driver.page_source
    # 解析
    html = etree.HTML(page_text)
    data = html.xpath('//pre/text()')[0]
    return data


# 处理json数据，返回一个json文件里的所有工作信息（二维列表）
def processing_data(data, category):
    json_data = json.loads(data, strict=False)
    jobs = json_data["data"]["list"]
    # 所有职位信息的列表
    # num = 0
    for each in jobs:
        # 存放每一个职位的信息
        job = []
        # jobInfo信息
        # 职位id
        job_id = each["jobId"]

        # 职位名称
        job_name = each["jobName"]

        # 薪资
        lowMonthPay = int(each["lowMonthPay"])
        salary = lowMonthPay * 1000
        if salary == 0:
            continue

        # 学历要求
        degree = each["degreeName"]

        # 职位类别
        categories = category

        # 相关科目要求
        major = each["major"]
        if not major:
            major = ""
        else:
            major = major.replace(',', ' ').replace('，', ' ')

        # 福利(可能为null)
        welfare = each["recTags"]
        if not welfare:
            welfare = ""
        else:
            welfare = welfare.replace(',', ' ').replace('，', ' ')

        # 招聘人数
        head_count = each["headCount"]
        if head_count == '':
            continue

        # 发布日期
        publish_date = each["publishDate"]
        timeArray = time.localtime(int(publish_date / 1000))
        publish_date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        # if str(datetime.date.today()) in str(publish_date):
        #     num += 1

        # 更新日期
        update_date = each["updateDate"]
        timeArray = time.localtime(int(update_date / 1000))
        update_date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

        # 职位来源
        source = each["sourcesNameCh"]
        if not source:
            source = "大学生就业服务平台"

        # compInfo信息

        # 公司名称
        company_name = each["recName"]

        # 地区
        area = each["areaCodeName"]

        # 公司规模
        company_scale = each["recScale"]
        if not company_scale:
            company_scale = ''
        elif company_scale == '员工数量':
            continue

        # 公司性质
        company_property = each["recProperty"]

        saveData(job_id, job_name, salary, degree, categories, major, welfare, head_count, publish_date, update_date,
                 source,
                 company_name, area,
                 company_scale, company_property)
        print(job_id, job_name, salary, degree, categories, major, welfare, head_count, publish_date, update_date,
              source,
              company_name, area,
              company_scale, company_property)
    # if num > 0:
    #     return 'is_today'
    # else:
    #     return 'not_today'


# 存储数据
def saveData(job_id, job_name, salary, degree, categories, major, welfare, head_count, publish_date, update_date,
             source,
             company_name, area,
             company_scale, company_property):
    # 1 获取连接对象
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root', password='123456',
                           database='boss', charset='utf8')

    # 2 获取游标对象
    cursor = conn.cursor()

    # 3 执行SQL语句

    sql = "select * from jobs_info where (job_name = %s and area = %s and company_name = %s)"

    cursor.execute(sql, (str(job_name), str(area), str(company_name)))

    if not cursor.fetchall():
        sql = f"replace into jobs_info(job_id, job_name, salary, degree, categories, major, welfare, head_count, publish_date, update_date, source, " \
              f"company_name, area, company_scale, company_property) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            row_count = cursor.execute(sql, (
                str(job_id), str(job_name), int(salary), str(degree), str(categories), str(major), str(welfare),
                str(head_count),
                str(publish_date), str(update_date), str(source), str(company_name), str(area), str(company_scale),
                str(company_property)))
        except:
            print("数据格式不符合，无法插入数据库")

    # 4 操作结果集---提交事务
    conn.commit()

    # 5 释放资源
    cursor.close()
    conn.close()


if __name__ == '__main__':
    category = {
        '01': '计算机/网络/技术类',
        '02': '电子/电器/通信技术类',
        '03': '行政/后勤类',
        '04': '翻译类',
        '05': '销售类',
        '06': '客户服务类',
        '07': '市场/公关/媒介类',
        '08': '咨询/顾问类',
        '09': '技工类',
        '10': '财务/审计/统计类',
        '11': '人力资源类',
        '12': '教育/培训类',
        '13': '质量管理类',
        '14': '美术/设计/创意类',
        '15': '金融保险类',
        '16': '贸易/物流/采购/运输类',
        '17': '经营管理类',
        '18': '商业零售类',
        '19': '建筑/房地产/装饰装修/物业管理类',
        '20': '法律类',
        '21': '酒店/餐饮/旅游/服务类',
        '22': '生物/制药/化工/环保类',
        '23': '文体/影视/写作/媒体类',
        '24': '机械/仪器仪表类',
        '25': '科研类',
        '26': '工厂生产类',
        '27': '医疗卫生/美容保健类',
        '28': '电气/能源/动力类',
        '29': '其他类'
    }

    # 处理数据，并存入数据库f

    for index in range(3, 29):
        for i in range(1, 5):
            if index < 10:
                ind = '0' + str(index)
            else:
                ind = str(index)
            print(f"获取到第{i}页。。。")
            url = f"https://www.ncss.cn/student/jobs/jobslist/ajax/?&limit=50&offset={i}&categoryCode={ind}"
            page_data = get_Page_Data(url)
            if '"list":[],' in page_data:
                break
            if page_data != 'error':
                if_today = processing_data(page_data, category[ind])
