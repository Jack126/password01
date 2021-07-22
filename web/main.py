#!/usr/local/opt/python@3.7/bin/python3
# -*- coding: utf-8 -*-

import os.path
import tornado.escape
from tornado import gen
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json
from pycket.session import SessionMixin

import web.base as webBase
import libs.database as database
from libs.send import Send
from libs.common import Common


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # 设置路由
            (r"/", HomeHandler),
            (r"/test", TestHandler),
            (r"/login.html", LoginHandler),
            (r"/nologin", NologinHandler),
            (r"/send", SendHandler),
        ]
        settings = dict(  # 配置
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,  # True,
            # cookie加密
            cookie_secret="027asdb67090df0392c2da87092z8a17b58b7",
            debug=True,

            blog_title="password01 - tornado",
            login_url="/login.html",
            # 1 配置pycket 注意别忘记开启redis服务C:\redis>redis-server.exe
            pycket={
                'engine': 'redis',
                'storage': {
                    'host': 'localhost',
                    'port': 6379,
                    'db_sessions': 2,
                    # 'password': '',
                    'db_notifications': 11,
                    'max_connections': 2 ** 31,
                },
                'cookies': {
                    'expires_days': 30,
                    'max_age': 5000
                }
            },
        )
        super(Application, self).__init__(handlers, **settings)
        # Have one global connection to the blog DB across all handlers
        self.db = database.Connection("password01.db")


# 首页handler
class HomeHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):

        # sql1 = "select * from users"
        # list1 = self.db.query(sql1)

        # self.render("index.html", entries="hello", data=self.db.get(
        #     "select * from users where id='2'"), list=list1)
        # name = self.get_current_user()
        # self.write("hello %s" % (name))
        print(self.request.headers["User-Agent"])


class LoginHandler(tornado.web.RequestHandler, SessionMixin):
    def get(self, *args, **kwargs):
        self.xsrf_token
        self.render("login.html")

    def post(self, *args, **kwargs):
        name = self.get_body_arguments('name', '')
        password = self.get_body_arguments('password', '')
        code = self.get_body_arguments('code', '')
        if not name:
            self.write({'code': 0, 'message': 'params error'})
        db = database.Connection("password01.db")
        sql = "select * from users where name= ? ;"
        row = db.get(sql, (name,))
        print(row)
        self.write({'code': 1, 'data': name})
        # TODO user password
        #self.set_secure_cookie('user', self.get_argument('user', None))
        # 4设置session
        #@self.session.set('user', self.get_argument('user'))


class TestHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        name = 'jack123'
        self.session.set('cookie_name', name)
        self.write('success login')
        print(self.session.get('cookie_name'))


class NologinHandler(webBase.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write('this message is secrect')


class LogoutHandler(webBase.BaseHandler):
    """
        logout function
    """
    @gen.coroutine
    def get(self):
        self.session.set('user', "")


class SendHandler(webBase.BaseHandler):
    """
        send email
    """
    def post(self):
        code = Send.email()
        if not code:
            self.write({'code': 0})
        try:
            sql = "insert into code(uid, code,createtime) values(?, ?, ?);"
            self.db.execute(sql, 1, code, Common.getTime())
        except Exception as e:
            print(e)
        self.write({'code': 1})


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    port = 9999
    http_server.listen(port)
    tornado.options.parse_command_line()

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
