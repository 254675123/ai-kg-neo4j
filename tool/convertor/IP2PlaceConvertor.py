#!/usr/bin/env python
# encoding: utf-8
# date: 2016-03-31
# note: 测试中遇到的问题,请求指定的链接会有超时现象,可以多请求几次

import requests, re
import sys

reload(sys)
sys.setdefaultencoding('utf8')

IP138_API = 'httprequest://www.ip138.com/ips138.asp?ip='
PATTERN = ur'<li>本站数据：(.*?)</li>'


def query_api(url):
    data = ''
    r = requests.get(url)
    if r.status_code == 200:
        data = r.content
    return data


def parse_ip138(html):
    # 只能是unicode编码,不能在后面再转换为utf-8,否则无法正则匹配上.
    html = unicode(html, 'gb2312')
    # html = unicode(html, 'gb2312').encode('utf-8')
    # print html
    pattern = re.compile(PATTERN)
    m = pattern.search(html)
    if m:
        print m.group(1)
    else:
        print 'regex match failed'


if __name__ == '__main__':
    url = IP138_API + '61.135.169.125' + '&action=2'
    resp = query_api(url)
    if not resp:
        print 'no content'
    parse_ip138(resp)
