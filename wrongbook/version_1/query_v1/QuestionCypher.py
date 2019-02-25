# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* generate cypher by json *_*

"""
from BaseCypher import BaseCypher
class QuestionCypher(BaseCypher):
    """
    Genarate cypher statement.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        super(QuestionCypher, self).__init__()
        self.cypherstatementlist = []


    def generateCypher_ids(self, jsondata):
        """
        Generate the cypher statement by json data .
        :param jsondata: json object
            The json object holds the detail of request all infomation.
        """
        flag = True
        cypher = []
        try:
            # if has cypherstatement
            if 'cypher' in jsondata:
                self.cypherstatement = jsondata['cypher']

                self.result['code'] = 200
                self.result['message'] = 'sucess'
                return flag
            # process the json data
            if jsondata['input_type'] == 'Question' and jsondata['output_type'] == 'Question':
                #ns = 'start rq=node:Question(code="{0}")'.format(jsondata['code'])
                #cypher.append(ns)
                qidlist = jsondata['QuestionIDS']
                length = len(qidlist)
                offset = int(jsondata['offset'])
                offset = offset / length

                limit = int(jsondata['limit'])
                limit = limit / length
                if limit < 1:
                    limit = 1

                for qid in qidlist:
                    ns = "match (rq)<-[:CHECK]-(k)-[:CHECK]->(res)"
                    cypher.append(ns)
                    ns = 'where rq.code="{0}"'.format(qid['QuestionID'])
                    cypher.append(ns)
                    cypher.append('RETURN res.code, res.databaseid, k.code, k.name')
                    cypher.append('order by k.name')
                    cypher.append('skip {0}'.format(jsondata['offset']))
                    cypher.append('limit {0}'.format(jsondata['limit']))
                    cs = '\r\n'.join(cypher)
                    self.cypherstatementlist.append(cs)

                self.keys.append('QuestionID')
                self.keys.append('ItemBankID')
                self.keys.append('KnowledgeID')
                self.keys.append('KnowledgeName')

            elif jsondata['input_type'] == 'Question' and jsondata['output_type'] == 'Knowledge':
                ns = "match (rq)<-[:CHECK]-(res)"
                cypher.append(ns)
                ns = 'where rq.code="{0}"'.format(jsondata['QuestionID'])
                cypher.append(ns)
                cypher.append('RETURN res.code, res.name')

                self.keys.append('KnowledgeID')
                self.keys.append('KnowledgeName')

            #self.cypherstatement = 'process result is cypher statement'
            self.cypherstatement = '\r\n'.join(cypher)

            self.result['code'] = 200
            self.result['message'] = 'sucess'
        except Exception as err:
            flag = False
            print err
            self.result['code'] = 501
            self.result['message'] = err.message
            self.result['data'] = ''
        return flag

    def generateCypher_id(self, jsondata):
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

            # 如果数据有效
            ns = "match (rq)<-[:CHECK]-(k)-[:CHECK]->(res)"
            cypher.append(ns)
            ns = 'where rq.code="{0}" and res.databaseid ="{1}"'.format(jsondata['QuestionId'],jsondata['ItemBankId'])
            cypher.append(ns)
            cypher.append('RETURN res.code, k.code, k.name')
            cypher.append('order by k.name')
            cypher.append('skip 0')
            if jsondata.__contains__('Count'):
                cypher.append('limit {0}'.format(jsondata['Count']))

            self.keys.append('QuestionId')
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
            self.resp.setResult(self.result, 0, 'questionId not cantains')
            return flag
        if not jsondata.__contains__('ItemBankId'):
            flag = False
            self.resp.setResult(self.result, 0, 'itemBankId not cantains')
            return flag
        #if not jsondata.__contains__('Count'):
        #    flag = False
        #    self.resp.setResult(self.result, 0, 'count not cantains')
        #    return flag

        return flag

