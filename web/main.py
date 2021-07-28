#!/usr/local/opt/python@3.7/bin/python3
# -*- coding: utf-8 -*-

import os.path
import tornado.escape
from tornado import gen
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import web.base as webBase
import libs.database as database
from libs.send import Send
from libs.common import Common


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # set route
            (r"/nologin", NologinHandler),
            (r"/test", TestHandler),

            (r"/", HomeHandler),
            (r"/login.html", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/send", SendHandler),
            (r"/account", AccountHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,  # True,
            # cookie加密
            cookie_secret="027asdb67090df0392c2da87092z8a17b58b7",
            debug=True,

            blog_title="password01 - tornado",
            login_url="/login.html",
            salt="PassWord01",
            # 1 配置pycket 注意别忘记开启redis服务
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
class HomeHandler(webBase.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # self.write(self.settings['blog_title'])
        # sql1 = "select * from users"
        # list1 = self.db.query(sql1)

        # self.render("index.html", entries="hello", data=self.db.get(
        #     "select * from users where id='2'"), list=list1)
        name = self.get_current_user()
        self.write(name)
        # self.write("hello %s" % (name))
        # print(self.request.headers["User-Agent"])


class LoginHandler(webBase.BaseHandler):
    def get(self, *args, **kwargs):
        self.xsrf_token
        self.render("login.html", title=self.settings['blog_title'])

    def post(self, *args, **kwargs):
        name = self.get_argument('name', None)
        password = self.get_argument('password', None)
        code = self.get_argument('code', None)
        if not name or not password or not code:
            return self.write({'code': 0, 'message': 'params error'})
        sql = "select * from users where name= ? ;"
        user = self.db.get(sql, str(name))
        if not user:
            return self.write({'code': 0})
        # check code
        sql = "select * from code where uid=? order by createtime desc limit 1;"
        row = self.db.get(sql, str(user['id']))
        if not row:
            return self.write({'code': 0})
        if str(code) != row['code']:
            return self.write({'code': 102})
        pwd = Common.getMd5(str(password), str(self.settings['salt']))
        if pwd != user['password']:
            return self.write({'code': 0})
        # delete code
        self.db.execute("delete from code where uid=?", str(user['id']))
        # user password
        self.set_secure_cookie('user', name)
        # session
        self.session.set('user', name + '=' + str(user['id']))
        return self.write({'code': 1})


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
    @tornado.web.authenticated
    def get(self):
        self.session.set('user', "")


class SendHandler(webBase.BaseHandler):
    """
        send user email
    """
    def post(self):
        name = self.get_argument('name', None)
        if not name:
            self.write({'code': 0})
        code, uid = Send.email(self.db, str(name))
        if not code:
            self.write({'code': 0})
        try:
            sql = "insert into code(uid, code,createtime) values(?, ?, ?);"
            self.db.execute(sql, uid, code, Common.getTime())
        except Exception as e:
            print(e)
        self.write({'code': 1})


class AccountHandler(webBase.BaseHandler):
    """
        list account
    """
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        u = user.split('=')
        uid = u[1]
        sql = "select * from account where uid= ? ;"
        data = self.db.query(sql, uid)
        print(data)
        self.render("account.html", data=data, title=self.settings['blog_title'])


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    port = 9999
    http_server.listen(port)
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
