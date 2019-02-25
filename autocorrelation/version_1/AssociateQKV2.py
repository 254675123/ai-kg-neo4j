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

class AssociateQKByKeyword:
    """
    word net generator.
    """
    def __init__(self):
        """
        initialize local variables.
        该类对v1版本进行了改进，通过题干中的关键词和知识点中的关键词，匹配度高者，优先作为知识点候选
        该类仅对知识点中的关键词，包含在题干中，比较有效，对于题干中毫无知识点的感念，则无效
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

            # associate
            candidate_qklist_org = self.getAssociateQK_Origin(question_org)
            candidate_qklist_ext = self.getAssociateQK_Extension(question_ext)


            associatelist = []
            maxassociatelist = []
            maxcount = -1
            for candidate_k in candidate_qklist_org:
                count = candidate_k[1]
                if maxcount == -1:
                    maxcount = count
                elif maxcount > count:
                    break

                kname = candidate_k[0]
                maxassociatelist.append(kname)

                if candidate_qklist_ext.__contains__(kname):
                    associatelist.append(kname)

            # 如果没有交叉，则取最长的
            reslist = None
            if len(associatelist) > 0:
                reslist = associatelist
            else :
                reslist = maxassociatelist
            # print
            print '问题{0}:'.format(qindex)+line
            print '知识点:'+ ';'.join(reslist)
            print '\r\n'

    def getAssociateQK_Origin(self, question):
        qklist = []
        for k in self.knowledge.keys():
            klist = self.knowledge.get(k)
            length = len(klist)
            index = 0
            pointcount = 0
            for v in klist:
                if question.__contains__(v):
                    index = index + 1
                    pointcount = pointcount + 1

            tup = (k, pointcount)
            qklist.append(tup)

        # sort
        sortlist = sorted(qklist, cmp=lambda x,y:cmp(y[1], x[1]))
        return sortlist

    def getAssociateQK_Extension(self, question):
        qklist = {}
        for k in self.knowledge.keys():
            klist = self.knowledge.get(k)
            length = len(klist)
            index = 0
            for v in klist:
                if question.__contains__(v):
                    index = index + 1

            if length == index:
                qklist[k] = ''


        return qklist

if __name__ == "__main__":
    sr = AssociateQKByKeyword()
    #sr.generateCypher()
    sr.readKnowledgeList()
    sr.getQuestion()

    print 'split over'