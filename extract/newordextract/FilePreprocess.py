# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-08-15
program       : *_* sentence reader  *_*

"""
import re
import os
import sys

from tool.convertor import UnicodeConvertor

reload(sys)
sys.setdefaultencoding('utf-8')

class FilePreprocess:
    """
    read sentence one by one.
    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.__curpath = os.path.dirname(os.path.realpath(__file__))
        # 标点符号与数字集，用于分割句子
        self.__splitwords = "[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:：“”。？~@#￥%……&*（）]+"
        self.__pattern = r'(第[一二三四五六七八九十零0123456789]+章)|(第[一二三四五六七八九十零0123456789]+节)|(附录[一二三四五六七八九十]*)'
        # 统计词得总数
        self.wordcount = 0
        # 句子在文中得权重，正文为1，标题为25
        self.__defaultweight = 25
        self.quoteweight = 5
        self.sentenceweight = 1
        # 把停用词做成字典
        self.stopwords = {}
        self.stopwordlist = []
        # 把包含词也做成字典
        self.inludewords = {}
        # 遍历句子中，使用双引号强调的词
        self.quotewords = {}
        # 辅组词词典，该辅助词不能作为知识点
        self.auxiliarywords = {}
        # initialize
        self.__initStopwords__()
        self.__initIncludewords__()
        self.__initAuxiliarywords__()

    def __initStopwords__(self):
        fstop = open(self.__curpath+'/../data/dictionary/stopwords-pre-v20180817.txt', 'r')
        for eachWord in fstop:
            eachWord = eachWord.strip()
            eachWord = eachWord.decode('utf-8', 'ignore')
            length = len(eachWord)
            tup = (eachWord, length)
            self.stopwordlist.append(tup)
            self.stopwords[eachWord] = eachWord
        fstop.close()

        self.stopwordlist = sorted(self.stopwordlist, cmp=lambda x, y: cmp(y[1], x[1]))

    def __initIncludewords__(self):
        fwords = open(self.__curpath+'/../data/dictionary/includewords-pre-v20180824.txt', 'r')
        for eachWord in fwords:
            eachWord = eachWord.strip()
            eachWord = eachWord.decode('utf-8', 'ignore')
            self.inludewords[eachWord] = eachWord
        fwords.close()

    def __initAuxiliarywords__(self):
        fwords = open(self.__curpath+'/../data/dictionary/auxiliary-pre-20180829.txt', 'r')
        for eachWord in fwords:
            eachWord = eachWord.strip()
            eachWord = eachWord.decode('utf-8', 'ignore')
            self.auxiliarywords[eachWord] = eachWord
        fwords.close()

    def getSentence(self, filepath):
        linecount = 0
        fin = open(filepath, 'r')  # 以读的方式打开文件
        for eachLine in fin:
            stripline = eachLine.strip()
            linecount = linecount + 1
            # 首先判断是否是章节句子
            se = re.findall(self.__pattern, stripline)
            firststart = False
            if len(se) == 1 and (stripline.startswith('第') or stripline.startswith('附录')):
                firststart = True
            # 去除数字和标点符号，统一替换为英文逗号
            # 去除每行首尾可能出现的空格，并转为Unicode进行处理

            line = stripline.decode('utf-8', 'ignore')
            self.getQuoteWords(line)
            line1 = re.sub(self.__splitwords.decode("utf8"), ",".decode("utf8"), line)

            if firststart and len(line1) < 30:
                self.sentenceweight = self.__defaultweight
            else:
                self.sentenceweight = 1
            print 'has processed line count:' + str(linecount)

            # 是否包含不能去掉得词，如果包含，该句子不做去除停用词
            incwords = self.getIncludewords(line1)
            line2 = self.removeStopwords(line1, incwords)
            sublinearray = line2.split(',')
            for subline in sublinearray:
                if subline.strip() == '':
                    continue

                self.wordcount = self.wordcount + len(subline)
                yield subline

        fin.close()


    def getIncludewords(self, sentence):
        """
        判断句子中是否包含不能去掉得词，如果包含，则返回true
        :param sentence: 
        :return: 
        """
        incwords = []
        if len(sentence.strip()) == 0:
            return incwords
        for word in self.inludewords:
            if str(sentence).__contains__(word):
                incwords.append(word)
        return incwords

    def removeStopwords(self, sentence, incwords):
        if len(sentence.strip()) == 0:
            return ''

        #nline = []
        # 单个字的停用，但对于停用词无效
        #for char in sentence:
        #    if self.stopwords.__contains__(char):
        #        nline.append(',')
        #    else:
        #        nline.append(char)

        #line2 = ''.join(nline)

        # 应该是用停用词，去句子中找，如果找到，则替换掉
        if len(incwords) > 0:
            for stopword in self.stopwordlist:
                canremove = True
                for incword in incwords:
                    if str(incword).__contains__(stopword[0]):
                        canremove = False
                        sentence = sentence.replace(incword, '*')
                        sentence = sentence.replace(stopword[0], ',')
                        sentence = sentence.replace('*', incword)
                if canremove == True:
                    sentence = sentence.replace(stopword[0], ',')
        else:
            for stopword in self.stopwordlist:
                sentence = sentence.replace(stopword[0], ',')

        return sentence

    def getQuoteWords(self, sentence):
        """
        获取句子中，使用双引号强调的词
        :param sentence: 
        :return: 
        """
        start = False
        end = False
        tempword = []
        for ch in sentence:
            if ch == '“':
                start = True
                continue
            if ch == '”' and start == True:
                start = False
                if len(tempword) == 1:
                    tempword = []
                    continue

                word = ''.join(tempword)
                # 如果是辅助词，则不要
                if self.auxiliarywords.__contains__(word):
                    continue

                if self.quotewords.__contains__(word):
                    self.quotewords[word] = self.quotewords[word] + self.quoteweight
                else:
                    self.quotewords[word] = self.quoteweight

                tempword = []
                continue
            if start == True:
                if self.isChinese(ch):
                    tempword.append(ch)
                else:
                    start = False
                    tempword = []

    def isChinese(self, ch):
        res = False
        s_unicode = UnicodeConvertor.stringToUnicode(ch)
        if s_unicode >= u'\\u4e00' and s_unicode <= u'\\u9fa5':
            res = True
        return  res

if __name__ == "__main__":
    #sr = FilePreprocess()
    #sr.splitSentence('./../data/financial-course.txt')
    #for sentence in sr.getSentence('./../data/financial-course.txt'):
    #    print sentence
    sentence = '第二十一2节 税收得概念第五章第二版'
    se = re.findall(r'(第[一二三四五六七八九十零0123456789]+章)|(第[一二三四五六七八九十零0123456789]+节)', sentence)
    if se :
        print se.count()


    print 'split over'