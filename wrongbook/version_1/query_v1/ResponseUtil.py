# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-08-01
program       : *_* response util  *_*

"""

class ResponseUtil:
    """
    execure the response.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.version = 'v1'

    def setResult(self, result_dict, code, message, data=''):
        """
        set result content
        :param result_dict: 
        :param code: 
        :param message: 
        :param data: 
        :return: 
        """
        result_dict['code'] = code
        result_dict['message'] = message
        result_dict['data'] = data
        result_dict['version'] = self.version