# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-06
program       : *_* read excel data  *_*

"""
import os
import hashlib
import xlrd
#import xlwt
#from datetime import date,datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ExcelReader:
    """
    read data from excel file.
    从excel中提取出需要的数据，然后将数据写入到文本文件
    """

    def __init__(self):
        """
        initialize data
        """
        self.trainfilepath = None
        self.testfilepath = None

        self.result = []
        self.cypher = None
        self.cypherlist = []

        self.knowledge = {}
        self.question = {}

    def getCourseCypher(self, filepath):
        """
        file path
        :param filepath: 
        :return: 
        """
        self.readFile(filepath)
        self.generateCypher()

        return self.cypherlist


    def readFile(self, sourcefilepath, targetfilepath):
        """
        read the excel data
        python操作excel主要用到xlrd和xlwt这两个库，即xlrd是读excel，xlwt是写excel的库。
        可从这里下载https://pypi.python.org/pypi。下面分别记录python读和写excel.
        :param filepath:the excel full path 
        :return: ture if read file ok, false otherwise 
        """
        fileNames = os.path.splitext(targetfilepath)
        self.trainfilepath = fileNames[0] + '-train.txt'
        self.testfilepath = fileNames[0] + '-test.txt'
        # 打开文件
        workbook = xlrd.open_workbook(sourcefilepath)
        # 获取所有sheet
        #print workbook.sheet_names()  # [u'sheet1', u'sheet2']
        #sheet2_name = workbook.sheet_names()[1]
        sheetlength = workbook.sheets().__len__()
        index = 0
        traintxt = []
        testtxt = []
        kntxt = []
        while index < sheetlength:
            sheet = workbook.sheet_by_index(index)
            index = index + 1

            rowindex = 0
            while rowindex < sheet.nrows:
                row = sheet.row_values(rowindex)
                rowindex = rowindex + 1
                if rowindex == 1:
                    continue
                if len(row) < 18:
                    break
                knowledge = row[17]
                if len(knowledge) == 0:
                    continue

                answer = row[14]
                content = row[7]
                answer_content = ''
                if str(answer).__contains__('A'):
                    answer_content = answer_content + ',' + str(row[9])
                if str(answer).__contains__('B'):
                    answer_content = answer_content + ',' + str(row[10])
                if str(answer).__contains__('C'):
                    answer_content = answer_content + ',' + str(row[11])
                if str(answer).__contains__('D'):
                    answer_content = answer_content +  ',' + str(row[12])
                if str(answer).__contains__('E'):
                    answer_content = answer_content +  ',' + str(row[13])


                #knowledge = '无'
                content = content + ' 答案：' + answer_content[1:]
                #kntxt.append(knowledge)
                traintxt.append(content)
                testtxt.append(knowledge+':'+content)


        # 写结果文件
        fout = open(self.trainfilepath, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(traintxt))  # 将分词好的结果写入到输出文件
        fout.close()

        fout = open(self.testfilepath, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(testtxt))  # 将分词好的结果写入到输出文件
        fout.close()

        #fout = open('./../data/guojiashuishou-knowledge.txt', 'w')  # 以写得方式打开文件
        #fout.write('\n'.join(kntxt))  # 将分词好的结果写入到输出文件
        #fout.close()

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

        cylist = []
        cylist.append("CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;")
        cylist.append("CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;")
        for item in self.result:
            k = str(item['knowledge'])
            md5code = self.getMd5(k)
            kns = "MERGE (k:Knowledge {{code:'{0}',name: '{1}'}})".format(md5code, k)
            qns = "MERGE (q:Question {{code: '{0}',type:'{1}', category:'{2}',diff:{3},coursename:'{4}',courseid:'{5}', databaseid:'{6}'}})".format(item['questionid'], item['questiontype'], item['questioncate'],item['questiondiff'],item['coursename'],item['courseid'],item['databaseid'])
            rns = "MERGE (k)-[:CHECK]->(q);"
            com = kns + '\r\n' + qns + '\r\n' + rns + '\r\n'
            self.cypherlist.append(com)

    def preprocess(self, data):
        data = str(data)
        if data.__contains__("'"):
            data = str(data).replace("'","")

        return  data

    def getMd5(self,text):

        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()

        return md5

if __name__ == '__main__':
    #read_excel()
    er = ExcelReader()
    er.readFile('./../data/course/guojiashuishou-20180821.xlsx')

    data = er.result


    print ''