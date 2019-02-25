# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-11-14
program       : *_*  save knowledge information *_*
"""
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from tool.httprequest import HttpRequester

class KnowledgeSaver:
    """
        catalog information.
        """

    def __init__(self):
        """
        initialize local variables.
        """
        pass


    def saveKnowledge(self, data):
        # data 为对象
        # url
        #url = 'http://10.100.133.35/api/resourceservice/v3/ai/knowledges'
        url = 'http://p-paas-api-resource-test.testyf.ak/api/resourceservice/v3/ai/knowledges'
        #app_key = 'c2f8dfa6038b4e12b327c8893e76cc29'
        #app_secret = '11ec1b2189f8438e89678371b8a3de02'
        headers = {"content-type": "application/json","appkey":"c2f8dfa6038b4e12b327c8893e76cc29",
                   "appsecret":"11ec1b2189f8438e89678371b8a3de02"}

        HttpRequester.requestHttp(url, data, headers)


if __name__ == "__main__":
    c = KnowledgeSaver()
    #
    data = [{ "name": "但丁", "industry": "1020", "subject": "200I1", "course": "30001", "code": "1020-20011-30001-1.2.4.3", "precons": "12221", "poscons": "22231"},
            { "name": "黄河", "industry": "1021", "subject": "200I1", "course": "30001", "code": "1021-20011-30001-1.2.4.3", "precons": "12221", "poscons": "22231"}]
    c.saveKnowledge(data)