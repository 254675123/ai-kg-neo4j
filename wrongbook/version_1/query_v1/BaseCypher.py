# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* generate cypher by json *_*

"""
import ResponseUtil

class BaseCypher(object):
    """
    Genarate cypher statement.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.result = {}
        self.cypherstatement = None
        self.keys = []
        self.resp = ResponseUtil.ResponseUtil()