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
        该类为了处理v2中的问题，题干中没有知识点的概念，此时需要统计题干子网的聚集度，通过统计子网中关系的集中概念
        来给定概念的权重，以此来决定知识点
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
                question_org[word] = 0
                question_ext[word] = 0

            #self.knowledge[line] = words
            param = "','".join(words)
            cypher = "match(n)-[:NEXT]-(m) where n.name in ['{0}'] return m.name as name".format(param)
            result = self.neo4jdriver.cypherexecuter(cypher)
            for record in result:
                name = record['name']
                question_ext[name] = 0

            # 统计每个词，在子网中，有多少关系
            maxcount = 0
            for word in question_ext.keys():
                cypher = "match(n)-[r:NEXT]-(m) where n.name in ['{0}'] return count(r) as count".format(word)
                result = self.neo4jdriver.cypherexecuter(cypher)
                for record in result:
                    count = record['count']
                    question_ext[word] = count

                    if maxcount < count:
                        maxcount = count

                    break

            # associate
            #candidate_qklist_org = self.getAssociateQK_Origin(question_org)
            #candidate_qklist_ext = self.getAssociateQK_Extension(question_ext)
            candidate_qklist_ext = self.getAssociateQK(question_org, question_ext, maxcount)


            associatelist = []
            #maxassociatelist = []
            maxcount = -1
            for candidate_k in candidate_qklist_ext:
                count = candidate_k[1]
                if maxcount == -1.0:
                    maxcount = count
                elif maxcount > count:
                    break

                associatelist.append(candidate_k[0])

            # print
            print '问题{0}:'.format(qindex)+line
            print '知识点:'+ ';'.join(associatelist)
            print '\r\n'

    def getAssociateQK(self, question_org, question, maxcount):
        qklist = []
        for k in self.knowledge.keys():
            klist = self.knowledge.get(k)
            length = len(klist)
            index = 0
            weight = 0.0
            for v in klist:
                if question.__contains__(v):
                    index = index + 1
                    weight = weight + float(question[v]) / (2*maxcount)
                if question_org.__contains__(v):
                    weight = weight + 1.0

            tup = (k, weight)
            qklist.append(tup)

        # sort
        sortlist = sorted(qklist, cmp=lambda x,y:cmp(y[1], x[1]))
        return sortlist

if __name__ == "__main__":
    sr = AssociateQK()
    #sr.generateCypher()
    sr.readKnowledgeList()
    sr.getQuestion()

    print 'split over'