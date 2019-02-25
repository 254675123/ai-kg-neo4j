# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_*  associate question and knowledge *_*

"""
import sys

from database import Neo4jHandler
from tool.reader import SentenceReader
from tool.splitor import HanlpSplitor

reload(sys)
sys.setdefaultencoding('utf-8')

class AssociateQK:
    """
    word net generator.
    """
    def __init__(self):
        """
        initialize local variables.
        仅仅是对知识点的关键词，如果在子网中，则，改知识点为候选知识点，本类仅做这些事情
        """
        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)
        self.sentence = SentenceReader.SentenceReader()
        #self.splitor = JiebaSplitor.JiebaSplitor()
        self.splitor = HanlpSplitor.HanlpSplitor()
        #self.cypherlist = []
        self.sentcypherlist = []
        #self.cypherlist.append("CREATE CONSTRAINT ON (c:WORD) ASSERT c.name IS UNIQUE;")

        self.knowledge = {}


    def readKnowledgeList(self):
        words = open('./../data/kowledge.txt', 'r')
        ids_lines = words.readlines()
        for line in ids_lines:
            line = line.strip('\n')
            if self.knowledge.__contains__(line):
                continue
            words = self.splitor.split1list(line)
            self.knowledge[line] = words

    def getQuestion(self):
        # match(n)-[:NEXT]-(m) where n.name in ['典型','金本位制','指','金币','本位'] return n,m
        question = open('./../data/financial-test.txt', 'r')
        ids_lines = question.readlines()
        qindex = 0
        for line in ids_lines:
            line = line.strip('\n')
            qindex = qindex + 1
            question_org = {}
            question_ext = {}
            words = self.splitor.split1list(line)
            for word in words:
                question_org[word] = ''
                question_ext[word] = ''

            #self.knowledge[line] = words
            param = "','".join(words)
            cypher = "match(n)-[:NEXT]-(m) where n.name in ['{0}'] return m.name as name".format(param)
            result = self.neo4jdriver.cypherexecuter(cypher)
            for record in result:
                name = record['name']
                question_ext[name] = ''

            # associate
            qklist = []
            for k in self.knowledge.keys():
                klist = self.knowledge.get(k)
                length = len(klist)
                index = 0
                for v in klist:
                    if question.__contains__(v):
                        index = index + 1

                if index == length:
                    qklist.append(k)

            # print
            print '问题{0}:'.format(qindex)+line
            print '知识点:'+ ';'.join(qklist)
            print '\r\n'

if __name__ == "__main__":
    sr = AssociateQK()
    #sr.generateCypher()
    sr.readKnowledgeList()
    sr.getQuestion()

    print 'split over'