# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-11-13
program       : *_*  define catalog information *_*
"""
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from tool.reader import ExcelReader
from tool.convertor import UnicodeConvertor
from tool.processor import SentenceProcessor
class CatalogItem:
    """
        catalog information.
        """

    def __init__(self):
        """
        initialize local variables.
        """
        self.category_code = None
        self.category_name = None
        self.category_desc = None

    def initData(self, code, name, desc=None):
        self.category_code = code
        self.category_name = name
        self.category_desc = desc

    def toString(self):
        res_list = []
        res_list.append(self.category_code)
        res_list.append(self.category_name)
        res = ' '.join(res_list)

        return res

class Catalog:
    """
        catalog information.
        """

    def __init__(self):
        """
        initialize local variables.
        """
        # 保存分类的信息，有很多分类体系，比如国民经济分类体系，学科分类体系，岗位分类体系等
        self.catalog_code = None
        self.catalog_name = None
        # 分类体系内的细目
        self.category_list = []

        # 文本处理器
        self.sentence_processor = None

    def initCatalog(self):
        pass



    def readZhuankeCatalog(self, filepath):
        """
        专科专业目录
        :param filepath: 
        :return: 
        """
        self.category_list = []
        excel_reader = ExcelReader.ExcelReader()
        excel_reader.filepath = filepath
        excel_reader.sheet_scope_indexes = [0]
        # 定义一个question对象

        # self.excel_reader.column_scope_names = [u'题目内容', u'选项A', u'选项B', u'选项C', u'选项D', u'选项E', u'答案',u'试题编号',u'题型名称',u'试题类别',u'难度', u'标注知识点']
        excel_reader.column_scope_names = {}
        excel_reader.column_scope_names[u'专业大类'] = -1
        excel_reader.column_scope_names[u'专业大类代码'] = -1
        excel_reader.column_scope_names[u'专业类名称'] = -1
        excel_reader.column_scope_names[u'专业类代码'] = -1
        excel_reader.column_scope_names[u'专业名称'] = -1
        excel_reader.column_scope_names[u'专业代码'] = -1

        excel_content_rows = excel_reader.readFile()

        # 分析数据
        fst_name = None
        fst_code = None
        snd_name = None
        snd_code = None
        fst_code_length = 0
        snd_code_length = 0
        for row in excel_content_rows:
            level_fst_name = row[0]
            level_fst_code = row[1]
            level_snd_name = row[2]
            level_snd_code = row[3]
            level_trd_name = row[4]
            level_trd_code = row[5]



            if len(level_fst_name) > 0:
                fst_code = UnicodeConvertor.numToUnicode(level_fst_code)
                fst_name = level_fst_name
                fst_code_length = len(fst_code)
                ci = CatalogItem()
                ci.initData(fst_code, fst_name)
                self.category_list.append(ci)
            if len(level_snd_name) > 0:
                snd_code = UnicodeConvertor.numToUnicode(level_snd_code)
                snd_name = level_snd_name
                ci = CatalogItem()
                snd_code_length = len(snd_code)
                code = u'{}.{}'.format(fst_code, snd_code[fst_code_length:])
                ci.initData(code, snd_name)
                self.category_list.append(ci)

            ci = CatalogItem()
            trd_code = UnicodeConvertor.numToUnicode(level_trd_code)
            #code_length = len(snd_code)
            code = u'{}.{}.{}'.format(fst_code, snd_code[fst_code_length:],trd_code[snd_code_length:])
            ci.initData(code, level_trd_name)
            self.category_list.append(ci)

        return excel_content_rows

    def readBenkeCatalog(self, filepath):
        """
        本科专业目录
        :param filepath: 
        :return: 
        """
        self.category_list = []
        excel_reader = ExcelReader.ExcelReader()
        excel_reader.filepath = filepath
        excel_reader.sheet_scope_indexes = [0]
        # 定义一个question对象

        # self.excel_reader.column_scope_names = [u'题目内容', u'选项A', u'选项B', u'选项C', u'选项D', u'选项E', u'答案',u'试题编号',u'题型名称',u'试题类别',u'难度', u'标注知识点']
        excel_reader.column_scope_names = {}
        excel_reader.column_scope_names[u'大类'] = -1
        excel_reader.column_scope_names[u'大类代码'] = -1
        excel_reader.column_scope_names[u'专业类'] = -1
        excel_reader.column_scope_names[u'专业类代码'] = -1
        excel_reader.column_scope_names[u'专业'] = -1
        excel_reader.column_scope_names[u'专业代码'] = -1

        excel_content_rows = excel_reader.readFile()

        # 分析数据
        fst_name = None
        fst_code = None
        snd_name = None
        snd_code = None
        fst_code_length = 0
        snd_code_length = 0
        for row in excel_content_rows:
            level_fst_name = row[0]
            level_fst_code = row[1]
            level_snd_name = row[2]
            level_snd_code = row[3]
            level_trd_name = row[4]
            level_trd_code = row[5]

            if len(level_fst_name) > 0:
                fst_code = UnicodeConvertor.numToUnicode(level_fst_code)
                fst_name = level_fst_name
                fst_code_length = len(fst_code)
                ci = CatalogItem()
                ci.initData(fst_code, fst_name)
                self.category_list.append(ci)
            if len(level_snd_name) > 0:
                snd_code = UnicodeConvertor.numToUnicode(level_snd_code)
                snd_name = level_snd_name
                ci = CatalogItem()
                snd_code_length = len(snd_code)
                code = u'{}.{}'.format(fst_code, snd_code[fst_code_length:])
                ci.initData(code, snd_name)
                self.category_list.append(ci)

            ci = CatalogItem()
            trd_code = UnicodeConvertor.numToUnicode(level_trd_code)
            #code_length = len(snd_code)
            code = u'{}.{}.{}'.format(fst_code, snd_code[fst_code_length:],trd_code[snd_code_length:])
            ci.initData(code, level_trd_name)
            self.category_list.append(ci)

        return excel_content_rows

    def readGangweiCatalog(self, filepath):
        """
        岗位目录
        :param filepath: 
        :return: 
        """
        self.category_list = []
        excel_reader = ExcelReader.ExcelReader()
        excel_reader.filepath = filepath
        excel_reader.sheet_scope_indexes = [0]
        # 定义一个question对象

        # self.excel_reader.column_scope_names = [u'题目内容', u'选项A', u'选项B', u'选项C', u'选项D', u'选项E', u'答案',u'试题编号',u'题型名称',u'试题类别',u'难度', u'标注知识点']
        excel_reader.column_scope_names = {}
        excel_reader.column_scope_names[u'大类名称'] = -1
        excel_reader.column_scope_names[u'大类代码'] = -1
        excel_reader.column_scope_names[u'中类名称'] = -1
        excel_reader.column_scope_names[u'中类代码'] = -1
        excel_reader.column_scope_names[u'小类名称'] = -1
        excel_reader.column_scope_names[u'小类代码'] = -1

        excel_content_rows = excel_reader.readFile()

        # 分析数据
        fst_name = None
        fst_code = None
        snd_name = None
        snd_code = None
        fst_code_length = 0
        snd_code_length = 0
        for row in excel_content_rows:
            level_fst_name = row[excel_reader.column_scope_names[u'大类名称']]
            level_fst_code = row[excel_reader.column_scope_names[u'大类代码']]
            level_snd_name = row[excel_reader.column_scope_names[u'中类名称']]
            level_snd_code = row[excel_reader.column_scope_names[u'中类代码']]
            level_trd_name = row[excel_reader.column_scope_names[u'小类名称']]
            level_trd_code = row[excel_reader.column_scope_names[u'小类代码']]

            if len(level_fst_name) > 0:
                # 去括号
                fst_code = self.sentence_processor.removeBracket(level_fst_code)
                fst_code = fst_code.replace(u'-', '.')
                fst_name = level_fst_name

                ci = CatalogItem()
                ci.initData(fst_code, fst_name)
                self.category_list.append(ci)
            if len(level_snd_name) > 0:
                snd_code = self.sentence_processor.removeBracket(level_snd_code)
                snd_code = snd_code.replace(u'-', '.')
                snd_name = level_snd_name

                ci = CatalogItem()
                ci.initData(snd_code, snd_name)
                self.category_list.append(ci)

            if len(level_trd_name) > 0:
                trd_code = self.sentence_processor.removeBracket(level_trd_code)
                trd_code = trd_code.replace(u'-', '.')

                ci = CatalogItem()
                ci.initData(trd_code, level_trd_name)
                self.category_list.append(ci)

        return excel_content_rows


    def outputfile(self, filepath):
        filepath = u'{}.txt'.format(filepath)
        fout = open(filepath, 'w')
        for ci in self.category_list:
            fout.write(ci.toString())
            fout.write('\n')
        fout.close()

if __name__ == "__main__":
    c = Catalog()
    # 专科目录
    filepath = u'D:/奥鹏/运营平台-产品中心/分类目录/专科专业目录-catalog.xlsx'
    c.readZhuankeCatalog(filepath)
    c.outputfile(filepath)

    # 本科目录
    filepath = u'D:/奥鹏/运营平台-产品中心/分类目录/本科专业目录-catalog.xlsx'
    c.readBenkeCatalog(filepath)
    c.outputfile(filepath)

    # 岗位目录
    filepath = u'D:/奥鹏/运营平台-产品中心/分类目录/岗位分类目录-catalog.xlsx'
    sen_pro = SentenceProcessor.SenPreprocess()
    c.sentence_processor = sen_pro
    c.readGangweiCatalog(filepath)
    c.outputfile(filepath)

    pass

