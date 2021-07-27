#!/usr/local/opt/python@3.7/bin/python3
# -*- coding: utf-8 -*-

import tornado.web
from pycket.session import SessionMixin
# 基础handler，主要负责检查sqlite的数据库链接。


class BaseHandler(tornado.web.RequestHandler, SessionMixin):
    def initialize(self):
        user = self.get_current_user()
        if not user:
           self.render('login.html')

    def get_current_user(self):
       return self.session.get('user')

    @property
    def db(self):
        try:
            # check every time。
            self.application.db.query("SELECT 1 ")
        except Exception as e:
            print(e)
            self.application.db.reconnect()
        return self.application.db
    