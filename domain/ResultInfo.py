# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-11-05
program       : *_*  course exam question *_*
"""

class ResultInfo(object):
    def __init__(self, index, score, code, text):
        self.id = index
        self.code = code
        self.score = score
        self.text = text

    def toDescription(self):
        desc = u'{}(可信度:{}%)'.format(self.text, round(self.score * 100, 2))
        return desc

    def toFullDescription(self):
        desc = u'{}(编码：{}，可信度:{}%)'.format(self.text, self.code,round(self.score * 100, 2))
        return desc