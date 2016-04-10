# -*- coding: UTF-8 -*- 
# Created by qiu on 16-3-31
#

import tornado.web
from usth_api_v1 import Usth

import tornado.escape
import json

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        user = self.get_argument("username", "")
        passw = self.get_argument("password", "")

        if user and passw:

            usth = Usth(host="http://60.219.165.24", name=user, passw=passw)
            result = usth.todo()
            usth.destory()
            if result:
                self.set_header("Content-Type", "application/json")
                self.write(json.dumps(result, ensure_ascii=False))
        else:
            self.write("密码或者账号不能为空")
        self.finish()

