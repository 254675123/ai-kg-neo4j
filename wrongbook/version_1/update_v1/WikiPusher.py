# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-01
program       : *_* push wiki data to neo4j *_*

"""
import WikiReader
from database import Neo4jHandler


class WikiPusher:
    """
    push data to neo4j.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.__sleep_time_per_request = 0.01
        self.__sleep_time_per_request_none = 180.00
        self.__sleep_time_per_loop = 60

        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)
        self.reader = WikiReader.WikiReader()

    def executePush(self):
        data = {
            'format': 'json',
            'action': 'ask',
            'query_v1': '[[Category:Questions]][[ItemBank::805AAF07-1FFF-4B96-A470-A132AE776C87]][[App::c2f8dfa6038b4e12b327c8893e76cc29]]|?Check',
        }
        cypherstatement = self.reader.read(data)
        self.neo4jdriver.cypherexecuter(cypherstatement)


if __name__ == "__main__":
    wikipusher = WikiPusher()
    wikipusher.executePush()