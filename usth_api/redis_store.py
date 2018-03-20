# _*_ coding: utf-8 _*_
import simplejson as json

import redis

from config import Setting, config


class RedisPools(object):
    redis_conf = config(Setting.app_setting, is_yaml=True).redis
    connection_pool = redis.ConnectionPool(
        host=redis_conf.host,
        port=redis_conf.port,
        db=redis_conf.db
    )

    @classmethod
    def get_redis_connect(cls):
        return redis.Redis(connection_pool=cls.connection_pool)


class RedisStorage(object):
    redis_conn = RedisPools.get_redis_connect()

    @classmethod
    def save_student(cls, student_id, storage):
        cls.redis_conn.hset("student", student_id, storage)

    @classmethod
    def get_student(cls, student_id):
        grade = cls.redis_conn.hget("student", student_id)
        if grade is None:
            return None
        return json.loads(grade.decode("utf-8"))

    @classmethod
    def save_passed_grade(cls, student_id, storage):
        cls.redis_conn.hset("pass_score", student_id, storage)

    @classmethod
    def get_passed_grade(cls, student_id):
        grade = cls.redis_conn.hget("pass_score", student_id)
        if grade is None:
            return None
        return json.loads(grade.decode("utf-8"))

    @classmethod
    def save_failed_grade(cls, student_id, storage):
        cls.redis_conn.hset("fail_score", student_id, storage)

    @classmethod
    def get_failed_grade(cls, student_id):
        grade = cls.redis_conn.hget("fail_score", student_id)
        if grade is None:
            return None
        return json.loads(grade.decode("utf-8"))

    @classmethod
    def save_semester_grade(cls, student_id, storage):
        cls.redis_conn.hset("semester_score", student_id, storage)

    @classmethod
    def get_semester_grade(cls, student_id):
        grade = cls.redis_conn.hget("semester_score", student_id)
        if grade is None:
            return None
        return json.loads(grade.decode("utf-8"))

    @classmethod
    def get_student_list(cls):
        grade_list = cls.redis_conn.hgetall("student")
        if grade_list is None:
            return list()
        return json.loads(grade_list.decode("utf-8"))