# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-11-02
program       : *_*  short sentence syntacticparsing  *_*

"""
import os
import sys
from tool.splitor import HanlpSplitor
from tool.reader import ExcelReader
reload(sys)
sys.setdefaultencoding('utf-8')


class ShortSentenceParsing:
    """
    short sentence syntacticparsing

    抽取规则说明
    分析短句子中的核心词

    """

    def __init__(self):
        """
        initialize local variables.
        """
        # 核心词列表
        self.core_words_list = []
        # 句子分析器
        self.splitor = HanlpSplitor.HanlpSplitor()
        # excel 读取器
        self.excel_reader = ExcelReader.ExcelReader()

    def parseShortSentence(self, filepath):
        """
        分析文件中的短句
        :param filepath: 
        :return: 
        """
        excel_content_rows = self.read_excel_file(filepath)
        #excel_content_rows = [u'中国的房价又贵了', u'明天要考试了，还没有复习']
        for sen in excel_content_rows:
            #res = self.splitor.parseDependency(sen)
            #print res
            for subsen in sen:
                if not (isinstance(subsen, str) or isinstance(subsen, unicode)):
                    continue
                res = self.splitor.extractKeyword(subsen, 3)
                if len(res) == 0:
                    continue

                vip_word_list = []
                for word in res:
                    if len(word) < 2:
                        continue
                    vip_word_list.append(word)
                if len(vip_word_list) == 0:
                    continue

                #vip_word_list.reverse()
                tup = (subsen, vip_word_list)
                self.core_words_list.append(tup)

    def read_excel_file(self, filepath):
        """
        从excel中读取数据
        :param filepath: 
        :return: 
        """
        self.excel_reader.filepath = filepath
        self.excel_reader.sheet_scope_indexes = [1]
        self.excel_reader.column_scope_names = [u'发帖内容', u'回帖内容']
        excel_content_rows = self.excel_reader.readFile()

        return excel_content_rows

    def outputFile1(self, filepath):
        # 写入文件
        fout = open(filepath, 'w')
        for word_tup in self.core_words_list:
            line = '{}: {}'.format(word_tup[0], ' '.join(word_tup[1]))
            fout.write(line)
            fout.write('\n')

        fout.close()

    def outputFile2(self, filepath):
        # 写入文件
        fout = open(filepath, 'w')
        for word_tup in self.core_words_list:
            line = ' '.join(word_tup[1])
            fout.write(line)
            fout.write('\n')

        fout.close()

    def outputFile(self, filepath):
        # 统计一下关键词
        word_dict = {}
        for word in self.core_words_list:
            if word_dict.__contains__(word):
                word_dict[word] = word_dict[word] + 1
            else:
                word_dict[word] = 1

        # 排序
        sort_list = sorted(word_dict.items(),lambda x, y:cmp(x[1], y[1]), reverse=True)

        # 写入文件
        fout = open(filepath, 'w')
        for word in sort_list:
            line = '{}: {}'.format(word[0], word[1])
            fout.write(line)
            fout.write('\n')

        fout.close()


if __name__ == "__main__":
    cp = ShortSentenceParsing()
    filepath = u'D:/奥鹏/学生服务中心标注/副本2018年8月1日--10月8日课程问答发帖及回帖内容.xlsx'
    cp.parseShortSentence(filepath)

    filepath = u'D:/奥鹏/学生服务中心标注/2018年8月1日--10月8日课程问答发帖及回帖内容-statistics.txt'
    cp.outputFile1(filepath)
    filepath = u'D:/奥鹏/学生服务中心标注/2018年8月1日--10月8日课程问答发帖及回帖内容-statistics-pure.txt'
    cp.outputFile2(filepath)