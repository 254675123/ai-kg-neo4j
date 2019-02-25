# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-11-14
program       : *_*  request *_*
"""
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def requestHttp(url, body, headers):
    import requests
    import json

    #url = 'http://official-account/app/messages/group'
    #body = {"type": "text", "content": "测试文本", "tag_id": "20717"}
    #headers = {'content-type': "application/json", 'Authorization': 'APP appid = 4abf1a,token = 9480295ab2e2eddb8'}

    # print type(body)
    # print type(json.dumps(body))
    # 这里有个细节，如果body需要json形式的话，需要做处理
    # 可以是data = json.dumps(body)
    response = requests.post(url, data=json.dumps(body), headers=headers)
    # 也可以直接将data字段换成json字段，2.4.3版本之后支持
    # response  = requests.post(url, json = body, headers = headers)

    # 返回信息
    print response.text
    # 返回响应头
    print response.status_code

