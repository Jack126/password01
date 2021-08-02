#!/usr/local/opt/python@3.7/bin/python3
# -*- coding: utf-8 -*-

import os.path
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import web.base as webBase
import libs.database as database
from libs.send import Send
from libs.common import Common
from libs.avatar import get_avatar_html


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # set route
            (r"/", HomeHandler),
            (r"/login.html", LoginHandler),
            (r"/logout.html", LogoutHandler),
            (r"/send.html", SendHandler),
            (r"/account.html", AccountHandler),
            (r"/add.html", AddHandler),
            (r"/setting.html", SettingHandler),
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
                    'max_connections': 2**31,
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


class HomeHandler(webBase.BaseHandler):
    """
        home page
    """
    @tornado.web.authenticated
    def get(self):
        self.render("index.html", title=self.settings['blog_title'])


class LoginHandler(webBase.BaseHandler):
    """
        login page
    """
    def get(self, *args, **kwargs):
        self.xsrf_token
        self.render("login.html", title=self.settings['blog_title'])

    """
        login post
    """

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
            return self.write({'code': 0})
        code, uid = Send.email(self.db, str(name))
        if not code:
            return self.write({'code': 0})
        try:
            sql = "insert into code(uid, code,createtime) values(?, ?, ?);"
            self.db.execute(sql, uid, code, Common.getTime())
        except Exception as e:
            print(e)
        return self.write({'code': 1})


class AddHandler(webBase.BaseHandler):
    """
        add account
    """
    @tornado.web.authenticated
    def get(self):
        self.render("add.html", title=self.settings['blog_title'])


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
        for i in data:
            i['avatar'] = get_avatar_html(str(i['title']), 32)
        self.render("account.html",
                    data=data,
                    title=self.settings['blog_title'])

    @tornado.web.authenticated
    def post(self):
        title = self.get_argument('title', None)
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        if not title or not password or not username:
            return self.write({'code': 0, 'message': 'params error'})
        user = self.get_current_user()
        u = user.split('=')
        uid = u[1]
        try:
            sql = "insert into account(uid,title,username,password) values(?,?,?,?);"
            self.db.execute(sql, uid, title, username, password)
        except Exception as e:
            print(e)
        return self.write({'code': 1})


class SettingHandler(webBase.BaseHandler):
    """
        setting page
    """
    @tornado.web.authenticated
    def get(self):
        self.xsrf_token
        self.render("setting.html", title=self.settings['blog_title'])

    """
        setting post
    """

    def post(self):
        name = self.get_argument('oldpassword', None)
        password = self.get_argument('password', None)
        confirmpwd = self.get_argument('confirmpwd', None)
        if not name or not password or not confirmpwd:
            return self.write({'code': 0, 'message': 'params error'})
        if (password != confirmpwd):
            return self.write({
                'code': 0,
                'message': 'The two passwords are inconsistent'
            })
        user = self.get_current_user()
        u = user.split('=')
        uid = u[1]
        sql = "select * from users where id= ? ;"
        user = self.db.get(sql, int(uid))
        if not user:
            return self.write({'code': 0, 'message': 'Empty user'})
        # check code
        pwd = Common.getMd5(str(name), str(self.settings['salt']))
        if pwd != user['password']:
            return self.write({'code': 0, 'message': 'Error password'})
        if password != confirmpwd:
            return self.write({
                'code': 0,
                'message': 'Two password is not same'
            })

        newpwd = Common.getMd5(str(password), str(self.settings['salt']))
        sql = "update users set password= ? where id= ?;"
        self.db.execute(sql, str(newpwd), int(uid))
        self.session.set('user', "")
        return self.write({'code': 1})


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    port = 9999
    http_server.listen(port)
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
