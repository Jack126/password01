#!/usr/local/opt/python@3.7/bin/python3
# -*- coding: utf-8 -*-

import os.path
import torndb
import tornado.escape
from tornado import gen
import tornado.httpserver
import tornado.ioloop
import tornado.options
import web.base as webBase
import libs.common as common
import web.dataTableHandler as dataTableHandler

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # 设置路由
            (r"/", HomeHandler),
            (r"/stock", dataTableHandler.PostStockHandler),
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
        self.db = torndb.Connection(
            charset="utf8", max_idle_time=3600, connect_timeout=1000,
            host=common.MYSQL_HOST, database=common.MYSQL_DB,
            user=common.MYSQL_USER, password=common.MYSQL_PWD)


# 首页handler。
class HomeHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        sql = 'select * from test limit 1'
        row = self.db.query(sql)
        list = common.select(sql)
        self.render("index.html", entries="hello", data=row,list=list)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    port = 9999
    http_server.listen(port)
    # tornado.options.options.logging = "debug"
    tornado.options.parse_command_line()

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
