
# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_* hanlp  *_*

"""

from pyhanlp import HanLP
import  re
import os
class HanlpSplitor:
    """
    hanlp splitor
    """
    def __init__(self):
        self.__curpath = os.path.dirname(os.path.realpath(__file__))
        self.wordnetlist = []
        self.wordposlist = []

        # 把停用词做成字典
        self.stopwords = {}
        fstop = open(self.__curpath+'/../../data/dictionary/stopwords-pre-v20180817.txt', 'r')
        for eachWord in fstop:
            self.stopwords[eachWord.strip().decode('utf-8', 'ignore')] = eachWord.strip().decode('utf-8', 'ignore')
        fstop.close()

    def pinyin(self, sentence):
        pinyinlist = HanLP.convertToPinyinList(sentence)
        res = []
        for pinyin in pinyinlist:
            res.append(str(pinyin))

        return ''.join(res)

    def simplechinese(self, sentence):
        simple = HanLP.convertToSimplifiedChinese(sentence)
        return simple

    def split_origin(self,sentence):
        line = sentence.strip().decode('utf-8', 'ignore')  # 去除每行首尾可能出现的空格，并转为Unicode进行处理
        line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:：“”-【】+\"\']+|[+——！，;:：“”。？、~@#￥%……&*（）]+".decode("utf8"),
                       " ".decode("utf8"), line)
        # wordList = list(jieba.cut(line1))  # 用结巴分词，对每行内容进行分词
        wordList = HanLP.segment(line1)

        resultlist = []
        for w in wordList:
            resultlist.append(w.word)

        return resultlist


    def split_test(self, sentence):
        #line = sentence.strip().decode('utf-8', 'ignore')  # 去除每行首尾可能出现的空格，并转为Unicode进行处理
        #line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+".decode("utf8"),
        #               " ".decode("utf8"), line)
        #wordList = list(jieba.cut(line1))  # 用结巴分词，对每行内容进行分词

        print(HanLP.segment('你好，欢迎在Python中调用HanLP的API'))
        for term in HanLP.segment('下雨天地面积水'):
            print('{}\t{}'.format(term.word, term.nature))  # 获取单词与词性
        testCases = [
            "商品和服务",
            "结婚的和尚未结婚的确实在干扰分词啊",
            "买水果然后来世博园最后去世博会",
            "中国的首都是北京",
            "欢迎新老师生前来就餐",
            "工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作",
            "随着页游兴起到现在的页游繁盛，依赖于存档进行逻辑判断的设计减少了，但这块也不能完全忽略掉。"]
        for sentence in testCases: print(HanLP.segment(sentence))
        # 关键词提取
        document = "水利部水资源司司长陈明忠9月29日在国务院新闻办举行的新闻发布会上透露，" \
                   "根据刚刚完成了水资源管理制度的考核，有部分省接近了红线的指标，" \
                   "有部分省超过红线的指标。对一些超过红线的地方，陈明忠表示，对一些取用水项目进行区域的限批，" \
                   "严格地进行水资源论证和取水许可的批准。"
        print(HanLP.extractKeyword(document, 2))
        # 自动摘要
        print(HanLP.extractSummary(document, 3))
        # 依存句法分析
        print(HanLP.parseDependency("徐先生还具体帮助他确定了把画雄鹰、松鼠和麻雀作为主攻目标。"))

        #return wordList

    def split1list(self, sentence):
        line = sentence.strip().decode('utf-8', 'ignore')  # 去除每行首尾可能出现的空格，并转为Unicode进行处理
        line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+".decode("utf8"),
                       " ".decode("utf8"), line)
        #wordList = list(jieba.cut(line1))  # 用结巴分词，对每行内容进行分词
        wordList = HanLP.segment(line1.strip())
        poslist = set()
        for w in wordList:
            length = len(w.word)
            nature = str(w.nature)
            if length < 2  and nature.__contains__('w'):
                continue

            if w.word in self.stopwords:
                preflag = None
                continue

            #if self.isFormWord(nature):
            #    continue

            #wordpos = w.word + '   ' + nature
            #self.wordposlist.append(wordpos)

            poslist.add(w.word)


        return poslist

    def splitlist_can_repeat(self, sentence):
        line = sentence.strip().decode('utf-8', 'ignore')  # 去除每行首尾可能出现的空格，并转为Unicode进行处理
        line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+".decode("utf8"),
                       " ".decode("utf8"), line)
        #wordList = list(jieba.cut(line1))  # 用结巴分词，对每行内容进行分词
        wordList = HanLP.segment(line1.strip())
        poslist = []
        for w in wordList:
            length = len(w.word)
            nature = str(w.nature)
            if length < 2  and nature.__contains__('w'):
                continue

            if w.word in self.stopwords:
                preflag = None
                continue

            #if self.isFormWord(nature):
            #    continue

            #wordpos = w.word + '   ' + nature
            #self.wordposlist.append(wordpos)

            poslist.append(w.word)


        return poslist

    def split(self, sentence):
        line = sentence.strip().decode('utf-8', 'ignore')  # 去除每行首尾可能出现的空格，并转为Unicode进行处理
        line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:：“”-【】+\"\']+|[+——！，;:：“”。？、~@#￥%……&*（）]+".decode("utf8"),
                       " ".decode("utf8"), line)
        #wordList = list(jieba.cut(line1))  # 用结巴分词，对每行内容进行分词
        wordList = HanLP.segment(line1)

        #
        self.process(wordList)
        return self.wordnetlist

    def process(self, wordList):
        self.wordnetlist = []
        preflag = None
        poslist = []
        for w in wordList:
            length = len(w.word)
            nature = str(w.nature)
            if length < 2 and nature.__contains__('w'):
                continue

            if w.word in self.stopwords:
                preflag = None
                continue

            if self.isFormWord(nature):
                continue

            wordpos =  w.word + '   ' + nature
            self.wordposlist.append(wordpos)

            if nature == preflag:
                poslist.append(w.word)
            else:
                if len(poslist) > 0:
                    self.wordnetlist.append(poslist)
                    poslist = []

                poslist.append(w.word)
                preflag = nature

        if len(poslist) > 0:
            self.wordnetlist.append(poslist)

    def isFormWord(self, nature):
        flag = False

        if nature.__contains__('c') or nature == 'e' or nature == 'f' or nature == 'h':
            flag = True

        if nature.__contains__('m')  or nature == 'w' or nature.__contains__('r'):
            flag = True
        if nature.__contains__('u')  or nature == 'p' or nature == 't':
            flag = True

        return flag

    def parseDependency(self, sent):
        """
        句法分析
        :param sent: 
        :return: 
        """
        res = res = HanLP.parseDependency(sent)

        return res

    def extractKeyword(self, sent, num=2):
        """
        抽取关键词
        :param sent: 
        :return: 
        """
        res = HanLP.extractKeyword(sent, num)
        res_list = []
        for word in res:
            if self.stopwords.__contains__(word):
                continue
            else:
                res_list.append(word)
        return res_list

if __name__ == "__main__":
    sr = HanlpSplitor()
    #sr.split('孽息')
    #sr.split_test('')
    #content = '根据刑事诉讼法、民事诉讼法和行政诉讼法的规定，有四类案件实行不公开审理。下列哪一项不属于不公开审理的范围？（   ）'
    #print(HanLP.extractKeyword(content, 5))
    res = HanLP.parseDependency("《灵与肉》的作者是？")
    pinyin = sr.pinyin("国际金融")
    #print res
    sen = u' :: 王某被取保候审，则他不应：（   ） 答案： 要求证人丁某为他说好话, 未经批准到外省出差'
    res = sr.split1list(sen)
    sen = u'  王某被取保候审，则他不应：（   ） 答案： 要求证人丁某为他说好话, 未经批准到外省出差'
    res = sr.splitlist_can_repeat(sen)
    print res
    print 'split over'