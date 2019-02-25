# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-30
program       : *_* base query info *_*

"""

import ResponseUtil
from database import Neo4jHandler
from tool.parser import JsonParser


class BaseQuery(object):
    """
    execure the request.
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.qparser = JsonParser.JsonParser()
        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)

        self.resp = ResponseUtil.ResponseUtil()
        self.result = {}