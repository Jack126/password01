#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from common import Common


class Send():
    mail_host = "smtp.163.com"  # 设置服务器
    mail_user = ""  # 用户名
    mail_pass = ""  # 口令

    sender = ''
    receivers = ['']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    code = 'Your code is : ' + Common.ranstr(8)
    message = MIMEText(code, 'plain', 'utf-8')
    message['From'] = Header("password01-code", 'utf-8')
    message['To'] = Header("password01-code", 'utf-8')

    subject = 'Password01 code'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("send success")
    except smtplib.SMTPException:
        print("Error: send error")
