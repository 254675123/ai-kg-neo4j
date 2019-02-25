# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* push wiki data to neo4j *_*

"""

import sys

import requests

from tool.parser import JsonParser

reload(sys)
sys.setdefaultencoding('utf-8')

class WikiReader:
    """
    read wiki schema data from api.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.username = 'root'
        self.password = 'openopen'  # see https://www.mediawiki.org/wiki/Manual:Bot_passwords
        self.api_url = 'httprequest://59.110.153.81/mediawiki/api.php'
        #summary = 'bot hello'
        #message = 'Hello Wikipedia. I am alive! haha'
        #page = 'Sandbox'
        self.jsonparer = JsonParser.JsonParser()
        self.resultjson = None
        self.cypherstatement = None
        self.knode = None
        self.qnode = None
        self.relation = None

    def read(self, jsondata):
        session = requests.Session()

        # query_v1
        r4 = session.post(self.api_url, data=jsondata)
        stat = self.jsonparer.parseJson(r4.text)
        if stat:
            self.resultjson = self.getSubJsonObject(self.jsonparer.jsondata, 'results')
            self.getNodeAndRelation(self.resultjson)
            self.cypherstatement = self.cypherGenerate()
        return self.cypherstatement

    def getSubJsonObject(self, dic_json, mainkey):
        res = None
        if isinstance(dic_json,dict): #判断是否是字典类型isinstance 返回True false
            queryjson = dic_json['query_v1']
            if queryjson.__contains__(mainkey):
                res = queryjson[mainkey]
        return res

    def getNodeAndRelation(self,jsondata):
        self.knode = []
        self.qnode = []
        self.relation = []
        if jsondata is None:
            return None
        qindex = 1
        kindex = 1
        for key in jsondata:
            code = key
            firv = jsondata[key]
            if firv.__contains__('printouts'):
                secv = firv['printouts']

                # QuestionDesc = secv['QuestionDesc']
                #for qd in QuestionDesc:
                #    qnode = {}
                #    qnode['key'] = 'q' + str(qindex)
                #    qnode['code'] = code
                #    qnode['text'] = qd['fulltext']
                #    self.qnode.append(qnode)
                #    qindex = qindex + 1
                qnode = {}
                qnode['key'] = 'q' + str(qindex)
                qnode['code'] = code
                self.qnode.append(qnode)

                Knowledge = secv['Check']
                for kd in Knowledge:
                    knode = {}
                    knode['key'] = 'k' + str(kindex)
                    knode['code'] = kd['fulltext']

                    self.knode.append(knode)
                    kindex = kindex + 1

                    # relation
                    relnode = (knode, qnode)
                    self.relation.append(relnode)
                    #self.relation = zip(self.knode, self.qnode)

    def cypherGenerate(self):
        cypher = []
        #cypher.append('MERGE ')
        for node in self.knode:
            #s = "({0}:Knowledge {{code: '{0}', text:'{1}'}})".format(code,text)
            ns = "MERGE ({0}:Knowledge {{code: '{1}'}})".format(node['key'],node['code'])
            cypher.append(ns)
        for node in self.qnode:
            ns = "MERGE ({0}:Question {{code: '{1}'}})".format(node['key'],node['code'])
            cypher.append(ns)

        for node in self.relation:
            # (Neo)-[:KNOWS]->(Morpheus),
            knode = node[0]
            qnode = node[1]

            ns = "MERGE ({0})-[:SOLVE]->({1})".format(knode['key'], qnode['key'])
            cypher.append(ns)

        #res = 'MERGE ' +  ', '.join(cypher)
        res =  '\r\n '.join(cypher)

        return res

if __name__ == "__main__":
    wikireader = WikiReader()

    data1 = {
        'format': 'json',
        'action': 'ask',
        'query_v1': '[[Category:Recipe]]|?zhishidian',
    }

    data = {
        'format': 'json',
        'action': 'ask',
        'query_v1': '[[Category:大学英语（一）]]|?QuestionDesc |?Knowledge',
    }

    wikireader.read(data)