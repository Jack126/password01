#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random


class Common():
    def ranstr(num):
        H = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        salt = ''
        for i in range(num):
            salt += random.choice(H)
        return salt
