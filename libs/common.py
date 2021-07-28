#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import time


class Common():
    def getTime():
        t = time.time()
        return int(t)

    def getMd5(str, salt):
        hl = hashlib.md5(bytes('password01', encoding='utf-8'))
        str = str + salt
        hl.update(bytes(str, encoding='utf-8'))
        return hl.hexdigest()
