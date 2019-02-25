# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-30
program       : *_* execute the query_v1 request *_*

"""

import BankCypher
from BaseQuery import BaseQuery

class BankQuery(BaseQuery):
    """
    execure the request.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        super(BankQuery, self).__init__()

        self.cyther = BankCypher.BankCypher()

    def executeQuery(self, queryparam):
        """
        execute query_v1 request .
        :param queryparam: json string
            The json object holds the detail of request all infomation.
        """
        flag = self.qparser.parseJson(queryparam)
        # parse fail
        if flag == False:
            return self.qparser.result

        # parse sucess, and generate cypher statement
        state = self.cyther.generateCypher(self.qparser.jsondata)

        # generate statement is none or empty
        if state == False:
            return self.cyther.result

        try:
            data = self.queryData()
            #data = self.neo4jdriver.dictreaderopted(self.cyther.cypherstatement,self.cyther.keys)
            length = len(data)
            if length > 0 :
                self.resp.setResult(self.result, 1, 'exist')
            else:
                self.resp.setResult(self.result, 0, 'no exist')
        except Exception as err:
            flag = False
            print err
            self.resp.setResult(self.result, -1, err.message)
        return self.result

    def queryData(self):
        """
        Read data from Neo4j in specified cypher.
        The function depends on constructing dict method of dict(key = value) and any error may occur if the "key" is invalid to Python.
        you can choose function dictreaderopted() below to read data by hand(via the args "keys").
        :param cypher: string
            Valid query_v1 cypher statement.
        :return: list
            Each returned record constructs a dict in "key : value" pairs and stored in a big list, [{...}, {...}, ...].
        """
        data = []
        cypherstatement = self.cyther.cypherstatement
        with self.neo4jdriver.driver.session() as session:
            with session.begin_transaction() as tx:

                fieldlength = len(self.cyther.keys)
                result = tx.run(cypherstatement).records()
                for record in result:
                    item = {}
                    index = 0
                    while index < fieldlength:
                        item[self.cyther.keys[index]] = record[index]
                        index = index + 1
                    data.append(item)

                return data

if __name__ == "__main__":
    qe = BankQuery()
    queryparam = '{"ItemBankId":"4C1DD98E-1F3A-47EF-A77D-42F60DC7FFEF"}'
    res = qe.executeQuery(queryparam)