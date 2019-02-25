# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-12-11
program       : *_*  define knowledge information *_*
"""
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import FilePath



class Knowledge:
    """
    knowledge information.
    """
    code = ''
    name = ''
    belongs = {}
    precons = {}
    poscons = {}

    def __init__(self):
        """
        initialize local variables.
        """
        pass


    def initByString(self, k_str):
        if len(k_str) == 0:
            return
        properties = k_str.split(' ')
        if len(properties) < 2:
            return

        self.code = properties[0]
        self.name = properties[1]
        #self.belongs = ?
        #self.precons = properties[2]
        #self.poscons = properties[3]

    def toDict(self):
        k_dict = {}
        k_dict['code'] = self.code
        k_dict['name'] = self.name
        k_dict['belongs'] = ''
        k_dict['precons'] = ''
        k_dict['poscons'] = ''

        sec_list = self.code.split('.')
        if len(sec_list) > 2:
            k_dict['course'] = '.'.join(sec_list[:3])

        return k_dict