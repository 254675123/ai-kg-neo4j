# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_*  associate question and knowledge *_*

"""
import math
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
        该类综合v2，v3的情况，形成的
        """
        self.sentenceparam = 0.4
        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)
        self.sentence = SentenceReader.SentenceReader()
        #self.splitor = JiebaSplitor.JiebaSplitor()
        self.splitor = HanlpSplitor.HanlpSplitor()
        #self.cypherlist = []
        self.sentcypherlist = []
        #self.cypherlist.append("CREATE CONSTRAINT ON (c:WORD) ASSERT c.name IS UNIQUE;")

        self.knowledgefilepath = None
        self.questionfilepath = None
        self.outputfilepath = None
        self.knowledge = {}

        self.outputcontentlist = []

    def readKnowledgeList(self):
        words = open('./../data/minfa-knowledge.txt', 'r')
        ids_lines = words.readlines()
        for line in ids_lines:
            line = line.strip('\n')
            if self.knowledge.__contains__(line):
                continue
            words = self.splitor.split1list(line)
            self.knowledge[line] = words

    def readRegularKnowledgeList(self):
        if self.knowledgefilepath == '':
            return
        #words = open('./../data/79037-002_knowledge.txt', 'r')
        # zhongjicaiwukuaiji-auto-knowledge
        f = open(self.knowledgefilepath, 'r')
        ids_lines = f.readlines()
        for line in ids_lines:
            line = line.strip('\n')
            line_k = line.split(' ')
            line_k_code = line_k[0]
            line_k_word = line_k[1]
            #line_k_confidence = line_k[2]
            line_k_confidence = 100

            if self.knowledge.__contains__(line_k_word):
                continue
            words = self.splitor.split1list(line_k_word)
            self.knowledge[line_k_word] = (words,line_k_confidence,line_k_code)

    def getQuestion(self):
        # match(n)-[:NEXT]-(m) where n.name in ['典型','金本位制','指','金币','本位'] return n,m
        question = open(self.questionfilepath, 'r')
        ids_lines = question.readlines()
        qindex = 0
        question_knowledge = {}
        correct_count = 0
        for line in ids_lines:
            #line = "物权的分类:从设立的角度对他物权再做分类，可把其分为（）。,用益物权和担保物权"
            line = line.strip('\n')
            index = line.index(':')
            k = line[0:index]
            q = line[index+1:]
            question_knowledge[q] = k
            qindex = qindex + 1
            question_org = {}
            question_ext = {}
            words = self.splitor.split1list(q)
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
            candidate_qklist_full = self.getAssociateQK_FullContains(q)
            if len(candidate_qklist_full) == 0:
                candidate_qklist_part_word = self.getAssociateQK_PartWordContains(question_org, q)
                candidate_qklist_part_char = [] if len(candidate_qklist_part_word) > 0 else self.getAssociateQK_PartCharacterContains(question_org)
                candidate_qklist_none = self.getAssociateQK_NoContains(question_ext)

                reslist = None
                if len(candidate_qklist_part_word) > 0:
                    reslist = self.getAssociateQK_Keyword(candidate_qklist_part_word, candidate_qklist_none)
                elif len(candidate_qklist_part_char) > 0:
                    reslist = self.getAssociateQK_Keyword(candidate_qklist_part_char, candidate_qklist_none)
                else:
                    reslist = self.getAssociateQK_Weight(question_org, question_ext)
            else :
                reslist = candidate_qklist_full

            # 格式化输出
            reslist, wordlist = self.formatOutput(reslist)
            # 统计正确率
            if len(reslist) > 0:
                ns = '问题{0}:'.format(qindex) + q
                self.outputcontentlist.append(ns + '\n')
                ns = '电脑标识知识点:' + ';'.join(wordlist)
                self.outputcontentlist.append(ns + '\n')
                ns = '知识点评估指标:' + ';'.join(reslist)
                self.outputcontentlist.append(ns + '\n')
                #print '老师标识知识点:' + k
                ns = '老师标识知识点:'
                self.outputcontentlist.append(ns + '\n')
                self.outputcontentlist.append('\n')
                #ns = '电脑标识是否正确:'
                #self.outputcontentlist.append(ns)

                #if reslist[0] == k:
                #    correct_count = correct_count + 1
                    #print '正确'
                #elif str(k).startswith(reslist[0]):
                #    correct_count = correct_count + 1
                    #print '正确'
                #else:
                    #print '错误'
                #    pass
                #print '\r\n'
        # 计算正确率
        correct_rate = float(correct_count) / len(question_knowledge)
        print '正确数：' + str(correct_count)
        print '总数：' + str(len(question_knowledge))
        print '正确率：' + str(correct_rate)

    def formatOutput(self, inputlist):
        reslist = []
        wordlist = []
        for item in inputlist:
            ns = '{0}(得分：{1}，可信度：{2})'.format(item[0],round(item[1],2),item[2])
            reslist.append(ns)
            wordlist.append(item[0])

        return reslist, wordlist

    def getAssociateQK_Weight(self, question_org, question_ext):
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

        qklist = []
        for k in self.knowledge.keys():
            klist = self.knowledge.get(k)[0]
            length = len(klist)
            index = 0
            weight = 0.0
            for v in klist:
                if question_ext.__contains__(v):
                    index = index + 1
                    weight = weight + float(question_ext[v]) / maxcount

            tup = (k, weight,50.0)
            qklist.append(tup)

        # sort
        sortlist = sorted(qklist, cmp=lambda x, y: cmp(y[1], x[1]))

        #reslist = []
        #for item in sortlist:
        #    reslist.append(item)

        return sortlist

    def getAssociateQK_Keyword(self, candidate_qklist_org, candidate_qklist_ext):
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
            maxassociatelist.append(candidate_k)

            if candidate_qklist_ext.__contains__(kname):
                associatelist.append(candidate_k)

        # 如果没有交叉，则取最长的
        reslist = None
        if len(associatelist) > 0:
            reslist = associatelist
        else:
            reslist = maxassociatelist
            # print
        return  reslist
    def getAssociateQK_PartWordContains(self, question, q):
        qklist = []
        for k in self.knowledge.keys():
            klist = self.knowledge.get(k)[0]
            length = len(klist)
            index = 0
            pointcount = 0.0
            distance = 0
            prelocation = 0
            for v in klist:
                if question.__contains__(v):
                    location = q.index(v)
                    if index == 0:
                        prelocation = location
                    else:
                        distance = distance + math.fabs(location - prelocation)
                    index = index + 1
                    pointcount = pointcount + 1
            if pointcount > 0:
                pointcount = pointcount + 3.0 / len(k)
                tup = (k, pointcount, 65.0)
                qklist.append(tup)

        # sort
        sortlist = sorted(qklist, cmp=lambda x,y:cmp(y[1], x[1]))
        return sortlist

    def getAssociateQK_PartCharacterContains(self, question):
        qklist = []
        for k in self.knowledge.keys():
            k1 = k.decode('utf-8')
            length = len(k1)
            index = 0
            pointcount = 0.0
            for v in k1:
                for qkey in question.keys():
                    if qkey.__contains__(v):
                        index = index + 1
                        pointcount = pointcount + 1
                        break

            if pointcount > 0:
                pointcount = pointcount + 1.0 / len(k1)
                tup = (k, pointcount, 60.0)
                qklist.append(tup)

        # sort
        sortlist = sorted(qklist, cmp=lambda x,y:cmp(y[1], x[1]))
        return sortlist

    def getAssociateQK_NoContains(self, question):
        qklist = {}
        for k in self.knowledge.keys():
            klist = self.knowledge.get(k)[0]
            length = len(klist)
            index = 0
            for v in klist:
                if question.__contains__(v):
                    index = index + 1

            if length == index:
                qklist[k] = ''


        return qklist

    def getAssociateQK_FullContains(self, q):
        qklist = []
        q = str(q)
        q_length = len(q)
        for k in self.knowledge.keys():
            k_q_c = '“' + k +'”'
            k_q_e = '"' + k +'"'
            k_length = len(k)
            if q.__contains__(k_q_c):
                index = q.find(k)
                location = self.sentenceparam + float(index + 1)/q_length
                score = (k_length + 100.0) / location
                tup = (k, score, 100.0)
                qklist.append(tup)
            elif q.__contains__(k_q_e):
                index = q.find(k)
                location = self.sentenceparam + float(index + 1) / q_length
                score = (k_length + 100.0) / location
                tup = (k, score, 100.0)
                qklist.append(tup)
            elif q.__contains__(k):
                index = q.find(k)
                location = self.sentenceparam + float(index + 1) / q_length
                score = (k_length + 1.0) / location
                tup = (k, score, 90.0)
                qklist.append(tup)

        # sort
        sortlist = sorted(qklist, cmp=lambda x, y: cmp(y[1], x[1]))
        reslist = []
        max_score = -1.0
        length = 3
        for item in sortlist:
            if max_score < 0:
                max_score = item[1]
                reslist.append(item)
            elif length > len(reslist):
                reslist.append(item)
            elif max_score > item[1]:
                break

        # 去重
        reslist = self.resultFilter(reslist)
        return reslist

    def resultFilter(self, reslist_orig):
        reslist = []
        for item1 in reslist_orig:
            length1 = len(item1[0])
            exist = False
            for item2 in reslist_orig:
                length2 = len(item2[0])
                if length1 == length2 and item1[0] == item2[0]:
                    continue
                elif str(item2[0]).__contains__(item1[0]):
                    exist = True
                    break
            # 如果包含了，就不要该项
            if exist == False:
                reslist.append(item1)

        return reslist

    def outputResult(self):
        fout = open(self.outputfilepath, 'w')  # 以写得方式打开文件
        fout.writelines(self.outputcontentlist)  # 将分词好的结果写入到输出文件
        fout.close()

    def executeAssociate(self):
        self.readRegularKnowledgeList()
        self.getQuestion()
        self.outputResult()
        print 'associate question and knowledge over.'

if __name__ == "__main__":
    sr = AssociateQKByKeyword()
    sr.knowledgefilepath = u'./../data/zhongjicaiwukuaiji-auto-knowledge.txt'
    sr.questionfilepath = u'./../data/course-question-tgt/0701-test.txt'
    sr.outputfilepath = u'./../data/course-question-tgt/0701-result.txt'
    #sr.generateCypher()
    #sr.readKnowledgeList()
    sr.readRegularKnowledgeList()
    sr.getQuestion()
    sr.outputResult()
    print 'split over'