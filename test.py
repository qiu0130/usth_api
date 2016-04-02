# -*- coding: UTF-8 -*-
# Created by qiu on 16-3-31
#


import tornado.web
import tornado.options
import  tornado.httpclient
import tornado.ioloop
import tornado.httpserver


from tornado.options import options, define
from app import  MainHandler

define("port", default=8001, help="run on the given port", type=int)


if __name__ == "__main__":

    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r'/api', MainHandler)

    ])

    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()













