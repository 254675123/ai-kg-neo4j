# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* parse the parameter and generate cypher *_*

"""
import json


class JsonParser:
    """
    Parser of request parameter.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.jsondata = None
        self.result = {}
    def parseJson(self, queryparam):
        """
        Parse the parameter string to json object .
        :param queryparam: json string
            The json object holds the detail of request all infomation.
        """
        self.querystring = queryparam
        flag = True
        try:
            self.jsondata = json.loads(queryparam)
            self.result['code'] = 200
            self.result['message'] = 'sucess'
        except Exception as err:
            flag = False
            print err
            self.result['code'] = 500
            self.result['message'] = err.message
            self.result['data'] = ''
        return flag

