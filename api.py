# -*- coding: UTF-8 -*- 
# Created by qiu on 16-4-2
#





if __name__ == "__main__":
    pass


# -*- coding: UTF-8 -*-
# Created by qiu on 16-3-30
#


import requests
import json
import re
import time

from bs4 import BeautifulSoup
from pymongo import MongoClient


class UsthAPI:
    def __init__(self, host, name, passw):
        self.username = name
        self.password = passw
        self.host = host
        self.login_do = "/loginAction.do"
        self.fail = "/gradeLnAllAction.do?type=ln&oper=bjg"
        self.semester = "/bxqcjcxAction.do"
        self.all_pass = "/gradeLnAllAction.do?type=ln&oper=qb"

        self.coures = [u"课程号", u"课序号", u"课程名", u"英文课程名", u"学分", u"课程属性", u"成绩", u"考试时间", u"未通过原因"]
        self.session = requests.session()

        # 使用默认localhost
        self.client = MongoClient()
        self.db = self.client.test

        self.delay = {"fail": None, "passing": None, "semester": None}
        self.update_id = None
    # 不及格成绩
    def fail_grade(self):

        page = self.session.get(self.host + self.fail)
        if page.status_code != requests.codes.ok:
            return {
                "_id": self.username,
                "status": "error",
                "cause": u"获取不及格成绩页面失败",
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

        notyet = re.compile(r"  &nbsp;&nbsp;(.+\d?)")

        result = notyet.findall(page.text)
        yet_no = int(result[1])

        if isinstance(yet_no, int) is False:
            return {
                "_id": self.username,
                "status": "error",
                "cause": u"获取尚不及格门数失败",
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }

        fail_grade_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")

        yet_fail = []
        ever_fail = []
        for no, table in enumerate(fail_grade_soup.find_all(class_="odd")):

            item = {}
            for row, coures in zip(table.find_all("td"), self.coures):
                item[coures] = row.text.strip()

            if no < yet_no:
                yet_fail.append(item)  # 尚不及格
            else:
                ever_fail.append(item)  # 曾不及格

        return {
            "_id": self.username,
            "status": "ok",
            u"尚不及格成绩": yet_fail,
            u"曾不及格成绩": ever_fail,
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
    # 本学期成绩
    def semester_grade(self):

        page = self.session.get(self.host + self.semester)

        if page.status_code != requests.codes.ok:
            return {
                "_id": self.username,
                "status": "ok",
                "cause": u"获取本学期成绩页面失败",
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

        semester_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
        semester_grade = []
        for table in semester_soup.find_all(class_="odd"):

            item = {}
            for row, coures in zip(table.find_all("td"), self.coures[:-2]):
                item[coures] = row.text.strip()

            semester_grade.append(item)

        return {
            "_id": self.username,
            "status": "ok",
            u"本学期成绩": semester_grade,
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }

    def todo(self, collection, id):

        login = self.login()

        if login is None:
            login = json.dumps(self.query(collection, id), ensure_ascii=False, indent=4)

        return login
    # 全部及格成绩
    def pass_grade(self):

        page = self.session.get(self.host + self.all_pass)

        if page.status_code != requests.codes.ok:
            return {
                "_id": self.username,
                "status": "error",
                "cause": u"获取*通过*全部及格成绩页面失败",
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

        all_grade_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
        #print(page.text)
        iframe = all_grade_soup.find_all('a')

        #print(iframe)
        if isinstance(iframe, list) is False or len(iframe) < 1:
            return {
                "_id": self.username,
                "status": "error",
                "cause": u"获取*通过*全部及格成绩*链接*失败",
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }


        cur_grade_url = iframe[-1].get("href")

        page = self.session.get(self.host + "/" + cur_grade_url)

        if page.status_code != requests.codes.ok:
            return {
                "_id": self.username,
                "status": "error",
                u"本学期成绩": u"获取全部及格成绩页面失败",
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

        pass_grade_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")

        all_pass = {}
        for top, seme in zip(pass_grade_soup.find_all(class_="titleTop2"), pass_grade_soup.find_all("a")):

            pass_grade_list = []

            for table in top.find_all(class_="odd"):
                item = {}

                for row, coures in zip(table.find_all("td"), self.coures[:-2]):
                    item[coures] = row.text.strip()

                pass_grade_list.append(item)

            if all_pass.get(seme.get("name"), None):
                all_pass[seme.get("name")].extend(pass_grade_list)
            else:
                all_pass[seme.get("name")] = pass_grade_list

        return {
            "_id": self.username,
            "status": "ok",
            u"全部及格成绩": all_pass,
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }
    # 登陆检查
    def login(self):

        from_data = {"zjh": self.username, "mm": self.password}

        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
        }

        login_page = self.session.post(
            url=self.host + self.login_do,
            headers=header,
            data=from_data,
        )
        if login_page.status_code != requests.codes.ok:
            return json.dumps({"error": u"登陆失败"}, ensure_ascii=False)

        login_soup = BeautifulSoup(login_page.text, "lxml", from_encoding="utf-8").find(class_="errorTop")

        if login_soup:
            return json.dumps({"error": login_soup.text.strip()}, ensure_ascii=False)
        else:
            return None
    # 查询
    def query(self, colletion, id):

        if self.db is None:
            return json.dumps({"error": u"mongodb连接错误"}, ensure_ascii=False)

        if colletion == "fail":
            result = self.db.fail.find_one({"_id": id})

            if result is None:
                result = self.fail_grade()
                self.delay[colletion] = result
                self.update_id = None
            else:
                self.update_id = result[u'_id']
                print(self.update_id)

        elif colletion == "passing":
            result = self.db.passing.find_one({"_id": id})

            if result is None:
                result = self.pass_grade()
                self.delay[colletion] = result
                self.update_id = None
            else:
                self.update_id = result[u'_id']

        else:
            result = self.db.semester.find_one({"_id": id})
            if result is None:
                result = self.semester_grade()
                self.delay[colletion] = result
                self.update_id = None
            else:
                self.update_id = result[u'_id']

        return result if result else json.dumps({"error": u"不明物体"}, ensure_ascii=False)
    # 插入
    def insert(self):
        if self.delay.get("fail", None):
            print("insert fail --- ")
            self.db.fail.insert_one(self.delay["fail"])
        elif self.delay.get("passing", None):
            print("insert passing --- ")
            self.db.passing.insert_one(self.delay["passing"])
        elif self.delay.get("semester", None):
            print("insert semester -- ")
            self.db.semester.insert_one(self.delay["semester"])
    # 更新
    def update(self, collection, id):

        if collection == "fail":
            print("update fail === ")
            self.db.fail.update_one({"_id": id}, {"$set": self.fail_grade()})
        elif collection == "passing":
            print("update passing === ")
            self.db.passing.update_one({"_id": id}, {"$set": self.pass_grade()})
        elif collection == "semester":
            print("update semester == ")
            self.db.semester.update({"_id": id}, {"$set": self.semester_grade()})
    # 清空数据
    def drop(self, collection):
        if collection == "fail":
            self.db.fail.drop()
        elif collection == "passing":
            self.db.passing.drop()
        elif collection == "semester":
            self.db.semester.drop()
    # 关掉数据库 session
    def destroy(self):
        if self.client:
            self.client.close()
        if self.session:
            self.session.close()







