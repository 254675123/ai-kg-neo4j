# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* tornado service *_*

"""
import time

import tornado.web
from tornado.options import options

from wrongbook.version_2.query_v2 import BankQuery
from wrongbook.version_2.query_v2 import KnowledgeQuery
from wrongbook.version_2.query_v2 import QuestionQuery

tornado.options.define('port', default=8888, help='run on this port', type=int)
#tornado.options.define("log_file_prefix", default='tornado_8888.log')
tornado.options.parse_command_line()

class KnowledgeHandler(tornado.web.RequestHandler):

    def get(self):
        start = time.time()
        #queryparam = self.get_argument('query_v1')
        #if queryparam is None:
        queryparam = self.request.body
        # 打印信息
        print('==========>')
        print("[INFO]开始处理本次请求:" + str(queryparam))

        # 处理句子
        #result_list = ChartPusher.start(image_ids)
        #res = ','.join(result_list)
        qe = KnowledgeQuery.KnowledgeQuery()
        res = qe.executeQuery(queryparam)

        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.write(res)
        print("[INFO]本次耗时" + str((time.time() - start)*1000) + "ms")

        return

    def post(self):
        self.get()


class QuestionHandler(tornado.web.RequestHandler):

    def get(self):
        start = time.time()
        #queryparam = self.get_argument('query_v1')
        #if queryparam is None:
        queryparam = self.request.body
        # 打印信息
        print('==========>')
        print("[INFO]开始处理本次请求:" + str(queryparam))

        # 处理句子
        #result_list = ChartPusher.start(image_ids)
        #res = ','.join(result_list)
        qe = QuestionQuery.QuestionQuery()
        res = qe.executeQuery(queryparam)

        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.write(res)
        print("[INFO]本次耗时" + str((time.time() - start)*1000) + "ms")

        return

    def post(self):
        self.get()


class BankHandler(tornado.web.RequestHandler):

    def get(self):
        start = time.time()
        #queryparam = self.get_argument('query_v1')
        #if queryparam is None:
        queryparam = self.request.body
        # 打印信息
        print('==========>')
        print("[INFO]开始处理本次请求:" + str(queryparam))

        # 处理句子
        #result_list = ChartPusher.start(image_ids)
        #res = ','.join(result_list)
        qe = BankQuery.BankQuery()
        res = qe.executeQuery(queryparam)

        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.write(res)
        print("[INFO]本次耗时" + str((time.time() - start)*1000) + "ms")

        return

    def post(self):
        self.get()


if __name__ == "__main__":

    settings = {
        'template_path': 'views',  # html文件
        'static_path': 'statics',  # 静态文件（css,js,img）
        'static_url_prefix': '/statics/',  # 静态文件前缀
        'cookie_secret': 'adm',  # cookie自定义字符串加盐
    }

    application = tornado.web.Application([(r"/api/v1/knowledges/recommend", QuestionHandler),
                                           (r"/api/v1/knowledges", KnowledgeHandler),
                                           (r"/api/v1/knowledges/issupport", BankHandler)],
                                          **settings)
    application.listen(options.port)
    print("SERVICE 已经开启！")
    tornado.ioloop.IOLoop.instance().start()
