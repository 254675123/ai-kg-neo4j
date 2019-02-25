# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* generate cypher by json *_*

"""
from BaseCypher import BaseCypher

class BankCypher(BaseCypher):
    """
    Genarate cypher statement.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        super(BankCypher, self).__init__()


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
            bankid = jsondata['ItemBankId']
            bankid = str(bankid).strip()
            bankidlength = len(bankid)

            ns = "match (n:Question)"
            cypher.append(ns)
            if bankidlength > 0:
                ns = "where n.databaseid = '{0}'".format(bankid)
                cypher.append(ns)
            cypher.append('RETURN distinct n.coursename,n.courseid,n.databaseid')

            self.keys.append('SubjectName')
            self.keys.append('SubjectCode')
            self.keys.append('ItemBankID')

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

        if not jsondata.__contains__('ItemBankId'):
            flag = False
            self.resp.setResult(self.result, -1, 'itemBankId not cantains')
            return flag

        return flag