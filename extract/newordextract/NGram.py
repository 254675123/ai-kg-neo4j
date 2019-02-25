# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-08-15
program       : *_* sentence reader  *_*

"""
import math
import sys

import FilePreprocess
from tool.splitor import HanlpSplitor

reload(sys)
sys.setdefaultencoding('utf-8')

class NGram:
    """
    read sentence one by one.
    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.minlength = 4
        self.maxlength = 7
        self.inputfile = None
        self.outputfile = None
        self.maxComputefreq = 15
        self.maxOutputfreq = 20
        self.titlewords = {}
        self.candicatewords = {}
        self.wordfreq = {}
        self.maybewords = {}
        self.realwords = {}

        # merge fail dict
        self.mergefaildict = {}

        self.outputwordsdict = {}
        self.outputwordslist = []

        self.fp = FilePreprocess.FilePreprocess()

        self.splitor = HanlpSplitor.HanlpSplitor()

    def generateCandidateword(self):

        for sentence in self.fp.getSentence(self.inputfile):
            length = len(sentence)
            self.processTitleWords(sentence)
            self.computeWordFrequence(sentence)
            if length < self.minlength:
                continue

            self.setNgramDict(sentence, length)

            print 'candidate dict length :' + str(self.candicatewords.__len__())


    def setNgramDict(self, sentence, length):
        wordlength = self.minlength
        if wordlength == length:
            self.setNgramDict_sub(sentence)
            return

        while wordlength < length and wordlength <= self.maxlength:

            for i in range(length - wordlength + 1):
                candidateword = sentence[i:wordlength + i]
                # 左邻词
                leftword = ''
                if i > 0:
                    leftword = sentence[i - 1:i]
                # 右邻词
                rightword = ''
                if (wordlength + i + 1) <= length:
                    rightword = sentence[wordlength + i:wordlength + i + 1]

                i = i + 1

                self.setNgramDict_sub(candidateword, leftword, rightword)

            wordlength = wordlength + 1

        if wordlength == length:
            self.setNgramDict_sub(sentence)
            return

    def setNgramDict_sub(self, candidateword, leftword='', rightword=''):
        leftweight = 1
        rightweight = 1
        if leftword == '':
            leftweight = self.fp.sentenceweight
        if rightword == '':
            rightweight = self.fp.sentenceweight

        if self.candicatewords.__contains__(candidateword):
            temp_worddict = self.candicatewords[candidateword]
            if temp_worddict.__contains__(leftword):
                temp_worddict[leftword] = temp_worddict[leftword] + leftweight
            else:
                temp_worddict[leftword] = leftweight

            if temp_worddict.__contains__(rightword):
                temp_worddict[rightword] = temp_worddict[rightword] + rightweight
            else:
                temp_worddict[rightword] = rightweight


            temp_worddict['count'] = temp_worddict['count'] + self.fp.sentenceweight
        else:
            temp_worddict = {}
            temp_worddict[leftword] = leftweight
            temp_worddict[rightword] = rightweight

            temp_worddict['count'] = self.fp.sentenceweight
            self.candicatewords[candidateword] = temp_worddict


    def processTitleWords(self, word):
        if self.fp.sentenceweight == 1 or len(word) == 1 :
            return
        #如果是停用词，不要
        if self.fp.stopwords.__contains__(word):
            return

        if self.titlewords.__contains__(word):
            self.titlewords[word] = self.titlewords[word] + 1
        else:
            self.titlewords[word] = 1

    def computeWordFrequence(self, sentence):
        wordlist = self.splitor.split_origin(sentence)
        if len(wordlist) == 0:
            return

        for word in wordlist:
            if self.wordfreq.__contains__(word):
                self.wordfreq[word] = self.wordfreq[word] + self.fp.sentenceweight
            else:
                self.wordfreq[word] = self.fp.sentenceweight

    def computeAggregation(self):
        # 遍历所有的候选词，计算凝固度
        chartotalcount = self.fp.wordcount
        for candidateword in self.candicatewords.keys():
            candidatedict = self.candicatewords[candidateword]
            candidatecount = candidatedict['count']
            candidatelength = len(candidateword)
            if candidatecount < self.maxComputefreq:
                continue
            #if  candidatelength >= 6 and candidatecount < self.maxfreq2nd:
            #    continue
            #elif candidatelength < 6 and candidatecount < self.maxfreq:
            #    continue

            candidaterate = float(candidatecount) / chartotalcount
            # 对候选词，用分词器做分词，做基本的分割
            splitwordlist = self.splitor.split_origin(candidateword)
            if len(splitwordlist) == 1:
                candidatedict['aggregation'] = 1000.0
                candidatedict['confidence'] = 90.0
                self.maybewords[candidateword] = candidatedict
                #print  '候选词：'+candidateword + '  ' + str(1000.0)
                continue

            isword = True
            splitwordrate = 1.0
            for splitword in splitwordlist:
                splitcount = 1
                if self.wordfreq.__contains__(splitword):
                    splitcount = self.wordfreq[splitword]
                else:
                    # 这不是个词，不要
                    isword = False
                    break
                charrate = float(splitcount) / chartotalcount
                splitwordrate = splitwordrate * charrate

            # 凝固度
            if isword == True:
                aggragaterate = candidaterate / splitwordrate
                candidatedict['aggregation'] = aggragaterate
                self.maybewords[candidateword] = candidatedict

                #print '候选词：'+candidateword + '  ' + str(aggragaterate)

                # 计算词的可信度，如果凝固度小于等于1000，设置可信度为50%，大于1000，可信度从50%递减到10%
                if aggragaterate <= 1000.0 :
                    confidence = 50.0
                else:
                    confidence = 10 + 100/(aggragaterate - 990)
                candidatedict['confidence'] = confidence

    def computeFreedom(self):
        # 遍历所有的候选词，计算自由度
        chartotalcount = self.fp.wordcount
        for candidateword in self.candicatewords.keys():
            candidatedict = self.candicatewords[candidateword]
            candidatecount = candidatedict['count']

            candidatelength = len(candidateword)
            if candidatecount < self.maxComputefreq:
                continue
            #if  candidatelength >= 6 and candidatecount < self.maxfreq2nd:
            #    continue
            #elif candidatelength < 6 and candidatecount < self.maxfreq:
            #    continue

            totalcount = 0
            emptycount = 0
            wordcount = 0
            fenzilist = []
            for leftrightword in candidatedict.keys():
                if leftrightword == 'count':
                    wordcount = candidatedict[leftrightword]
                    continue
                if leftrightword == 'aggregation':
                    continue
                if leftrightword == 'confidence':
                    continue

                fenzi = candidatedict[leftrightword]
                if leftrightword == '':
                    emptycount = fenzi
                else:
                    fenzilist.append(fenzi)
                    totalcount = totalcount + fenzi


            # 做对数运算，求信息熵
            entropy = 0.0
            wordcount_plus = wordcount * 0.5
            wordcount_max = wordcount + wordcount_plus
            fenzilength = len(fenzilist)
            if fenzilength == 0 or (float(emptycount) > wordcount_max) or (emptycount > wordcount and fenzilength > 5 ):
                entropy = 100.0
            else:
                for fenzi in fenzilist:
                    val = float(fenzi) / totalcount
                    entropy = entropy - math.log10(val)

            # 对左右熵求平均
            entropy = entropy / 2
            candidatedict['entropy']  = entropy
            self.maybewords[candidateword] = candidatedict
            if candidatedict.__contains__('aggregation'):
                print '候选词：' + candidateword + '' + str(candidatedict['count']) + '  ' + str(candidatedict['entropy'])+ '  ' + str(candidatedict['aggregation'])

            # 计算可信度，小于1的从25% 递减到0%，大于1小于50的25%递增到50%，大于等于50的直接为50%
            if entropy < 1:
                confidence = 25 * entropy
            elif entropy >= 50:
                confidence = 50.0
            else:
                confidence = 24.5 + entropy / 2
            if candidatedict.__contains__('confidence'):
                candidatedict['confidence'] = candidatedict['confidence'] + confidence
            else:
                candidatedict['confidence'] = confidence


    def filterByThreshold(self):
        for candidateword in self.maybewords.keys():
            candidatedict = self.maybewords[candidateword]
            if not candidatedict.__contains__('aggregation'):
                continue
            aggregate = candidatedict['aggregation']
            freedom = candidatedict['entropy']
            if freedom == 50 :
                pass
            elif freedom < 1 or aggregate > 5000:
                continue
            self.realwords[candidateword] = candidatedict

            print '候选词：' + candidateword + '' + str(candidatedict['count']) + '  ' + str(candidatedict['entropy'])+ '  ' + str(candidatedict['aggregation'])

    def includeMerge(self):
        removewordlist = []
        for candidateword1 in self.realwords.keys():
            candidatedict1 = self.realwords[candidateword1]
            candidatecount1 = candidatedict1['count']

            # 重新遍历一遍
            for candidateword2 in self.realwords.keys():
                if len(candidateword2) <= len(candidateword1):
                    continue
                if not str(candidateword2).__contains__(candidateword1):
                    continue


                candidatecount1_plus = candidatecount1 * 0.15
                candidatecount1_min = candidatecount1 - candidatecount1_plus
                candidatecount1_max = candidatecount1 + candidatecount1_plus

                candidatedict2 = self.realwords[candidateword2]
                candidatecount2 = candidatedict2['count']
                if candidatecount2 >= candidatecount1_min and candidatecount2 <= candidatecount1_max:
                    removewordlist.append(candidateword1)
                    break

        # 删除需要移除的词
        for removeword in removewordlist:
            print 'remove word:' + removeword
            if self.realwords.__contains__(removeword):
                del self.realwords[removeword]

    def prefixMerge(self):
        removewordlist = []
        for candidateword1 in self.realwords.keys():
            candidatedict1 = self.realwords[candidateword1]
            candidatecount1 = candidatedict1['count']

            # 重新遍历一遍
            for candidateword2 in self.realwords.keys():
                if not str(candidateword2).startswith(candidateword1):
                    continue
                if len(candidateword2) <= len(candidateword1):
                    continue

                candidatecount1_plus = candidatecount1*0.15
                candidatecount1_min = candidatecount1 - candidatecount1_plus
                candidatecount1_max = candidatecount1 + candidatecount1_plus

                candidatedict2 = self.realwords[candidateword2]
                candidatecount2 = candidatedict2['count']
                if candidatecount2 >= candidatecount1_min and candidatecount2 <= candidatecount1_max:
                    removewordlist.append(candidateword1)
                    break




        # 删除需要移除的词
        for removeword in removewordlist:
            print 'remove word:' + removeword
            if self.realwords.__contains__(removeword):
                del self.realwords[removeword]


    def suffixMerge(self):
        removewordlist = []
        for candidateword1 in self.realwords.keys():
            candidatedict1 = self.realwords[candidateword1]
            candidatecount1 = candidatedict1['count']

            # 重新遍历一遍
            for candidateword2 in self.realwords.keys():
                if not str(candidateword2).endswith(candidateword1):
                    continue
                if len(candidateword2) <= len(candidateword1):
                    continue

                candidatecount1_plus = candidatecount1*0.15
                candidatecount1_min = candidatecount1 - candidatecount1_plus
                candidatecount1_max = candidatecount1 + candidatecount1_plus

                candidatedict2 = self.realwords[candidateword2]
                candidatecount2 = candidatedict2['count']
                if candidatecount2 >= candidatecount1_min and candidatecount2 <= candidatecount1_max:
                    removewordlist.append(candidateword1)
                    break




        # 删除需要移除的词
        for removeword in removewordlist:
            print 'remove word:' + removeword
            if self.realwords.__contains__(removeword):
                del self.realwords[removeword]

    def middleMerge(self):
        removewordlist = []

        for candidateword1 in self.realwords.keys():
            candidatedict1 = self.realwords[candidateword1]
            candidatecount1 = candidatedict1['count']
            confidence_1 = candidatedict1['confidence']
            # 重新遍历一遍
            for candidateword2 in self.realwords.keys():
                if candidateword1 == candidateword2:
                    continue

                length = len(candidateword1)
                for i in range(length):
                    word = candidateword1[i:]
                    #print word
                    if not str(candidateword2).startswith(word):
                        continue
                    #
                    candidatecount1_plus = candidatecount1 * 0.15
                    candidatecount1_min = candidatecount1 - candidatecount1_plus
                    candidatecount1_max = candidatecount1 + candidatecount1_plus

                    # 前一个词及其数量也基本相符
                    preword = candidateword1[i-1:i]
                    candidatedict2 = self.realwords[candidateword2]
                    candidatecount2 = candidatedict2['count']
                    confidence_2 = candidatedict2['confidence']
                    # 合成向前看，是否可以合并
                    if candidatedict2.__contains__(preword):
                        prewordcount = candidatedict2[preword]
                        # 前一个字的数量也基本上符合
                        if prewordcount >= candidatecount1_min and prewordcount <= candidatecount1_max:
                            # ok , can merge
                            pass

                    else:
                        # 不包含，不能合并
                        continue

                    # 合成向后看，是否可以合并
                    # 前一个词及其数量也基本相符
                    wordlength = len(word)
                    sufword = candidateword2[wordlength:wordlength+1]
                    if sufword == '':
                        continue
                    if candidatedict1.__contains__(sufword):
                        sufwordcount = candidatedict1[sufword]
                        # 前一个字的数量也基本上符合
                        if sufwordcount >= candidatecount1_min and sufwordcount <= candidatecount1_max:
                            # ok , can merge
                            pass

                    else:
                        continue

                    candidatecount2 = candidatedict2['count']
                    if candidatecount2 >= candidatecount1_min and candidatecount2 <= candidatecount1_max:
                        removewordlist.append(candidateword1)
                        removewordlist.append(candidateword2)
                        word = candidateword1[:i]
                        word = word + candidateword2
                        pinyin = self.splitor.pinyin(word)
                        confidence = confidence_1 * confidence_2
                        tup = (word, pinyin, candidateword1, candidatecount1, candidateword2, candidatecount2, confidence)
                        self.outputwordsdict[word] = tup
                        self.outputwordslist.append(tup)
                        break
                    else:
                        self.addFailMergeDict(candidateword1, candidatecount1, confidence_1, candidateword2, candidatecount2, confidence_2,word)

        # 删除需要移除的词
        for removeword in removewordlist:
            print 'remove word:' + removeword
            if self.realwords.__contains__(removeword):
                del self.realwords[removeword]

        # 将新增加的词放入realwords中
        for tup in self.outputwordslist:
            worddict = {}
            worddict['count'] = tup[3]
            worddict['confidence'] = tup[6]
            self.realwords[tup[0]] = worddict

        # 清空outputlist
        self.outputwordslist = []

    def titleMerge(self):
        for titleword in self.titlewords.keys():
            # 对于频度为1，的词不要，两个字频度小于等于2的不要
            titleword_count = self.titlewords[titleword]
            titleword_length = len(titleword)
            if titleword_count == 1:
                continue
            if titleword_count < 3 and titleword_length == 2:
                continue
            # 在停用词表中得不要
            if self.fp.stopwords.__contains__(titleword):
                continue
            # 如果titleword在realword中存在，则不处理，如果不存在，则加入该词
            if self.realwords.__contains__(titleword):
                worddict = self.realwords[titleword]
                worddict['confidence'] = worddict['confidence'] + 100.0
                continue
            ndict = {}
            ndict['count'] = titleword_count * 30
            ndict['confidence'] = 100.0
            self.realwords[titleword] = ndict

    def word23lengthProcess(self):
        lst = []
        for word in self.wordfreq.keys():
            length = len(word)
            wordcount = self.wordfreq[word]
            if (length == 3 and wordcount > 100):
                # 看看是否在realword中已经存在了，不存在可以加入，存在得话，就排除
                hasexist = False
                for realword in self.realwords.keys():
                    if realword.__contains__(word):
                        hasexist = True
                        break
                if hasexist == False:
                    for realwordtup in self.outputwordslist:
                        if str(realwordtup[0]).__contains__(word):
                            hasexist = True
                            break
                if hasexist == False:
                    pinyin = self.splitor.pinyin(word)
                    tup = (word, pinyin, '', wordcount, '', wordcount, 80.0)
                    self.outputwordslist.append(tup)

    def failMiddleRemerge(self):
        """
        对于不能够一次性合并的，需要进行再次尝试合并
        :return: 
        """
        removewordlist = []
        for word in self.mergefaildict.keys():
            if word == '货币分析法':
                print word
            worddict = self.mergefaildict[word]
            midsame = worddict['midsame']
            if midsame == 0:
                continue
            wordcount = worddict['count']
            wordcount_plus = wordcount * 0.1
            wordcount_min = wordcount - wordcount_plus
            wordcount_max = wordcount + wordcount_plus
            subword_totalcount = 0.0
            for subword in worddict.keys():
                if subword == 'count' or subword == 'midsame' or subword == 'midword' or subword == 'confidence':
                    continue
                count = worddict[subword]
                subword_totalcount = subword_totalcount + count
            # can merge

            if subword_totalcount >= wordcount_min and subword_totalcount <= wordcount_max:
                self.failMiddleRemerge_sub(word, wordcount, worddict, removewordlist)

        # 删除需要移除的词
        for removeword in removewordlist:
            print 'remove word:' + removeword
            if self.realwords.__contains__(removeword):
                del self.realwords[removeword]

    def failMiddleRemerge_sub(self, candiword, candicount,candidict, removewordlist):
        """
        合并词，并将合并前的加入移除列表
        :param candiword: 
        :param candidict: 
        :param removewordlist: 
        :return: 
        """
        # 首先判断谁是先，谁是后
        midword = candidict['midword']
        midlength = len(midword)
        removewordlist.append(candiword)
        if str(candiword).startswith(midword):
            # 当前为后缀
            for subword in candidict.keys():
                if subword == 'count' or subword == 'midsame' or subword == 'midword'  or subword == 'confidence':
                    continue

                removewordlist.append(subword)
                word = candiword[midlength:]
                nword = subword + word
                pinyin = self.splitor.pinyin(nword)
                tup = (nword, pinyin, candiword, candicount, subword, candidict['count'], candidict['confidence'])
                self.outputwordsdict[nword] = tup
                self.outputwordslist.append(tup)

        elif str(candiword).endswith(midword):
            # 当前为前缀
            for subword in candidict.keys():
                if subword == 'count' or subword == 'midsame' or subword == 'midword'  or subword == 'confidence':
                    continue

                removewordlist.append(subword)
                word = candiword[:-midlength]
                nword = word + subword
                pinyin = self.splitor.pinyin(nword)
                tup = (nword, pinyin, candiword, candicount, subword, candidict['count'], candidict['confidence'])
                self.outputwordsdict[nword] = tup
                self.outputwordslist.append(tup)



    def addFailMergeDict(self, candi1, can1count,conf1, candi2, can2count, conf2,midword):
        """
        保存无法结合的词，作为最后检查时使用
        :param candi1: 
        :param candi2: 
        :return: 
        """
        # can1 - > can2
        if self.mergefaildict.__contains__(candi1):
            can1_dict = self.mergefaildict[candi1]
            midsame = can1_dict['midsame']
            if midsame == 0:
                #中间部分不同的，不能合并
                return
            premidword = can1_dict['midword']
            if premidword <> midword:
                can1_dict['midsame'] = 0
            if not can1_dict.__contains__(candi2):
                can1_dict[candi2] = can2count
        else:
            cand1dict = {}
            cand1dict['count'] = can1count
            cand1dict['midword'] = midword
            cand1dict['midsame'] = 1
            cand1dict['confidence'] = conf1
            cand1dict[candi2] = can2count
            self.mergefaildict[candi1] = cand1dict

        # can2 - > can1
        if self.mergefaildict.__contains__(candi2):
            can2_dict = self.mergefaildict[candi2]
            midsame = can2_dict['midsame']
            if midsame == 0:
                # 中间部分不同的，不能合并
                return
            premidword = can2_dict['midword']
            if premidword <> midword:
                can2_dict['midsame'] = 0
            if not can2_dict.__contains__(candi1):
                can2_dict[candi1] = can1count
        else:
            cand2dict = {}
            cand2dict['count'] = can2count
            cand2dict['midword'] = midword
            cand2dict['midsame'] = 1
            cand2dict['confidence'] = conf2
            cand2dict[candi1] = can1count
            self.mergefaildict[candi2] = cand2dict

    def outputResult(self):
        # 引用的词和ngram的词合并
        for quoteword in self.fp.quotewords.keys():
            quotewordcount = self.fp.quotewords[quoteword]
            if self.realwords.__contains__(quoteword):
                worddict = self.realwords[quoteword]
                worddict['count'] = worddict['count'] + quotewordcount
            elif quotewordcount > self.fp.quoteweight:
                ndict = {}
                ndict['count'] = quotewordcount
                ndict['confidence'] = 100.0
                self.realwords[quoteword] = ndict

        # ngram 词输出
        for word in self.realwords.keys():
            worddict = self.realwords[word]
            if self.outputwordsdict.__contains__(word):
                continue
            lastchar_1 = word[-1:]
            lastchar_2 = word[-2:-1]
            if lastchar_1 == lastchar_2:
                continue
            firstchar_1 = word[:1]
            firstchar_2 = word[1:2]
            if firstchar_1 == firstchar_2:
                continue
            # 如果是辅助词，不要
            if self.fp.auxiliarywords.__contains__(word):
                continue
            wordcount = worddict['count']
            # 小于输出频率得不要
            if wordcount < self.maxOutputfreq:
                continue
            confidence = worddict['confidence']
            pinyin = self.splitor.pinyin(word)
            tup = (word, pinyin, '', wordcount, '', wordcount, confidence)
            self.outputwordslist.append(tup)

        # 对字符串排序
        # 列表
        #vowels = ['e', 'a', 'u', 'o', 'i']
        # 降序
        #vowels.sort(reverse=True)
        #self.outputwords.sort()
        # 按名称排序
        #sortlist = sorted(self.outputwordslist, cmp=lambda x, y: cmp(x[1], y[1]))
        # 按重要度排序
        sortlist = sorted(self.outputwordslist, cmp=lambda x, y: cmp(y[3], x[3]))
        index = 0
        wordlst = []
        for tup in sortlist:
            index = index + 1
            confidence = tup[6]
            if confidence > 100.0:
                confidence = 100.0
            ns = '{0} {1} {7} {2} {3} {4} {5} {6}'.format(index, tup[0],tup[1],tup[2],tup[3], tup[4], tup[5], confidence)
            wordlst.append(ns)


        fout = open(self.outputfile, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(wordlst))  # 将分词好的结果写入到输出文件
        fout.close()

    def extractHotwords(self):
        # 政治学基础
        # sr.inputfile = './../data/zhengzhixuejichu-course.txt'
        # sr.outputfile = './../data/zhengzhixuejichu-auto-knowledge.txt'
        # 中级财务会计
        # sr.inputfile = './../data/zhongjicaiwukuaiji-course.txt'
        # sr.outputfile = './../data/zhongjicaiwukuaiji-auto-knowledge.txt'
        # 国际金融学
        # sr.inputfile = './../data/financial-course.txt'
        # sr.outputfile = './../data/guojijinrong-auto-knowledge.txt'

        # 国家税收
        #sr.inputfile = './../data/guojiashuishou-course.txt'
        #sr.outputfile = './../data/guojiashuishou-auto-knowledge.txt'


        # 生成ngram的所有候选集
        self.generateCandidateword()
        # 过滤频率小于3的词
        # 计算词的凝固度
        self.computeAggregation()
        # 计算词的自由度
        self.computeFreedom()
        # 对于自由度小于1的，或者凝固度大于5000的，都过滤掉
        print '=====================result=========================='
        self.filterByThreshold()

        # 单词合并，对于一个词完全是另外一个词的前缀 或者后缀，则该词可以舍弃（舍弃的条件也是，这2个词的数量在一个级别上，数量相差不能超过10%）；
        self.includeMerge()
        self.prefixMerge()
        self.suffixMerge()
        # 对于一个词的后半部分和另外一个词的前半部分完全重合，则，该2个词可以合并（该种情况下，词的数量比较接近，大概在10%，否则不予考虑）；
        self.middleMerge()
        self.failMiddleRemerge()
        self.titleMerge()
        self.word23lengthProcess()

        # 将结果输出到文件
        self.outputResult()
        print 'extract knowledge over.'

