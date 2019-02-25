# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-10-29
program       : *_*  将知识点和试题，生成cypher语句 *_*

"""

from domain import MD5

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class CypherGeneratorProcessor:
    """
    将试题与知识点的对应关系，转换为cypher语句
    试题使用排重后的，
    """
    def __init__(self):
        """
        定义变量
        """
        pass

    def generateCypher(self, qk_list):
        """
        generate cypher 
        :return: 
        """
        self.cypherlist = []
        # first make constraint
        # CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;
        # CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;
        # "MERGE ({0}:Knowledge {{code: '{1}'}})".format(node['key'],node['code'])
        # "MERGE ({0})-[:SOLVE]->({1})".format(knode['key'], qnode['key'])
        if len(qk_list) == 0:
            return

        self.cypherlist.append("CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;")
        self.cypherlist.append("CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;")
        self.cypherlist.append("create index on:Question(databaseid);")
        for item in qk_list:
            coursename = item['coursename']
            k_list = item['knowledge']
            for k in k_list:
                md5code = MD5.getMd5(coursename + k)
                md5code = str(md5code).upper()
                kns = "MERGE (k:Knowledge {{code:'{0}'}}) on create set k.name='{1}'".format(md5code, k)
                #kns = "MERGE (k:Knowledge {{code:'{0}',name: '{1}'}})".format(md5code, k)
                #qns = "MERGE (q:Question {{code: '{0}',type:'{1}', category:'{2}',diff:'{3}',coursename:'{4}',courseid:'{5}', databaseid:'{6}', schoolname:'{7}'}})".format(item['questionid'], item['questiontype'], item['questioncate'],item['questiondiff'],item['coursename'],item['courseid'],item['databaseid'],item['schoolname'])
                qns = "MERGE (q:Question {{code:'{0}'}}) on create set q.type='{1}', q.category='{2}',q.diff='{3}',q.coursename='{4}',q.courseid='{5}', q.databaseid='{6}', q.schoolname='{7}'".format(
                    item['questionid'], item['questiontype'], item['questioncate'], item['questiondiff'],
                    item['coursename'], item['courseid'], item['databaseid'], item['schoolname'])
                rns = "MERGE (k)-[:CHECK]->(q);"
                com = kns + '\r\n' + qns + '\r\n' + rns + '\r\n'
                self.cypherlist.append(com)
