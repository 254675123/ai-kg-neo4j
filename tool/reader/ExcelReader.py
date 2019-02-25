# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-06
program       : *_* read excel data  *_*
仅用来读取excel文件的内容
参数可以指定sheet的范围，默认是全部，指定的 时候用序号的数组，如: [0,1,2] 是指读取第1，2，3个sheet
参数可以指定列的范围，可以使用名字，也可以用列的序号，都是以数组形式
"""
import hashlib
import sys

import xlrd

from tool.convertor import UnicodeConvertor
from domain import FilePath
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
        # excel 文件的路径
        self.filepath = None
        # sheet的读取范围，默认为全部, 可以按序号，也可以按sheet的名称
        self.sheet_scope_indexes = None
        self.sheet_scope_names = None

        # 单个sheet中，列的范围，默认为全部
        self.column_scope_names = None
        self.column_scope_indexes = None

        # 是否获取第一行，第一行一般为数据头
        self.start_row_index = 1



    def readFile(self, filepath=None):
        """
        read the excel data
        python操作excel主要用到xlrd和xlwt这两个库，即xlrd是读excel，xlwt是写excel的库。
        可从这里下载https://pypi.python.org/pypi。下面分别记录python读和写excel.
        :param filepath:the excel full path 
        :return: ture if read file ok, false otherwise 
        """
        result_list = []

        # 如果filepath 是空的话，就先看看self.filepath 是否为空
        if filepath is None and self.filepath is None:
            print '请设置读取的文件名称.'
            return result_list

        if filepath is None:
            filepath = self.filepath

        # 检查文件是否存在
        if not FilePath.fileExist(filepath):
            return result_list

        # 打开文件
        workbook = xlrd.open_workbook(filepath)
        # 获取所有sheet
        #print workbook.sheet_names()  # [u'sheet1', u'sheet2']
        #sheet2_name = workbook.sheet_names()[1]
        local_sheet_scope_indexes = self.getSheetScope(workbook)


        totalcount = 0
        for index in local_sheet_scope_indexes:
            sheet = workbook.sheet_by_index(index)
            rowindex = self.start_row_index
            local_sheet_columns_indexes = self.getSheetColumnScope(sheet)
            # 如果列的范围与预期不一致，就跳过该sheet
            if self.column_scope_names is not None and len(local_sheet_columns_indexes) != len(self.column_scope_names):
                print '该sheet没有需要的数据'
                continue
            while rowindex < sheet.nrows:
                row = sheet.row_values(rowindex)
                rowindex = rowindex + 1
                try:
                    one_row = self.addOneRow(row, local_sheet_columns_indexes)
                    result_list.append(one_row)
                    totalcount = totalcount + 1
                    if totalcount % 100 == 0:
                        print '已经读取：{0}行'.format(totalcount)
                except Exception:
                    print '数据异常行数:' + str(rowindex)
                    print '读取数据异常：' + Exception.message


        print '共读取：{0}行'.format(totalcount)

        return result_list
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

    def getSheetColumnScope(self, sheet):
        """
        根据设置，取sheet中的哪些列，优先按名称获取
        :return: 
        """
        # 结果column的范围
        result_scope = None

        # 检查名称是否存在
        use_name = False
        use_index = False
        if self.column_scope_names and len(self.column_scope_names) > 0:
            use_name = True
        elif self.column_scope_indexes and len(self.column_scope_indexes) > 0:
            use_index = True

        column_length = sheet.ncols
        row_length = sheet.nrows
        if (use_index == False and use_name == False) or row_length == 0:
            result_scope = range(column_length)
            return result_scope

        result_scope = []
        first_row = sheet.row_values(0)
        result_index = 0
        index = 0
        for column_name in first_row:
            if use_name and self.column_scope_names.__contains__(column_name):
                self.column_scope_names[column_name]=result_index
                result_index += 1
                result_scope.append(index)
            elif use_index and self.column_scope_indexes.__contains__(index):
                #self.column_scope_names[column_name] = result_index
                #result_index += 1
                result_scope.append(index)
            else:
                pass
            index += 1
        return result_scope


    def getSheetScope(self, workbook):
        """
        根据设置，取那些sheet，如果sheet的名称和序号都提供了，优先按名称获取
        :return: 
        """
        # 结果sheet的范围
        result_scope = None

        # 检查名称是否存在
        use_name = False
        use_index = False
        if self.sheet_scope_names and len(self.sheet_scope_names) > 0:
            use_name = True
        elif self.sheet_scope_indexes and len(self.sheet_scope_indexes) > 0:
            use_index = True
        else:
            pass

        sheetlength = workbook.sheets().__len__()
        if use_index == False and use_name == False:
            result_scope = range(sheetlength)
            return result_scope

        index = 0
        result_scope = []
        while index < sheetlength:
            sheet = workbook.sheet_by_index(index)
            if use_name and self.sheet_scope_names.__contains__(sheet.name):
                result_scope.append(index)
            elif use_index and self.sheet_scope_indexes.__contains__(index):
                result_scope.append(index)
            else:
                pass
            index = index + 1
        return result_scope


    def addOneRow(self, row, column_scope):
        # 定义rows_list
        row_item_list = []
        for column_index in column_scope:
            row_item_list.append(row[column_index])
        return row_item_list


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
    # 读取指定的文件和sheet范围
    er.filepath = u'D:/西交《知识产权法学》-徐伟伟（部分完成）9.11.xlsx'
    #er.sheet_scope_indexes = [0]
    # 定义一个question对象
    # 指定列的范围 = [u'课程编号', u'试题编号', u'标注知识点']
    er.column_scope_names = {u'课程编号': -1, u'试题编号': -1, u'标注知识点': -1}
    er.readFile()



    print ''