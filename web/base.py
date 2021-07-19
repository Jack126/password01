#!/usr/local/opt/python@3.7/bin/python3
# -*- coding: utf-8 -*-

import tornado.web

#基础handler，主要负责检查sqlite的数据库链接。


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        try:
            # check every time。
            self.application.db.query("SELECT 1 ")
        except Exception as e:
            print(e)
            self.application.db.reconnect()
        return self.application.db
