# -*- coding: UTF-8 -*-
# Created by qiu on 16-3-30
#

import requests
import re
import time

from bs4 import BeautifulSoup

class Usth:
    def __init__(self, host, name, passw):
        self.username = name
        self.password = passw
        self.host = host
        self.login_do = "/loginAction.do"
        self.fail = "/gradeLnAllAction.do?type=ln&oper=bjg"
        self.semester = "/bxqcjcxAction.do"
        self.all_pass = "/gradeLnAllAction.do?type=ln&oper=qb"

        self.stu_name = ""

        self.courses = ["courseId", "courseNo", "courseName", "courseElName", "courseCredit", "courseAttribute",
                       "courseSocre", "examTime","notPassCause"]
        self.session = requests.session()

    def fail_grade(self):

        page = self.session.get(self.host + self.fail)
        if page.status_code != requests.codes.ok:
            return {
                "status": "error",
                "message": "获取不及格成绩页面失败",
            }

        notyet = re.compile(r"  &nbsp;&nbsp;(.+\d?)")

        result = notyet.findall(page.text)
        yet_no = int(result[1])

        if isinstance(yet_no, int) is False:
            return {
                "status": "error",
                "message": "获取尚不及格门数失败",
            }

        fail_grade_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")

        yet_fail = []
        ever_fail = []
        for no, table in enumerate(fail_grade_soup.find_all(class_="odd")):

            item = {}
            for row, coures in zip(table.find_all("td"), self.courses):
                item[coures] = row.text.strip()

            if no < yet_no:
                yet_fail.append(item)  # 尚不及格
            else:
                ever_fail.append(item)  # 曾不及格

        return {"type": "yet", "item": yet_fail, "status": "ok"}, {"type": "ever", "item": ever_fail, "status": "ok"}

    def semester_grade(self):
        page = self.session.get(self.host + self.semester)
        if page.status_code != requests.codes.ok:
            return {
                "status": "error",
                "message": "获取本学期成绩页面失败",
            }

        semester_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
        semester_grade = []
        for table in semester_soup.find_all(class_="odd"):

            item = {}
            for row, coures in zip(table.find_all("td"), self.courses[:-2]):
                item[coures] = row.text.strip()

            semester_grade.append(item)

        return {
           "type": "semester",
            "item": semester_grade,
            "status": "ok",
        }

    def todo(self):

        data = []
        login = self.login()
        if login is not None:
            return login

        if login is None:
            data.append(self.semester_grade())

            fail = self.fail_grade()
            if  isinstance(fail, (list, tuple)):
                data.extend(fail)
            else:
                data.extend(fail)

            passing  =self.pass_grade()
            if isinstance(passing, (list, tuple)):
                data.extend(passing)
            else:
                data.append(self.pass_grade())

            return {
                "data": data,
                "meta":  {
                    "_id": self.username,
                    "_name": self.stu_name,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                },
                "status": "ok"
            }
        return None


    def pass_grade(self):

        page = self.session.get(self.host + self.all_pass)

        if page.status_code != requests.codes.ok:
            return {
                "message": "获取*通过*全部及格成绩页面失败",
                "status": "error",
            }

        all_grade_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")

        iframe = all_grade_soup.find_all('a')
        if isinstance(iframe, list) is False or len(iframe) < 1:
            return {
                "message": "获取*通过*全部及格成绩*链接*失败",
                "status": "error",
            }

        cur_grade_url = iframe[-1].get("href")

        page = self.session.get(self.host + "/" + cur_grade_url)

        if page.status_code != requests.codes.ok:
            return {
                "status": "error",
                "message": "获取全部及格成绩页面失败",
            }

        pass_grade_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")

        all_pass = {}
        all_semester = []
        for top, seme in zip(pass_grade_soup.find_all(class_="titleTop2"), pass_grade_soup.find_all("a")):

            pass_grade_list = []

            for table in top.find_all(class_="odd"):
                item = {}

                for row, coures in zip(table.find_all("td"), self.courses[:-2]):
                    item[coures] = row.text.strip()

                pass_grade_list.append(item)

            cur_semester = seme.get("name")
            if cur_semester:
                semester = cur_semester[:9] + "-" +  cur_semester[12]
                if all_pass.has_key(semester):
                    all_pass[semester].extend(pass_grade_list)
                else:
                    all_pass[semester] = pass_grade_list
                    all_semester.append(semester)
        data = []
        for item in all_semester:
            data.append({"type": item, "item": all_pass[item], "status": "ok"})
        return data

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
            return {
                    "status": "error",
                    "message": "登陆失败",
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    }

        login_soup = BeautifulSoup(login_page.text, "lxml", from_encoding="utf-8").find(class_="errorTop")

        if login_soup:
            return {
                    "status": "error",
                    "message": login_soup.text.strip(),
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    }
        else:
            doc = self.session.get(url = self.host + "/menu/s_top.jsp")
            if doc.status_code == requests.codes.ok:

                # 正则编码
                doc_re = re.compile(u"欢迎光临&nbsp;(.+?)&nbsp")
                name = doc_re.search(doc.text)
                if name:
                    self.stu_name = name.group(1)
            return None

    def destory(self):
        if self.session:
            self.session.close()


