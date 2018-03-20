# _*_ coding: utf-8 _*_
import re

from collections import namedtuple, defaultdict

import requests
import simplejson as json
from bs4 import BeautifulSoup

from redis_store import RedisStorage


_LOGIN = "/loginAction.do"
_LOGIN_CHECK = "/menu/s_top.jsp"
_FAILED_GRADE = "/gradeLnAllAction.do?type=ln&oper=bjg"
_PASS_GRADE = "/gradeLnAllAction.do?type=ln&oper=qb"
_SEMESTER = "/bxqcjcxAction.do"

URIS = {"login": _LOGIN,
        "login_check": _LOGIN_CHECK,
        "failed_grade": _FAILED_GRADE,
        "passed_grade": _PASS_GRADE,
        "semester": _SEMESTER}

Course = namedtuple(
    "Course",
    ["id",
     "number",
     "name",
     "en_name",
     "credit",
     "label",
     "score",
     "exam_time",
     "failed_reason"]
)

PassedCourse = namedtuple(
    "PassedCourse",
    ["id",
     "number",
     "name",
     "en_name",
     "credit",
     "label",
     "score"
     ]
)

Response = namedtuple(
    "Response",
    ["code", "msg", "data", "en_msg"]
)

NRE = re.compile(r"  &nbsp;&nbsp;(.+\d?)")
LRE = re.compile(u"欢迎光临&nbsp;(.+?)&nbsp")


class Spider(object):

    redis_cls = RedisStorage
    def __init__(self, student_number, password):
        self._student_number = student_number
        self._password = password
        self._student_name = None

        self.__host = "http://60.219.165.24"
        self.uri_list = list()

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/49.0.2623.87 Safari/537.36"
        }

        self.session = requests.session()
        for key, value in URIS.items():
            setattr(self, key + "_url", self.__host+value)

    @property
    def student_name(self):
        return self._student_name

    @student_name.setter
    def student_name(self, student_name):
        if self._student_name is None:
            self._student_name = student_name

    @property
    def student_id(self):
        return str(self._student_number+":"+self.student_name)

    def authorized(self):
        authorized_form_data = {
            "zjh": self._student_number,
            "mm": self._password
        }
        response = self.session.post(
            url=self.login_url,
            headers=self.headers,
            data=authorized_form_data
        )
        if response.status_code != 200:
            return Response(code=0x0001,
                            data=dict(),
                            msg="登录失败",
                            en_msg="Failed Login")

        soup = BeautifulSoup(response.text, "lxml", from_encoding="utf-8")
        if soup.find(class_="errorTop"):
            return Response(code=0x0002,
                            data=dict(),
                            msg="验证失败",
                            en_msg="Failed Check")

        response = self.session.get(url=self.login_check_url)
        if response.status_code == 200:
            group_list = LRE.search(response.text)
            if group_list:
                self.student_name = group_list.group(1)
                return Response(code=0x000,
                                data=dict(),
                                msg="成功",
                                en_msg="Success")
        return Response(code=0x0003,
                        data=dict(),
                        msg="未知错误",
                        en_msg="Unknown Error")

    def parse_failed_grade(self):
        if self._student_name is None:
            self.authorized()
        response = self.session.get(url=self.failed_grade_url)
        if response.status_code != 200:
            return Response(code=0x0004,
                            data=dict(),
                            msg="不及格成绩页面解析失败",
                            en_msg="")

        score = NRE.findall(response.text)
        pass_count = 0
        if isinstance(score, list):
            pass_count = int(score[1])
        else:
            ValueError("Not Found score")

        soup = BeautifulSoup(response.text, "lxml", from_encoding="utf-8")

        failed_grade_list = list()
        nor_grade_list = list()
        for idx, table in enumerate(soup.find_all(class_="odd")):
            course = list()
            for row in table.find_all("td"):
                course.append(row.text.strip())

            if idx < pass_count:
                failed_grade_list.append(dict(Course(*course)._asdict()))
            else:
                nor_grade_list.append(dict(Course(*course)._asdict()))

        res = Response(code=0x0000,
                       data=dict(failed=failed_grade_list, nor=nor_grade_list),
                       msg="成功",
                       en_msg="success")
        self.redis_cls.save_failed_grade(self.student_id, json.dumps(res.data))
        return res

    def parse_semester_grade(self):
        if self._student_name is None:
            self.authorized()

        response = self.session.get(self.semester_url)
        if response.status_code != 200:
            return Response(code=0x0001,
                            data=dict(),
                            msg="学期成绩页面获取失败",
                            en_msg="")

        soup = BeautifulSoup(response.text, "lxml", from_encoding="utf-8")
        semester_grade_list = list()
        for table in soup.find_all(class_="odd"):
            course = list()
            for row in table.find_all("td"):
                course.append(row.text.strip())
            semester_grade_list.append(dict(Course(*course)._asdict()))

        res = Response(code=0x000,
                       data=dict(semester=semester_grade_list),
                       msg="成功",
                       en_msg="Success")
        self.redis_cls.save_semester_grade(self.student_id, json.dumps(res.data))
        return res

    def parse_passed_grade(self):

        if self._student_name is None:
            self.authorized()
        passed_grade_list = defaultdict(list)
        response = self.session.get(self.passed_grade_url)
        if response.status_code != 200:
            return Response(code=0x0001,
                            data=dict(),
                            msg="",
                            en_msg="")

        soup = BeautifulSoup(response.text, "lxml", from_encoding="utf-8")
        current_frame = soup.find_all('a')
        if len(current_frame) < 1:
            return Response(code=0x0001,
                            data=dict(),
                            msg="全部及格成绩链接失败",
                            en_msg="")

        current_grade_href = current_frame[-1].get("href")
        response = self.session.get(url=self.__host + "/" + current_grade_href)

        if response.status_code != 200:
            return Response(
                code=0x0001,
                data=dict(),
                msg="",
                en_msg=""
            )
        passed_grade_soup = BeautifulSoup(
            response.text, "lxml",
            from_encoding="utf-8")

        semester_name_list = passed_grade_soup.find_all("a")
        title_top_list = passed_grade_soup.find_all(class_="titleTop2")
        if len(semester_name_list) != len(title_top_list):
            raise ValueError("学期成绩出错")

        for title, semester in zip(title_top_list, semester_name_list):
            current_passed_list = list()
            for table in title.find_all(class_="odd"):
                course = list()
                for row in table.find_all("td"):
                    course.append(row.text.strip())

                current_passed_list.append(
                    dict(PassedCourse(*course)._asdict())
                )

            semester_name = semester.get("name")
            if semester_name:
                passed_grade_list[semester_name].append(current_passed_list)

        res = Response(code=0x0000,
                       data=dict(passed=passed_grade_list),
                       msg="成功",
                       en_msg="Success")
        self.redis_cls.save_passed_grade(self.student_id, json.dumps(res.data))
        return res