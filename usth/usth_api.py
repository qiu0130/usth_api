# -*- coding: UTF-8 -*-
# Created by qiu on 16-3-30
#


import requests
import re
import time

from bs4 import BeautifulSoup
#from pymongo import MongoClient

import sae.kvdb

class UsthAPI:
    def __init__(self, host, name, passw):
        self.username = name
        self.password = passw
        self.host = host
        self.login_do = "/loginAction.do"
        self.fail = "/gradeLnAllAction.do?type=ln&oper=bjg"
        self.semester = "/bxqcjcxAction.do"
        self.all_pass = "/gradeLnAllAction.do?type=ln&oper=qb"

        self.stu_name = ""
        self.coures = ["course_id", "course_no", "course_name", "course_el_name", "credit", "course_attribute",
                       "socre", "exam_time","not_pass_cause"]
        self.session = requests.session()

        # 使用默认localhost
        #self.client = MongoClient()
        #self.db = self.client.test

        self.kv = sae.kvdb.Client()
        '''
        self.getcwd = os.path.join(os.path.dirname(__file__), "static")

        self.fail_p = os.path.join(self.getcwd, "fail")
        self.passing_p = os.path.join(self.getcwd, "passing")
        self.semester_p = os.path.join(self.getcwd, "semester")
        '''

        self.delay = {"fail": None, "passing": None, "semester": None}
        self.update_id = None

    def fail_grade(self):

        page = self.session.get(self.host + self.fail)
        if page.status_code != requests.codes.ok:
            return {
                "_id": self.username,
                "_name": self.stu_name,
                "status": "error",
                "cause": "获取不及格成绩页面失败",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

        notyet = re.compile(r"  &nbsp;&nbsp;(.+\d?)")

        result = notyet.findall(page.text)
        yet_no = int(result[1])

        if isinstance(yet_no, int) is False:
            return {
                "_id": self.username,
                "status": "error",
                "_name": self.stu_name,
                "cause": "获取尚不及格门数失败",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
            "_name": self.stu_name,
            "yet_fail_grade": yet_fail,
            "ever_fail_grade": ever_fail,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

    def semester_grade(self):

        page = self.session.get(self.host + self.semester)

        if page.status_code != requests.codes.ok:
            return {
                "_id": self.username,
                "status": "ok",
                "_name": self.stu_name,
                "cause": "获取本学期成绩页面失败",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
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
            "_name": self.stu_name,
            "this_semester_grade": semester_grade,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }

    def todo(self, collection, id):

        login = self.login()
        if login is None:
            login = self.query(collection, id)

        return login

    def pass_grade(self):

        page = self.session.get(self.host + self.all_pass)

        if page.status_code != requests.codes.ok:
            return {
                "_id": self.username,
                "status": "error",
                "_name": self.stu_name,
                "cause": "获取*通过*全部及格成绩页面失败",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

        all_grade_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
        #print(page.text)
        iframe = all_grade_soup.find_all('a')

        #print(iframe)
        if isinstance(iframe, list) is False or len(iframe) < 1:
            return {
                "_id": self.username,
                "status": "error",
                "_name": self.stu_name,
                "cause": "获取*通过*全部及格成绩*链接*失败",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

        cur_grade_url = iframe[-1].get("href")

        page = self.session.get(self.host + "/" + cur_grade_url)

        if page.status_code != requests.codes.ok:
            return {
                "_id": self.username,
                "status": "error",
                "_name": self.stu_name,
                "cause": "获取全部及格成绩页面失败",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

        pass_grade_soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")

        all_pass = {}

        all_semester = []
        for top, seme in zip(pass_grade_soup.find_all(class_="titleTop2"), pass_grade_soup.find_all("a")):

            pass_grade_list = []

            for table in top.find_all(class_="odd"):
                item = {}

                for row, coures in zip(table.find_all("td"), self.coures[:-2]):
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
            '''
            else:
                all_pass[semester[:9] + "-" + semester[12]] = pass_grade_list
            '''

        all_pass["_id"] = self.username
        all_pass["status"] = "ok"
        all_pass["_name"] = self.stu_name
        all_pass["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        all_pass["semeters"] = all_semester

        return all_pass


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
            return {"status": "error", "cause": "登陆失败",  "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),}

        login_soup = BeautifulSoup(login_page.text, "lxml", from_encoding="utf-8").find(class_="errorTop")

        if login_soup:
            return {"status": "error", "cause": login_soup.text.strip(),  "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),}
        else:
            doc = self.session.get(url = self.host + "/menu/s_top.jsp")
            if doc.status_code == requests.codes.ok:

                # 正则编码
                doc_re = re.compile(u"欢迎光临&nbsp;(.+?)&nbsp")
                name = doc_re.search(doc.text)
                if name:
                    self.stu_name = name.group(1)
            return None

    def query(self, colletion, id):
        '''
        if self.db is None:
            return json.dumps({"error": "mongodb连接错误"}, ensure_ascii=False)
        '''
        id += ".json"
        if colletion == "fail":
            id = "fail/" + id
            result = self.kv.get(str(id))

            if result:
                self.update_id = "update", result['_id']
            else:
                result = self.fail_grade()
                self.delay[colletion] = result
                self.update_id = "insert", result['_id']

        elif colletion == "passing":
            id = "passing/" + id
            result = self.kv.get(str(id))
            if result:
                self.update_id = 'update', result['_id']
            else:
                result = self.pass_grade()
                self.delay[colletion] = result
                self.update_id = 'insert', result['_id']

        elif colletion == "semester":
            id = "semester/" + id
            result = self.kv.get(str(id))

            if result:

                self.update_id = "update", result['_id']
            else:
                result = self.semester_grade()
                self.delay[colletion] = result
                self.update_id = 'insert', result['_id']

        return result if result else {"status": "error", "cause": "不明物体","_name": self.stu_name,
                                                 "created_at": time.strftime("%Y-%m-%d %H:%M:%S",
                                                                             time.localtime())}

    def insert(self, id):
        id += ".json"
        if self.delay.get("fail", None):
            id = "fail/" + id
            print("insert fail --- ")
            self.kv.add(str(id), self.delay["fail"])

        elif self.delay.get("passing", None):
            id = "passing/" + id
            print("insert passing --- ")

            self.kv.add(str(id), self.delay['passing'])
        elif self.delay.get("semester", None):
            id = "semester/" + id
            print("insert semester -- ")
            self.kv.add(str(id), self.delay['semester'])

    def update(self, collection, id):
        id += ".json"
        if collection == "fail":
            id = "fail/" + id
            print("update fail --- ")
            self.kv.replace(str(id), self.fail_grade())

        elif collection == "passing":
            id = "passing/" + id
            print("update passing --- ")

            self.kv.replace(str(id), self.pass_grade())
        elif collection == "semester":
            id = "semester/" + id
            print("update semester -- ")
            self.kv.replace(str(id), self.semester_grade())

    def destory(self):
        if self.session:
            self.session.close()
        if self.kv:
            self.kv.disconnect_all()




    '''
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

    def drop(self, collection):
        if collection == "fail":
            self.db.fail.drop()
        elif collection == "passing":
            self.db.passing.drop()
        elif collection == "semester":
            self.db.semester.drop()

    def destroy(self):

        if self.client:
            self.client.close()
        if self.session:
            self.session.close()
    '''



'''
    内网 http://192.168.11.239
    外网 http://60.219.165.24
'''

'''
if __name__ == "__main__":
    name = "2013025273"
    password = "1"
    QueryType = "semester"

    import time

    for i in range(2013025256, 2013025287):
        name = str(i)
        usthApi = UsthAPI(host="http://60.219.165.24", name=name, passw=password)

        result = usthApi.todo(QueryType, id=name)
        if json.loads(result).get("error", None):
            print(json.loads(result).get("error", None))
        else:

            updateId = usthApi.update_id
            print(result)
            print(name, updateId)

            if updateId:
                usthApi.update(QueryType, updateId)
            else:
                usthApi.insert()
        usthApi.destroy()
        time.sleep(0.1)
'''


