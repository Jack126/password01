#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from tornado import gen
import web.base as webBase
import libs.stock_web_dic as stock_web_dic
import logging
import datetime
import math
"""
    添加需要收集信息的股票入库待命
    name 股票名称
"""
class PostStockHandler(webBase.BaseHandler):
    @gen.coroutine
    def post(self):
        name = self.get_body_argument("name")
        if not name:
            logging.error("error name")
            return
        
        values = []
        values.append(name)
        values.append("0") # code for 0
        values.append('1') # status for 1
        values.append(str(math.floor(datetime.datetime.now().timestamp())))
        tableName = 'stock_wait'
        stockWeb =stock_web_dic.STOCK_WEB_DATA_MAP['stock_wait']
        tmp_columns = "`, `".join(stockWeb.columns)
        tmp_values = "',' ".join(values)
        sql = " INSERT INTO %s (`%s`) VALUES ('%s'); " % (tableName, tmp_columns, tmp_values)
        try:
            self.db.execute(sql)
        except Exception as e:
            err = {"error - ":str(e)}
            logging.error(err)
            self.write(err)
            return