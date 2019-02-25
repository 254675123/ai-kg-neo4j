# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_*  associate question and knowledge *_*

"""
import sys

from domain import CourseInfomation
from domain import ResultInfo
from tool.reader import SentenceReader
from tool.textvector import word_vector
from domain import FilePath
reload(sys)
sys.setdefaultencoding('utf-8')

class AssociateQKByKeyword:
    """
    word net generator.
    """
    def __init__(self, course_path_info):
        """
        initialize local variables.
        该类综合v2，v3的情况，形成的
        """
        self.sentenceparam = 0.4
        self.sentence = SentenceReader.SentenceReader()
        self.preprocessor = None
        self.doc_vec = word_vector.TextVector(course_path_info)
        self.course_path_info = course_path_info
        self.examquestion_info = None
        self.knowledge = {}
        self.knowledgeByCode = {}
        self.result_map = {}
        self.outputcontentlist = []
        self.bad_examquestion_list = None


    def readRegularKnowledgeList(self):
        if not FilePath.fileExist(self.course_path_info.courseware_knowledge_txt_filepath):
            return
        #words = open('./../data/79037-002_knowledge.txt', 'r')
        # zhongjicaiwukuaiji-auto-knowledge
        f = open(self.course_path_info.courseware_knowledge_txt_filepath, 'r')
        ids_lines = f.readlines()
        index = 0
        for line in ids_lines:
            index += 1
            if index == 1:
                continue
            line = line.strip('\n')
            line_k = line.split(' ')
            if len(line_k) < 2:
                continue

            line_k_code = line_k[0]
            line_k_word = line_k[1]
            line_k_word_key = line_k_word.replace(u"'", ".")
            #line_k_confidence = line_k[2]
            line_k_confidence = 100

            if self.knowledge.__contains__(line_k_word_key):
                continue
            words = self.sentence.splitSentenceCanRepeat(line_k_word)
            words = self.preprocessor.enlargeVipWords(words, line_k_word)
            tup = (words,line_k_confidence,line_k_code)
            self.knowledge[line_k_word_key] = tup
            tup = (line_k_word_key, line_k_confidence, line_k_code)
            self.knowledgeByCode[line_k_code] = tup

    def training(self):
        #self.doc_vec.train_input_course_file =
        self.doc_vec.knowledge = self.knowledge
        self.doc_vec.train()
        pass
    def predication(self):
        self.bad_examquestion_list = []
        self.course_score = CourseInfomation.CourseScore()
        self.course_score.initCourse(self.course_path_info.course)
        # match(n)-[:NEXT]-(m) where n.name in ['典型','金本位制','指','金币','本位'] return n,m
        if self.examquestion_info is None:
            return
        if not self.examquestion_info.examquestion_dict.__contains__(self.course_path_info.course):
            return
        exam_question_list = self.examquestion_info.examquestion_dict.get(self.course_path_info.course)
        qindex = 0
        question_knowledge_map = {}
        for exam_question in exam_question_list:
            #line = "物权的分类:从设立的角度对他物权再做分类，可把其分为（）。,用益物权和担保物权"
            k = exam_question.knowledge_list
            q = exam_question.getContentAndAnswer()
            question_knowledge_map[q] = k
            qindex = qindex + 1

            q_words = self.sentence.splitSentenceCanRepeat(q)
            # 从q中找重点词, 并放大重点词
            q_words = self.preprocessor.enlargeVipWords(q_words, q)
            if len(q_words) == 0:
                continue
            # 然后再遍历知识点
            index = 0
            res_list = []
            for k_key in self.knowledge.keys():
                k_tup = self.knowledge.get(k_key)
                k_words = k_tup[0]
                if len(k_words) == 0:
                    continue
                score = self.doc_vec.pred_similarity(q_words, k_words)
                res = ResultInfo.ResultInfo(index, score, k_tup[2], k_key)
                res_list.append(res)
                index += 1
            # 对列表按score降序排列
            res_list.sort(cmp=None,key=lambda x:x.score, reverse=True)
            # 取分值最高的几个，超过1%，的舍去，或者再限定具体数量，比如3个

            # 统计得分的情况
            self.computeScore(res_list)

            # 统计不超过50分的试题
            if self.badExamquestionStatistics(res_list) == True:
                self.bad_examquestion_list.append((exam_question, res_list[0:3]))

            # 获取上级 知识点
            #reslist = self.getParentKnowledge(reslist)
            # 格式化输出
            reslist, wordlist = self.formatOutput(res_list, k)
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


        # 计算正确率
        # 题目总数
        self.course_score.compute()


        ns = '试题总数：{}'.format(self.course_score.score_scope_total)
        self.outputcontentlist.append(ns + '\n')
        print ns

        ns = '比较靠谱数(60分以上)：{}  ，比较靠谱占比：{}%'.format(self.course_score.score_scope_more60_count, round(self.course_score.score_scope_more60_rate*100, 2))
        self.outputcontentlist.append(ns + '\n')
        print ns
        ns = '基本靠谱数(50-60分)：{}  ，基本靠谱占比：{}%'.format(self.course_score.score_scope_between5060_count, round(self.course_score.score_scope_between5060_rate*100, 2))
        self.outputcontentlist.append(ns + '\n')
        print ns
        ns = '不太靠谱数(40-50分)：{}  ，不太靠谱占比：{}%'.format(self.course_score.score_scope_between4050_count, round(self.course_score.score_scope_between4050_rate*100, 2))
        self.outputcontentlist.append(ns + '\n')
        print ns
        ns = '不靠谱数(40分以下)：{}  ，不靠谱占比：{}%'.format(self.course_score.score_scope_less40_count, round(self.course_score.score_scope_less40_rate*100, 2))
        self.outputcontentlist.append(ns + '\n')
        print ns

    def badExamquestionStatistics(self, res_list):
        flag = False
        if res_list is None:
            flag = True
            return flag

        for res in res_list:
            if res.score < 0.45:
                flag = True
            break
        return flag

    def predication1(self):
        self.course_score = CourseInfomation.CourseScore()
        self.course_score.initCourse(self.course_path_info.course)
        # match(n)-[:NEXT]-(m) where n.name in ['典型','金本位制','指','金币','本位'] return n,m
        if not FilePath.fileExist(self.course_path_info.examquestion_source_txt_filepath):
            return
        question = open(self.course_path_info.examquestion_source_txt_filepath, 'r')
        ids_lines = question.readlines()
        qindex = 0
        question_knowledge_map = {}


        for line in ids_lines:
            #line = "物权的分类:从设立的角度对他物权再做分类，可把其分为（）。,用益物权和担保物权"
            line = line.strip('\n')
            index = line.index('::')
            k = line[0:index]
            q = line[index+2:]
            question_knowledge_map[q] = k
            qindex = qindex + 1
            q_words = self.sentence.splitSentenceCanRepeat(q)
            # 从q中找重点词, 并放大重点词
            q_words = self.preprocessor.enlargeVipWords(q_words, q)
            if len(q_words) == 0:
                continue
            # 然后再遍历知识点
            index = 0
            res_list = []
            for k_key in self.knowledge.keys():
                k_tup = self.knowledge.get(k_key)
                k_words = k_tup[0]
                if len(k_words) == 0:
                    continue
                score = self.doc_vec.pred_similarity(q_words, k_words)
                res = ResultInfo.ResultInfo(index, score, k_tup[2] + ' ' + k_key)
                res_list.append(res)
                index += 1
            # 对列表按score降序排列
            res_list.sort(cmp=None,key=lambda x:x.score, reverse=True)
            # 取分值最高的几个，超过1%，的舍去，或者再限定具体数量，比如3个

            # 统计得分的情况
            self.computeScore(res_list)

            # 获取上级 知识点
            #reslist = self.getParentKnowledge(reslist)
            # 格式化输出
            reslist, wordlist = self.formatOutput(res_list, k)
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


        # 计算正确率
        # 题目总数
        self.course_score.compute()


        ns = '试题总数：{}'.format(self.course_score.score_scope_total)
        self.outputcontentlist.append(ns + '\n')
        print ns

        ns = '比较靠谱数(60分以上)：{}  ，比较靠谱占比：{}%'.format(self.course_score.score_scope_more60_count, round(self.course_score.score_scope_more60_rate*100, 2))
        self.outputcontentlist.append(ns + '\n')
        print ns
        ns = '基本靠谱数(50-60分)：{}  ，基本靠谱占比：{}%'.format(self.course_score.score_scope_between5060_count, round(self.course_score.score_scope_between5060_rate*100, 2))
        self.outputcontentlist.append(ns + '\n')
        print ns
        ns = '不太靠谱数(40-50分)：{}  ，不太靠谱占比：{}%'.format(self.course_score.score_scope_between4050_count, round(self.course_score.score_scope_between4050_rate*100, 2))
        self.outputcontentlist.append(ns + '\n')
        print ns
        ns = '不靠谱数(40分以下)：{}  ，不靠谱占比：{}%'.format(self.course_score.score_scope_less40_count, round(self.course_score.score_scope_less40_rate*100, 2))
        self.outputcontentlist.append(ns + '\n')
        print ns

    def subjectSimilarity(self):
        """
        判断2个短句的相似性
        :return: 
        """
        if not FilePath.fileExist(self.course_path_info.examquestion_source_txt_filepath):
            return
        question = open(self.course_path_info.examquestion_source_txt_filepath, 'r')
        ids_lines = question.readlines()
        qindex = 0
        question_map = {}
        processed_q_map = {}
        for line in ids_lines:
            line = line.strip('\n')
            index = line.index('::')
            k = line[0:index]
            q = line[index+2:]

            qindex = qindex + 1
            q_words = self.sentence.splitOneSentence(q)
            if len(q_words) == 0:
                continue
            # 然后再遍历知识点

            find_same_flag = False
            for old_q in question_map.keys():
                old_q_list = question_map.get(old_q)
                old_q_words = self.sentence.splitOneSentence(old_q)

                score = self.doc_vec.pred_similarity(q_words, old_q_words)
                if score > 0.95:
                    old_q_list.append(q)
                    find_same_flag = True
                    break
            if find_same_flag == False:
                question_map[q] = []

        # 过滤下，对于list是空的，不要管
        self.result_map = {}
        for q_key in question_map.keys():
            q_list = question_map.get(q_key)
            if len(q_list) > 0:
                self.result_map[q_key] = q_list



    def getParentKnowledge(self, orglist):
        reslist = []
        resdict = {}
        index = 0
        for k in orglist:
            k_name = k[0]
            k_code = k[1]
            index += 1


            if resdict.__contains__(k_code):
                continue

            resdict[k_code] = ''
            if not k_code.__contains__(u'.'):
                reslist.append(k)
                continue

            ridx = k_code.rindex(u'.')
            if ridx < 0:
                reslist.append(k)
                continue
            k_code_n = k_code[:ridx]
            if not self.knowledgeByCode.__contains__(k_code_n) or not k_code_n.__contains__(u'.'):
                reslist.append(k)
                continue

            k_parent = self.knowledgeByCode[k_code_n]
            if not resdict.__contains__(k_code_n):
                resdict[k_parent[2]] = ''
                k_parent_tup = (k_parent[0]+'--'+k[0], k[1], k[2], k[3])
                #reslist.append(k_parent_tup)
                reslist.append(k_parent_tup)

            if index > 3:
                break
        return reslist

    def formatOutput(self, inputlist, k):
        reslist = []
        wordlist = []
        index = 0
        for item in inputlist:
            ns = '{} (可信度：{})'.format(item.text, item.score)
            reslist.append(ns)
            wordlist.append(item.text)
            k.append(item)
            index += 1
            if index > 3:
                break
        return reslist, wordlist

    def computeScore(self, inputlist):
        """
        统计各个阶段的数量
        :param inputlist: 
        :return: 
        """
        for item in inputlist:
            if item.score >= 0.6:
                self.course_score.score_scope_more60_count += 1
            elif item.score >= 0.5:
                self.course_score.score_scope_between5060_count += 1
            elif item.score >= 0.4:
                self.course_score.score_scope_between4050_count += 1
            else:
                self.course_score.score_scope_less40_count += 1

            break


    def outputResult(self):
        fout = open(self.course_path_info.correlation_txt_filepath, 'w')  # 以写得方式打开文件
        fout.writelines(self.outputcontentlist)  # 将分词好的结果写入到输出文件

        for same_q in self.result_map:
            q_list = self.result_map.get(same_q)
            line = '{} -- 重复题数量：{}'.format(same_q, len(q_list))
            fout.write(line + '\n')
        fout.close()

    def executeAssociate(self):
        self.readRegularKnowledgeList()
        self.training()
        self.predication()
        # 对比试题的相似性
        #self.subjectSimilarity()
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
    sr.predication()
    sr.outputResult()

    # 对比

    print 'split over'