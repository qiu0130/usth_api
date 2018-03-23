# _*_ coding: utf-8 _*_
import tornado.web
import tornado.options
import tornado.httpclient
import tornado.ioloop
import tornado.httpserver
from tornado.options import options, define

from handler import ApiHandler


def main():
    define("port", default=8080, help="run on the given port", type=int)
    tornado.options.parse_command_line()
    application = tornado.web.Application(
        [
            (r'/api/v1/usth/score', ApiHandler)
         ],
        dict(debug=True)
    )
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    print("start...")


if __name__ == "__main__":
    main()