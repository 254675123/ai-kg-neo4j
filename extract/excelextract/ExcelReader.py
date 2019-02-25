# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-06
program       : *_* read excel data  *_*
处理杨云老师给得excel 树形数据
"""
import hashlib
import sys

import xlrd

from tool.convertor import UnicodeConvertor

# import xlwt
# from datetime import date,datetime
reload(sys)
sys.setdefaultencoding('utf-8')

class ExcelReader:
    """
    该excel里面.
    """

    def __init__(self):
        """
        initialize data
        """
        # 存储多个树,key为rootid
        self.result = {}



    def readFile(self, filepath):
        """
        read the excel data
        python操作excel主要用到xlrd和xlwt这两个库，即xlrd是读excel，xlwt是写excel的库。
        可从这里下载https://pypi.python.org/pypi。下面分别记录python读和写excel.
        :param filepath:the excel full path 
        :return: ture if read file ok, false otherwise 
        """
        # 打开文件
        workbook = xlrd.open_workbook(filepath)
        # 获取所有sheet
        #print workbook.sheet_names()  # [u'sheet1', u'sheet2']
        #sheet2_name = workbook.sheet_names()[1]
        sheetlength = workbook.sheets().__len__()
        totalcount = 0
        index = 0
        while index < sheetlength:
            sheet = workbook.sheet_by_index(index)
            index = index + 1

            rowindex = 0
            while rowindex < sheet.nrows:
                row = sheet.row_values(rowindex)
                if rowindex == 0:
                    rowindex = rowindex + 1
                    continue

                rowindex = rowindex + 1

                try:
                    self.addOneRow(row)
                    totalcount = totalcount + 1
                    if totalcount % 100 == 0:
                        print '已经读取：{0}行'.format(totalcount)
                except Exception:
                    print '读取数据异常：' + Exception.message
                    print '数据异常行数:' + str(rowindex)
                # unique
                #if not self.knowledge.__contains__(item['knowledge']):
                #    self.knowledge[item['knowledge']] = ''

                #if not self.question.__contains__(item['questionid']):
                #    self.question[item['questionid']] = ''

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

    def addOneRow(self, row):
        myid = row[0].upper()
        rootid = row[11].upper()
        if self.result.__contains__(rootid):
            item_list = self.result.get(rootid)
        else:
            item_list = []
            self.result[rootid] = item_list

        # 创建行对象
        cr = CourseRow()
        cr.myid = myid
        cr.rootid = rootid
        cr.name =row[7]
        cr.parentid = row[8].upper()
        cr.courseid = row[13].upper()
        cr.coursename = row[14]

        item_list.append(cr)



    def isChinese(self, ch):
        res = False
        s_unicode = UnicodeConvertor.stringToUnicode(ch)
        if s_unicode >= u'\\u4e00' and s_unicode <= u'\\u9fa5':
            res = True
        return  res
    def getMd5(self,text):

        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()

        return md5

class CourseRow:
    """
        树节点
        """

    def __init__(self):
        """
        initialize local variables.
        """
         # 用于排序的序号
        #self.seq = 0
        self.myid = None
        self.rootid = None
        self.parentid = None
        self.name = None
        self.courseid = None
        self.coursename = None


if __name__ == '__main__':
    #read_excel()
    er = ExcelReader()
    #er.readFile('D:/0701.xlsx')



    print ''