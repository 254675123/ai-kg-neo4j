# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_* word net generate *_*

"""

import sys

from database import Neo4jHandler
from tool.reader import SentenceReader
from tool.splitor import HanlpSplitor

reload(sys)
sys.setdefaultencoding('utf-8')
class Characternet:
    """
    CHAR net generator.
    merge (c1:CHAR {name:'国'}) 
    merge (c2:CHAR {name:'家'})
    merge (c1)-[r:NEXT]-(c2) 
    on create set r.weight = 1
    on match set r.weight = r.weight + 1
    return c1, c2
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)
        self.sentence = SentenceReader.SentenceReader()
        self.splitor = HanlpSplitor.HanlpSplitor()
        #self.cypherlist = []
        self.sentcypherlist = []
        #self.cypherlist.append("CREATE CONSTRAINT ON (c:WORD) ASSERT c.name IS UNIQUE;")

    def generateNode(self):
        # 创建约束
        self.neo4jdriver.cypherexecuter("CREATE CONSTRAINT ON (c:CHAR) ASSERT c.name IS UNIQUE;")
        sentencecount = 0
        for cypherstatement in self.generateCypher():
            sentencecount = sentencecount + 1
            print 'sentence index : ' + str(sentencecount)
            print cypherstatement
            self.neo4jdriver.cypherexecuter(cypherstatement)
            print 'push one sentence over.'

        print 'push over.'

    def generateCypher(self):
        """
        generate cypher statement
        :return: 
        """
        for sentence in self.sentence.getSentence('./../data/financial-course.txt'):
            length = len(sentence)
            if length == 0:
                continue
            self.sentcypherlist = []
            index = 1
            for char in sentence:
                #print char
                ns = "merge (c{0}:CHAR {{name:'{1}'}})".format(index,char)
                self.sentcypherlist.append(ns)
                index = index + 1
            index = 1
            while index < length:
                rel = str(index) + str(index+1)
                ns = "merge (c{0})-[r{2}:NEXT]-(c{1})".format(index, index+1,rel)
                self.sentcypherlist.append(ns)
                ns = "on create set r{0}.weight = 1".format(rel)
                self.sentcypherlist.append(ns)
                ns = "on match set r{0}.weight = r{0}.weight + 1".format(rel)
                self.sentcypherlist.append(ns)
                index = index + 1

            # 合并cypher
            cypherstatement = '\r\n'.join(self.sentcypherlist) + ';'
            yield cypherstatement
            #self.cypherlist.append(cypherstatement)


    def createRelationLayerInner(self, poslist,index):
        """
        同层概念之间建立关系
        :param poslist: 
        :param index: 
        :return: 
        """
        poslength = len(poslist)
        seq = str(index)
        cypher = []
        if poslength > 1:
            posindex = 0

            while posindex < poslength:
                # create node cypher
                nseq = seq + str(posindex)
                wns = "MERGE (w{0}:WORD {{name: '{1}'}})".format(nseq,poslist[posindex])
                cypher.append(wns)
                posindex = posindex + 1

            posindex = 0
            while posindex < poslength - 1:
                # create relation cypher
                subposlist = poslist[posindex:]
                subposindex = 1
                sublength = len(subposlist)
                while subposindex < sublength:
                    start_seq = seq + str(posindex)
                    end_seq = seq + str(posindex + subposindex)
                    rns = "MERGE (w{0})-[:NEXT]->(w{1})".format(start_seq, end_seq)
                    cypher.append(rns)
                    subposindex = subposindex + 1
                posindex = posindex + 1
        else:
            nseq = seq + str(0)
            wns = "MERGE (w{0}:WORD {{name: '{1}'}})".format(nseq,poslist[0])
            cypher.append(wns)

        cypherstatement = '\r\n'.join(cypher)
        self.sentcypherlist.append(cypherstatement)

    def createRelationLayerOuter(self, poslist, nextposlist,index):
        pre_seq = str(index)
        aft_seq = str(index + 1)
        pre_length = len(poslist)
        aft_length = len(nextposlist)
        pre_index = 0
        cypher = []
        # 2层循环
        while pre_index < pre_length:
            start_seq = pre_seq + str(pre_index)
            pre_index = pre_index + 1

            aft_index = 0
            while aft_index < aft_length:
                end_seq = aft_seq + str(aft_index)
                rns = "MERGE (w{0})-[:NEXT]->(w{1})".format(start_seq, end_seq)
                cypher.append(rns)
                aft_index = aft_index + 1

        if len(cypher) > 0:
            cypherstatement = '\r\n'.join(cypher)
            self.sentcypherlist.append(cypherstatement)

if __name__ == "__main__":
    sr = Characternet()
    #sr.generateCypher()
    sr.generateNode()
    print 'split over'