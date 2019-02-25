# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* Read and Write Neo4j *_*

"""

# need install pachage : database-driver
from neo4j.v1 import GraphDatabase


class Neo4jDriver:
    """
    database ip , user , passwd, and so on.
    """

    def __init__(self):
        """
        Get Neo4j server driver.
            A driver object holds the detail of a Neo4j database including server URIs, credentials and other configuration, see
            " httprequest://database.com/docs/api/python-driver/current/driver.html ".
        """
        #self.uri = "bolt://192.168.211.132:7687"
        #self.uri = "bolt://10.100.137.50:7687"
        self.uri = "bolt://10.100.17.155:7687"
        self.driver = GraphDatabase.driver(self.uri, auth=("neo4j", "123456"))


