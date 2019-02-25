
# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_* jie ba  *_*

"""


import jieba                                          #导入jieba模块
import re
#jieba.load_userdict("./../data/newdict.txt")                     #加载自定义词典
jieba.load_userdict("./../../dictionary/data/newdict.txt")                     #加载自定义词典

import jieba.posseg as pseg

class JiebaSplitor:
    """
    jie ba splitor
    """
    def __init__(self):

        self.wordnetlist = []
        self.wordposlist = []
        # 把停用词做成字典
        self.stopwords = {}
        fstop = open('./../data/stopwords.txt', 'r')
        for eachWord in fstop:
            self.stopwords[eachWord.strip().decode('utf-8', 'ignore')] = eachWord.strip().decode('utf-8', 'ignore')
        fstop.close()

    def split1list(self, sentence):
        line = sentence.strip().decode('utf-8', 'ignore')  # 去除每行首尾可能出现的空格，并转为Unicode进行处理
        line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+".decode("utf8"),
                       " ".decode("utf8"), line)
        #wordList = list(jieba.cut(line1))  # 用结巴分词，对每行内容进行分词
        wordList = pseg.cut(line1)
        poslist = []
        for w in wordList:
            length = len(w.word)
            if length < 2:
                continue
            if w.word in self.stopwords:
                preflag = None
                continue

            if self.isFormWord(w):
                continue

            poslist.append(w.word)


        return poslist

    def split(self, sentence):
        line = sentence.strip().decode('utf-8', 'ignore')  # 去除每行首尾可能出现的空格，并转为Unicode进行处理
        line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+".decode("utf8"),
                       " ".decode("utf8"), line)
        #wordList = list(jieba.cut(line1))  # 用结巴分词，对每行内容进行分词
        wordList = pseg.cut(line1)

        #
        self.process(wordList)
        return self.wordnetlist

    def process(self, wordList):
        self.wordnetlist = []
        preflag = None
        poslist = []
        for w in wordList:
            length = len(w.word)
            if length < 2:
                continue
            if w.word in self.stopwords:
                preflag = None
                continue

            if self.isFormWord(w):
                continue

            wordpos =  w.word + '   ' + w.flag
            self.wordposlist.append(wordpos)

            if w.flag == preflag:
                poslist.append(w.word)
            else:
                if len(poslist) > 0:
                    self.wordnetlist.append(poslist)
                    poslist = []

                poslist.append(w.word)
                preflag = w.flag

        if len(poslist) > 0:
            self.wordnetlist.append(poslist)

    def isFormWord(self, w):
        flag = False

        if w.flag == 'c' or w.flag == 'e' or w.flag == 'f' or w.flag == 'h' or w.flag == 'p' or w.flag == 't':
            flag = True

        if w.flag == 'r' or w.flag == 'm' or str(w.flag).__contains__('d'):
            flag = True

        return flag

if __name__ == "__main__":
    sr = JiebaSplitor()
    #sr.split1list('国际收支账户')
    #账户是国际收支平衡表中最基本的往来账户
    #sr.split1list('账户是国际收支平衡表中最基本的往来账户')
    sr.split1list('外汇管制的作用')
    print 'split over'