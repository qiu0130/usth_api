# -*- coding: UTF-8 -*-
# Created by qiu on 16-3-31
#

import tornado.web
import tornado.options
import  tornado.httpclient
import tornado.ioloop
import tornado.httpserver

from api import UsthAPI

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("login.html")

    def post(self):
        user = self.get_argument("username", "")
        passw = self.get_argument("password", "")
        query = self.get_argument("type", "")
        if user and passw and query:
            usth = UsthAPI(host="http://60.219.165.24", name=user, passw=passw)
            result = usth.todo(collection=query, id = user)

            self.set_header("Content-Type", "application/json")
            self.write(result)

            updateId = usth.update_id

            if updateId:
                usth.update(query, updateId)
            else:
                usth.insert()
        else:

            self.write(u"密码或者账号不能为空")
        usth.destroy()














