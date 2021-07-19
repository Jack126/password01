#!/usr/local/opt/python@3.7/bin/python3
# -*- coding: utf-8 -*-

import os.path
import tornado.escape
from tornado import gen
import tornado.httpserver
import tornado.ioloop
import tornado.options
import web.base as webBase
import libs.database as database


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # 设置路由
            (r"/", HomeHandler),
            (r"/test",TestHandler),
        ]
        settings = dict(  # 配置
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,  # True,
            # cookie加密
            cookie_secret="027asdb67090df0392c2da87092z8a17b58b7",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)
        # Have one global connection to the blog DB across all handlers
        self.db = database.Connection("password01.db")


# 首页handler
class HomeHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):

        sql1 = "select * from users"
        list1 = self.db.query(sql1)

        self.render("index.html", entries="hello", data=self.db.get("select * from users where id='2'"), list=list1)

class TestHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        self.session['name'] = 'jack'

        print(self.session['name'])

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    port = 9999
    http_server.listen(port)
    tornado.options.parse_command_line()

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
