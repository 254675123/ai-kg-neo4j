# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* generate cypher by json *_*

"""

from BaseCypher import BaseCypher

class KnowledgeCypher(BaseCypher):
    """
    Genarate cypher statement.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        super(KnowledgeCypher, self).__init__()

    def generateCypher(self, jsondata):
        """
        Generate the cypher statement by json data .
        :param jsondata: json object
            The json object holds the detail of request all infomation.
        """
        flag = True
        cypher = []
        try:
            # 校验数据参数
            flag = self.jsondataValidating(jsondata)
            if flag == False:
                return flag

            # process the json data
            ns = "match (rq)<-[:CHECK]-(res)"
            cypher.append(ns)
            ns = 'where rq.code="{0}"'.format(jsondata['QuestionId'])
            cypher.append(ns)
            cypher.append('RETURN res.code, res.name')

            self.keys.append('KnowledgeId')
            self.keys.append('KnowledgeName')

            #self.cypherstatement = 'process result is cypher statement'
            self.cypherstatement = '\r\n'.join(cypher)

        except Exception as err:
            flag = False
            print err
            self.resp.setResult(self.result, -1, err.message)
        return flag

    def jsondataValidating(self, jsondata):
        """
        检查jsondata中是否存在完整的参数
        :param jsondata: 
        :return: False, True
        """
        flag = True

        if not jsondata.__contains__('QuestionId'):
            flag = False
            self.resp.setResult(self.result, -1, 'questionId not cantains')
            return flag

        return flag