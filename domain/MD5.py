# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-06
program       : *_* read excel data  *_*

"""
import hashlib


def getMd5(text):

    md5 = hashlib.md5(text.encode('utf-8')).hexdigest()

    return md5