if __name__ == "__main__":
    sr = NGram()
    sr.maxComputefreq = 10
    sr.maxOutputfreq = 15
    # 政治学基础
    #sr.inputfile = './../data/zhengzhixuejichu-course.txt'
    #sr.outputfile = './../data/zhengzhixuejichu-auto-knowledge.txt'
    # 中级财务会计
    #sr.inputfile = './../data/zhongjicaiwukuaiji-course.txt'
    #sr.outputfile = './../data/zhongjicaiwukuaiji-auto-knowledge.txt'
    # 国际金融学
    #sr.inputfile = './../data/financial-course.txt'
    #sr.outputfile = './../data/financial-auto-knowledge.txt'

    # 国家税收
    #sr.inputfile = './../data/guojiashuishou.txt'
    #sr.outputfile = './../data/guojiashuishou-auto-knowledge.txt'
    #sr.inputfile = './../data/guojiashuishou-ori.txt'
    #sr.outputfile = './../data/guojiashuishou-ori-auto-knowledge1.txt'

    # 营销管理
    #sr.inputfile = './../data/yingxiaoguanli-course.txt'
    #sr.outputfile = './../data/yingxiaoguanli-auto-knowledge.txt'

    # 中国法制史
    #sr.inputfile = './../data/zhongguofazhishi-course.txt'
    #sr.outputfile = './../data/zhongguofazhishi-auto-knowledge.txt'

    # 程序设计实验指导
    #sr.inputfile = './../data/chengxusheji-01-course.txt'
    #sr.outputfile = './../data/chengxusheji-01-auto-knowledge.txt'

    # c-datastructure
    #sr.inputfile = './../data/c-datastructure-courese.txt'
    #sr.outputfile = './../data/c-datastructure-auto-knowledge.txt'

    # 少儿身心发育与养护
    #sr.inputfile = u'./../data/少儿身心发育与养护.txt'
    #sr.outputfile = u'./../data/少儿身心发育与养护-auto-knowledge.txt'

    # 无机化学
    sr.inputfile = u'./../data/无机化学.txt'
    sr.outputfile = u'./../data/无机化学-auto-knowledge.txt'

    # 生成ngram的所有候选集
    sr.generateCandidateword()
    # 过滤频率小于3的词
    # 计算词的凝固度
    sr.computeAggregation()
    # 计算词的自由度
    sr.computeFreedom()
    # 对于自由度小于1的，或者凝固度大于5000的，都过滤掉
    print '=====================result=========================='
    sr.filterByThreshold()

    # 单词合并，对于一个词完全是另外一个词的前缀 或者后缀，则该词可以舍弃（舍弃的条件也是，这2个词的数量在一个级别上，数量相差不能超过10%）；
    sr.includeMerge()
    sr.prefixMerge()
    sr.suffixMerge()
    # 对于一个词的后半部分和另外一个词的前半部分完全重合，则，该2个词可以合并（该种情况下，词的数量比较接近，大概在10%，否则不予考虑）；
    sr.middleMerge()
    sr.failMiddleRemerge()
    sr.titleMerge()
    sr.word23lengthProcess()

    # 将结果输出到文件
    sr.outputResult()
    key = u'离子化合物'
    if sr.candicatewords.__contains__(key):
        dit = sr.candicatewords[key]
        print 'find'
    key = u'子化合物'
    if sr.candicatewords.__contains__(key):
        dit = sr.candicatewords[key]
        print 'find'
    key = u'子化合物'
    if sr.candicatewords.__contains__(key):
        dit = sr.candicatewords[key]
        print 'find'

    key = u'固定资产原'
    if sr.candicatewords.__contains__(key):
        dit = sr.candicatewords[key]
        print 'find'

    #len(sr.fp.quotewords.keys())

    length = len(sr.mergefaildict)
    print 'split over'