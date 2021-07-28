#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import random


class Send():
    def email(db, name):
        sql = "select * from users where name=? ;"
        row = db.get(sql, name)
        if not row:
            return False
        rec_email = row['email']
        mail_host = "smtp.aliyun.com"  # mail smtp host
        mail_user = ""  # username
        mail_pass = ""  # password

        sender = ""  # send email
        receivers = [rec_email]  # receive email

        code = Common.ranstr(8)
        return code, row['id']
        # mess = 'Your number is : ' + code
        # message = MIMEText(mess, 'plain', 'utf-8')
        # message['From'] = Header("", 'utf-8')  # from@aliyun.com
        # message['To'] = Header(rec_email, 'utf-8')  # to@aliyun.com

        # subject = 'Your number'
        # message['Subject'] = Header(subject, 'utf-8')

        # try:
        #     smtpObj = smtplib.SMTP()
        #     smtpObj.connect(mail_host, 25)  # 25 SMTP port
        #     smtpObj.login(mail_user, mail_pass)
        #     smtpObj.sendmail(sender, receivers, message.as_string())
        #     return code, row['id']
        # except smtplib.SMTPException:
        #     return False


class Common():
    def ranstr(num):
        H = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        salt = ''
        for i in range(num):
            salt += random.choice(H)
        return salt
