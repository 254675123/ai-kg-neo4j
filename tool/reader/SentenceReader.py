# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_* sentence reader  *_*

"""
import re
import sys
import os
from tool.splitor import HanlpSplitor
from tool.convertor import UnicodeConvertor
reload(sys)
sys.setdefaultencoding('utf-8')

class SentenceReader:
    """
    read sentence one by one.
    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.__curpath = os.path.dirname(os.path.realpath(__file__))
        #self.jiebasplitor = JiebaSplitor.JiebaSplitor()
        self.hanlpsplitor = HanlpSplitor.HanlpSplitor()
        self.wordlist = []

        self.stopwords = {}
        fstop = open(self.__curpath+'/../../data/dictionary/stopwords-pre-v20180817.txt', 'r')
        for eachWord in fstop:
            self.stopwords[eachWord.strip().decode('utf-8', 'ignore')] = eachWord.strip().decode('utf-8', 'ignore')
        fstop.close()

    def getSentence(self, filepath):
        fin = open(filepath, 'r')  # 以读的方式打开文件
        for eachLine in fin:
            line = eachLine.strip().decode('utf-8', 'ignore')  # 去除每行首尾可能出现的空格，并转为Unicode进行处理
            #line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+".decode("utf8"),
            #               ",".decode("utf8"), line)
            line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:：“”。？~@#￥%……&*（）]+".decode("utf8"),
                           ",".decode("utf8"), line)
            sublinearray = line1.split(',')
            for subline in sublinearray:
                if subline.strip() == '':
                    continue
                yield subline

        fin.close()
    def splitOneSentence(self, sentence):
        res_list = []
        wordList = self.hanlpsplitor.split1list(sentence)
        for word in wordList:
            if self.stopwords.__contains__(word):
                continue
            word = word.strip()
            if len(word) == 0:
                continue
            if self.isChineseSign(word) == False:
                continue
            res_list.append(word)

        return res_list

    def splitSentenceCanRepeat(self, sentence):
        res_list = []
        wordList = self.hanlpsplitor.splitlist_can_repeat(sentence)
        for word in wordList:
            if self.stopwords.__contains__(word):
                continue
            word = word.strip()
            if len(word) == 0:
                continue
            if self.isChineseSign(word) == False:
                continue
            res_list.append(word)

        return res_list

    def isChineseSign(self, word):
        flag = True
        if word is None:
            return flag

        for ch in word:
            flag = UnicodeConvertor.is_chinese(ch)
            if flag == False:
                break

        return flag


    def splitSentence(self,inputFile):
        # 把停用词做成字典

        fin = open(inputFile, 'r')  # 以读的方式打开文件

        #jieba.enable_parallel(4)  # 并行分词
        #jieba.enable_parallel()

        for eachLine in fin:
            res_list = []
            wordList = self.hanlpsplitor.split1list(eachLine)
            for word in wordList:
                if self.stopwords.__contains__(word):
                    continue

                word = word.strip()
                if len(word) == 0:
                    continue

                res_list.append(word)

            yield res_list

        fin.close()
        # fout = open('./../data/words-jieba-plit.txt', 'w')  # 以写得方式打开文件
        # fout.write('\n'.join(self.jiebasplitor.wordposlist))  # 将分词好的结果写入到输出文件
        # fout.close()
        #
        # fout = open('./../data/words-hanlp-plit.txt', 'w')  # 以写得方式打开文件
        # fout.write('\n'.join(self.hanlpsplitor.wordposlist))  # 将分词好的结果写入到输出文件
        # fout.close()



if __name__ == "__main__":
    sr = SentenceReader()
    #sr.splitSentence('./../data/financial-course.txt')
    sen = u'个人自学结合在一起的教学组织形式是() 答案： 特朗普制'
    res = sr.splitOneSentence(sen)
    for word in res:
        word1 = word.split()
        for ch in word:
            res = UnicodeConvertor.is_chinese(ch)
            print res

    print res
    res = sr.splitSentenceCanRepeat(sen)
    print 'split over'