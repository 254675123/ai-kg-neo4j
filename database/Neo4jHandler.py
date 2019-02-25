# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* Read and Write Neo4j *_*

"""
# need install pachage : database-driver
from neo4j.v1 import GraphDatabase
import Neo4jDriver

class Neo4jHandler:
    """
    Handler of graph database Neo4j reading and writing.
    """

    def __init__(self, driver):
        """
        Get Neo4j server driver.
        :param driver: driver object
            A driver object holds the detail of a Neo4j database including server URIs, credentials and other configuration, see
            " httprequest://database.com/docs/api/python-driver/current/driver.html ".
        """
        if driver is None:

            self.driver = Neo4jDriver.Neo4jDriver().driver
        else:
            self.driver = driver

    def __repr__(self):
        printer = 'Neo4j driver "{0}" carry me fly...'.format(self.driver)
        return printer

    def listreader(self, cypher, keys):
        """
        Read data from Neo4j in specified cypher.
        Read and parse data straightly from cypher field result.
        :param cypher: string
            Valid query_v1 cypher statement.
        :param keys: list
            Cypher query_v1 columns to return.
        :return: list
            Each returned record constructs a list and stored in a big list, [[...], [...], ...].
        """

        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                data = []
                result = tx.run(cypher)
                for record in result:
                    rows = []
                    for key in keys:
                        rows.append(record[key])
                    data.append(rows)
                return data

    def dictreader(self, cypher):
        """
        Read data from Neo4j in specified cypher.
        The function depends on constructing dict method of dict(key = value) and any error may occur if the "key" is invalid to Python.
        you can choose function dictreaderopted() below to read data by hand(via the args "keys").
        :param cypher: string
            Valid query_v1 cypher statement.
        :return: list
            Each returned record constructs a dict in "key : value" pairs and stored in a big list, [{...}, {...}, ...].
        """

        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                data = []
                result = tx.run(cypher).records()
                for record in result:
                    item = {}
                    item['QuestionID'] = record[0]
                    item['ItemBankID'] = record[1]
                    data.append(item)

                return data

    def dictreaderopted(self, cypher, keys=None):

        """
        Optimized function of dictreader().
        Read and parse data straightly from cypher field result.
        :param cypher: string
            Valid query_v1 cypher statement.
        :param keys: list, default : none(call dictreader())
            Cypher query_v1 columns to return.
        :return: list.
            Each returned record constructs an dict in "key : value" pairs and stored in a list, [{...}, {...}, ...].
        """

        if not keys:
            return self.dictreader(cypher)
        else:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    data = []
                    result = tx.run(cypher)
                    for record in result:
                        item = {}
                        for key in keys:
                            item.update({'labels': list(record[key]._labels)})
                            item.update({'properties': record[key]._properties})
                        data.append(item)
                    return data

    def cypherexecuterlist(self, cypherarray):
        """
        Execute manipulation into Neo4j in specified cypher.
        :param cypherarray: string list
            Valid handle cypher statement.
        :return: none.
        """
        count = 0
        for cypher in cypherarray:
            try:
                with self.driver.session() as session:
                    with session.begin_transaction() as tx:
                        res = tx.run(cypher)
                        count = count + 1
                        #print 'cypher:'+cypher
                #session.close()
                if count % 100 == 0:
                    print '已经执行cypher语句:'+str(count)
            except Exception:
                print '异常语句：' + cypher
                print '异常：'+Exception.message
        print '共执行cypher语句:' + str(count)

    def cypherexecuter(self, cypher):
        """
        Execute manipulation into Neo4j in specified cypher.
        :param cypher: string
            Valid handle cypher statement.
        :return: none.
        """
        result = None
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(cypher)
        session.close()

        return result
# self test




if __name__ == "__main__":
    uri = "bolt://192.168.211.132:7687"
    driver = GraphDatabase.driver(uri, auth=("database", "123456"))
    MyNH = Neo4jHandler(driver)
    print(MyNH)
    cypher_exec = """
                    CREATE (Neo:Crew {name:'Neo'}),
                           (Morpheus:Crew {name: 'Morpheus'}),
                           (Trinity:Crew {name: 'Trinity'}),
                           (Cypher:Crew:Matrix {name: 'Cypher'}),
                           (Smith:Matrix {name: 'Agent Smith'}),
                           (Architect:Matrix {name:'The Architect'}),
                           (Neo)-[:KNOWS]->(Morpheus),
                           (Neo)-[:LOVES]->(Trinity),
                           (Morpheus)-[:KNOWS]->(Trinity),
                           (Morpheus)-[:KNOWS]->(Cypher),
                           (Cypher)-[:KNOWS]->(Smith),
                           (Smith)-[:CODED_BY]->(Architect)
                  """  # "example cypher statement from http://console.neo4j.org/"

    cypher_read = """
                    MATCH (a) -[:KNOWS|LOVES]-> (b:Crew {name: 'Trinity'})
                    RETURN a.name AS l, b.name AS r
                  """

    MyNH.cypherexecuter(cypher_exec)
    listres = MyNH.listreader(cypher_read, ['l', 'r'])
    print(listres)
    dictres = MyNH.dictreader(cypher_read)
    print(dictres)
    dictoptres = MyNH.dictreaderopted(cypher_read, ['l'])
    print(dictoptres)
