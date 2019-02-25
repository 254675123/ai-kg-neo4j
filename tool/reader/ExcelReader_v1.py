# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-06
program       : *_* read excel data  *_*

"""
import hashlib
import re
import sys

import xlrd

from domain import CourseInfomation
from tool.convertor import UnicodeConvertor

# import xlwt
# from datetime import date,datetime
reload(sys)
sys.setdefaultencoding('utf-8')

class ExcelReader:
    """
    read data from excel file.
    """

    def __init__(self):
        """
        initialize data
        """
        self.result = []
        self.cypher = None
        self.cypherlist = []

        self.knowledge = {}
        self.question = {}

        self.course = CourseInfomation.CourseDictionary()

        #self.course.initDictionary(u'./../data/dictionary/course.txt')
        # 记录没有知识点的行，打印用
        self.no_kwg_row_count = 0
        # 初始化列
        self.__initColumn()


    def __initColumn(self):
        self.columns = {}
        cols = [u'院校',u'高校名称',u'课程名称',u'课程编号',u'题库编号',u'试题编号',
                u'题型名称',u'试题类别',u'难度',u'标注知识点']

        for col in cols:
            self.columns[col] = (-1, -1)


    def resetColumn(self):
        for col in self.columns.keys():
            self.columns[col] = (-1, -1)


    def getCourseCypher(self, filepath):
        """
        file path
        :param filepath: 
        :return: 
        """
        self.cypherlist = []

        self.readFile(filepath)
        self.generateCypher()

        return self.cypherlist

    def initColumnIndex(self, sheet):
        if sheet.nrows == 0:
            return
        first_row = sheet.row_values(0)
        name_in_sheet_index = 0
        name_in_data_index = 0
        for col_name in first_row:
            if self.columns.__contains__(col_name):
                self.columns[col_name] = (name_in_sheet_index, name_in_data_index)
                name_in_data_index += 1
                print '列名称：{} 列序号：{}'.format(col_name, name_in_sheet_index)

            name_in_sheet_index += 1

    def readFile(self, filepath):
        """
        read the excel data
        python操作excel主要用到xlrd和xlwt这两个库，即xlrd是读excel，xlwt是写excel的库。
        可从这里下载https://pypi.python.org/pypi。下面分别记录python读和写excel.
        未读取到数据的文件有：
        东财《人际沟通与交往艺术》智能题库试点课程题库试题标知识点、核对难度、补做解析--工商组马骥骅.xlsx
        东财《工程建设监理》--智能题库试点课程题库试题标知识点、核对难度、补做解析--谭海超.xlsx
        东财《服务管理》智能题库试点课程题库试题标知识点、核对难度、补做解析.xlsx
        东财《金融市场学》--智能题库试点课程题库试题标知识点、核对难度、补做解析.xlsx
        福师《中国教育简史》智能题库试点课程题库试题标知识点、核对难度、补做解析.xlsx
        福师《中国法制史》智能题库试点课程题库试题标知识点、核对难度、补做解析--郭兵.xlsx
        福师《外国法制史》智能题库试点课程题库试题标知识点、核对难度、补做解析-郭兵.xlsx
        福师《现代公共关系学》智能题库试点课程题库试题标知识点、核对难度、补做解析.xlsx
        西交《公司金融》智能题库试点课程题库试题标知识点、核对难度、补做解析--徐晶晶-金融组.xlsx
        西交《桥梁工程》智能题库试点课程题库试题标知识点、核对难度、补做解析--张坤.xlsx
        西交《桥梁工程》智能题库试点课程题库试题标知识点、核对难度、补做解析.xlsx
        东财《建筑力学B》刘晶-9.11.xlsx
        东财《金融法》智能题库试点课程题库试题标知识点、核对难度、补做解析--单美玉.xlsx
        福师《中国当代文学》-黄莹.xlsx
        福师《中国政治制度史》--文史哲组孙剑.xlsx
        福师《大学英语（一）》等甘棠--(完成770题)9.11.xlsx
        福师《宪法学》--魏海群9.11.xlsx
        福师《心理学》师范组肖聆伊.xlsx
        福师《经济法律通论》郑本兵-9.12.xlsx
        西交《知识产权法学》-徐伟伟（部分完成）9.11.xlsx
        西交《经济法学（高起专）》郑本兵-9.12.xlsx
        西交《老年护理学》《外科护理学（高起专）》寇耀晖9.11.xlsx
        预生产环境 20180918.xlsx
        福师《中国当代文学》黄莹解析--李玥萱审核.xlsx
        福师《日语（二）》-何珊建设.xlsx
        东财《国际经济学》.xlsx
        西交《水污染控制工程》.xlsx
        :param filepath:the excel full path 
        :return: ture if read file ok, false otherwise 
        """

        self.result = []
        # 打开文件
        workbook = xlrd.open_workbook(filepath)

        # 获取所有sheet
        # [u'院校',u'高校名称',u'课程名称',u'课程编号',u'题库编号',u'试题编号',u'题型名称',u'试题类别', u'难度',u'标注知识点']
        #print workbook.sheet_names()  # [u'sheet1', u'sheet2']
        #sheet2_name = workbook.sheet_names()[1]
        sheetlength = workbook.sheets().__len__()
        totalcount = 0
        index = 0
        while index < sheetlength:
            sheet = workbook.sheet_by_index(index)
            self.resetColumn()
            self.initColumnIndex(sheet)
            index = index + 1

            rowindex = 0
            while rowindex < sheet.nrows:
                row = sheet.row_values(rowindex)
                if rowindex == 0:
                    rowindex = rowindex + 1
                    k_col_tuple_val = self.columns[u'标注知识点']
                    if k_col_tuple_val[0] == -1:
                        break
                    else:
                        continue

                rowindex = rowindex + 1
                row_col_length = len(row)

                item = {}
                # 标注知识点
                exam_knowledge_tuple = self.columns[u'标注知识点']
                if exam_knowledge_tuple[0] == -1:
                    continue
                if exam_knowledge_tuple[0] >= row_col_length:
                    continue
                kdesc = self.preprocessKnowledge(row[exam_knowledge_tuple[0]])
                # row = sheet.row_values(rowindex)
                if len(kdesc) == 0:
                    self.no_kwg_row_count += 1
                    #print 'no knowledge row count:' + str(self.no_kwg_row_count)
                    continue
                item['knowledge'] = kdesc

                # 院校
                school_name_tuple = self.columns[u'院校']
                if school_name_tuple[0] == -1:
                    school_name_tuple = self.columns[u'高校名称']
                    if school_name_tuple[0] == -1:
                        continue
                if school_name_tuple[0] >= row_col_length:
                    continue
                item[u'schoolname'] = row[school_name_tuple[0]]

                # 课程名称
                course_name_tuple = self.columns[u'课程名称']
                if course_name_tuple[0] == -1:
                    continue
                if course_name_tuple[0] >= row_col_length:
                    continue
                item[u'coursename'] = row[course_name_tuple[0]]

                # 课程编码
                course_code_tuple = self.columns[u'课程编号']
                if course_code_tuple[0] == -1:
                    continue
                if course_code_tuple[0] >= row_col_length:
                    continue
                item[u'courseid'] = self.preprocessCourseId(str(row[course_code_tuple[0]]))

                # 题库编号
                bank_code_tuple = self.columns[u'题库编号']
                if bank_code_tuple[0] == -1:
                    item['databaseid'] = self.course.getBankIdByCourseCode(item[u'courseid'])
                else:
                    if bank_code_tuple[0] >= row_col_length:
                        continue
                    item['databaseid'] = row[bank_code_tuple[0]]

                # 试题编号
                exam_code_tuple = self.columns[u'试题编号']
                if exam_code_tuple[0] == -1:
                    continue
                if exam_code_tuple[0] >= row_col_length:
                    continue
                item['questionid'] = str(row[exam_code_tuple[0]]).upper()

                # 题型名称
                exam_type_tuple = self.columns[u'题型名称']
                if exam_type_tuple[0] == -1:
                    continue
                if exam_type_tuple[0] >= row_col_length:
                    continue
                item['questiontype'] = str(row[exam_type_tuple[0]])

                # 试题类别
                exam_cate_tuple = self.columns[u'试题类别']
                if exam_cate_tuple[0] == -1:
                    continue
                if exam_cate_tuple[0] >= row_col_length:
                    continue
                item['questioncate'] = str(row[exam_cate_tuple[0]])

                # 难度
                exam_diff_tuple = self.columns[u'难度']
                if exam_diff_tuple[0] == -1:
                    continue
                if exam_diff_tuple[0] >= row_col_length:
                    continue
                item['questiondiff'] = str(row[exam_diff_tuple[0]])

                self.result.append(item)
                totalcount = totalcount + 1
                if totalcount % 100 == 0:
                    print '已经读取：{0}行'.format(totalcount)

        print '共读取：{0}行'.format(totalcount)
        # sheet的名称，行数，列数
        #print sheet2.name, sheet2.nrows, sheet2.ncols

        # 获取整行和整列的值（数组）
        #rows = sheet2.row_values(3)  # 获取第四行内容
        #cols = sheet2.col_values(2)  # 获取第三列内容
        #print rows
        #print cols

        # 获取单元格内容
        #print sheet2.cell(1, 0).value.encode('utf-8')
        #print sheet2.cell_value(1, 0).encode('utf-8')
        #print sheet2.row(1)[0].value.encode('utf-8')

        # 获取单元格内容的数据类型
        #print sheet2.cell(1, 0).ctype

    def addOneRow(self, row, knowledgelist):
        item = {}
        schoolname = str(row[0])
        coursename = str(row[1])
        courseid = self.preprocessCourseId(str(row[2]))
        bankid = self.course.getBankIdByCourseCode(courseid)
        if bankid is None:
            print 'not bank id'
            return
        item['schoolname'] = schoolname
        item['coursename'] = coursename
        item['courseid'] = courseid
        item['databaseid'] = bankid
        item['questionid'] = str(row[3]).upper()
        item['questiontype'] = str(row[4])
        item['questioncate'] = str(row[5])
        item['questiondiff'] = str(row[6])

        item['knowledge'] = knowledgelist
        self.result.append(item)

    def generateCypher(self):
        """
        generate cypher 
        :return: 
        """
        # first make constraint
        # CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;
        # CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;
        # "MERGE ({0}:Knowledge {{code: '{1}'}})".format(node['key'],node['code'])
        # "MERGE ({0})-[:SOLVE]->({1})".format(knode['key'], qnode['key'])
        if len(self.result) == 0:
            return

        self.cypherlist.append("CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;")
        self.cypherlist.append("CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;")
        self.cypherlist.append("create index on:Question(databaseid);")
        for item in self.result:
            coursename = item['coursename']
            k_list = item['knowledge']
            for k in k_list:
                md5code = self.getMd5(coursename + k)
                md5code = str(md5code).upper()
                kns = "MERGE (k:Knowledge {{code:'{0}'}}) on create set k.name='{1}'".format(md5code, k)
                #kns = "MERGE (k:Knowledge {{code:'{0}',name: '{1}'}})".format(md5code, k)
                #qns = "MERGE (q:Question {{code: '{0}',type:'{1}', category:'{2}',diff:'{3}',coursename:'{4}',courseid:'{5}', databaseid:'{6}', schoolname:'{7}'}})".format(item['questionid'], item['questiontype'], item['questioncate'],item['questiondiff'],item['coursename'],item['courseid'],item['databaseid'],item['schoolname'])
                qns = "MERGE (q:Question {{code:'{0}'}}) on create set q.type='{1}', q.category='{2}',q.diff='{3}',q.coursename='{4}',q.courseid='{5}', q.databaseid='{6}', q.schoolname='{7}'".format(
                    item['questionid'], item['questiontype'], item['questioncate'], item['questiondiff'],
                    item['coursename'], item['courseid'], item['databaseid'], item['schoolname'])
                rns = "MERGE (k)-[:CHECK]->(q);"
                com = kns + '\r\n' + qns + '\r\n' + rns + '\r\n'
                self.cypherlist.append(com)

    def preprocessCourseId(self, data):
        """
        UnicodeEncodeError: 'decimal' codec can't encode character u'\x00' in position 8: invalid decimal Unicode string
        You have some non-visible characters in your string before and after the 100. 
        Therefore theint function is failing because it can't convert this string into an int.
        :param data: 
        :return: 
        """
        #print data
        # find all characters in the string that are numeric.
        m = re.search(ur'(-{0,1}\d+)', data)
        numeric = m.group() # retrieve numeric string
        res = int(numeric) # returns 100
        return res

    def preprocessKnowledge(self, data):
        res_wordlist = []

        if not isinstance(data, unicode) or len(data.strip()) == 0:
            return res_wordlist
        #data = str(data)
        if data.__contains__("'"):
            data = str(data).replace("'","")

        # 去掉多余空格[像英语之类的知识点，固定短语之类的知识点之间是有空格的，所以空格不能随便去掉]
        #if data.__contains__(" "):
        #    data = str(data).replace(" ", "")

        # 对于多个知识点时，用分号分割
        data = data.replace('；', ';')
        wordlist = data.split(';')

        for word in wordlist:
            # 如果有双引号，则取双引号内的部分作为大粒度知识点
            first = word.find('“')
            last = word.find('”')

            if first >= 0 and last > 0:
                # 只取中间的部分
                res_wordlist = res_wordlist + self.getQuoteWords(word)
            elif first >= 0:
                word = str(word).replace('“', '')
            elif last >= 0:
                word = str(word).replace('”', '')

            res_wordlist.append(word)

        return  res_wordlist

    def getQuoteWords(self, sentence):
        """
        获取句子中，使用双引号强调的词
        :param sentence: 
        :return: 
        """
        start = False
        end = False
        wordlist = []
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
                #if self.auxiliarywords.__contains__(word):
                #    continue

                # 将词加入
                wordlist.append(word)

                tempword = []
                continue
            if start == True:
                if self.isChinese(ch):
                    tempword.append(ch)
                else:
                    start = False
                    tempword = []

        return wordlist

    def isChinese(self, ch):
        res = False
        s_unicode = UnicodeConvertor.stringToUnicode(ch)
        if s_unicode >= u'\\u4e00' and s_unicode <= u'\\u9fa5':
            res = True
        return  res
    def getMd5(self,text):

        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()

        return md5

if __name__ == '__main__':
    #read_excel()
    er = ExcelReader()
    # 福师《比较教育学》-李婷婷建设、郭丽娜审核.xlsx
    # 东财《建筑力学B》刘晶解析--李洪旭审核.xlsx
    # 福师《计算机网络与通讯》-周治军-李小明审核.xls
    # 西交《电站锅炉原理》王健-高强伟审核.xlsx
    # 西交《程序设计基础》李小勇-李瑞静审核.xlsx
    er.readFile(u'./../data/course-subject-20181011/福师《计算机网络与通讯》-周治军-李小明审核.xlsx')

    #data = er.result
    sentencce = u'-1000.0'
    er.preprocessCourseId(sentencce)

    print ''