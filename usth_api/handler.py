# _*_ coding: utf-8 _*_
import time
import logging

import simplejson as json

from tornado.web import RequestHandler

from redis_store import RedisStorage
from spider import Spider


def timer(func):
    def wrap(*args, **kwargs):
        t0 = time.time()
        func(*args, **kwargs)
        t1 = time.time()
        logging.info("function {} speed time {}".format(func.__name__, t1-t0))
    return wrap


def gen_response(code=None, data=None, msg=None, en_msg=""):
    if code is None:
        raise ValueError("code 不为空")
    if msg is None:
        raise ValueError("msg 不为空")
    if data is None:
        data = dict()
    return json.dumps(dict(code=code, data=data, msg=msg, en_msg=en_msg))


class ApiHandler(RequestHandler):
    """
    url:
        /usth/score?query=semester&stu_no=2013025271&pwd=1
        /usth/score?query=pass&stu_no=2013025271&pwd=1
        /usth/socre?query=fail&stu_no=2013025271&pwd=1
    """
    redis_cls = RedisStorage

    @timer
    def get(self, *args, **kwargs):

        query = self.get_argument("query")
        student_number = self.get_argument("stu_no")
        password = self.get_argument("pwd")

        spider = Spider(student_number=student_number, password=password)
        spider.authorized()
        student_id = spider.student_id

        self.set_header("Content-Type", "application/json")
        try:
            if query == "semester":
                storage = self.redis_cls.get_semester_grade(student_id)
                if storage is None:
                    current = spider.parse_semester_grade()
                    if current.code != 0:
                        self.write(json.dumps(dict(current._asdict())))
                        return
                    data = current.data
                else:
                    data = storage

            elif query == "pass":
                storage = self.redis_cls.get_passed_grade(student_id)
                if storage is None:
                    current = spider.parse_passed_grade()
                    if current.code != 0:
                        self.write(json.dumps(dict(current._asdict())))
                        return
                    data = current.data
                else:
                    data = storage

            elif query == "fail":
                storage = self.redis_cls.get_failed_grade(student_id)
                if storage is None:
                    current = spider.parse_failed_grade()
                    if current.code != 0:
                        self.write(json.dumps(dict(current._asdict())))
                        return
                    data = current.data
                else:
                    data = storage
            else:
                raise ValueError("Query Operation Out")
            self.write(gen_response(code=0x0000,
                                    data=data,
                                    msg="成功",
                                    en_msg="Success"))
        except Exception as err:
            self.write(gen_response(code=0x0001,
                                    msg=str(err),
                                    en_msg="Unknown Error"))
