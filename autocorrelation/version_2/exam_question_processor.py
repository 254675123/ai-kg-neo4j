# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-10-26
program       : *_*  将excel中试题的的数据，按课程分开存储为单个文件，作为关联和训练语料使用 *_*

"""
from tool.reader import ExcelReader
from tool.convertor import UnicodeConvertor
from domain import CourseInfomation
from domain import QuestionInformation
from domain import MD5
from tool.reader import ExcelWriter

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class ExamQuestionProcessor:
    """
    将excel中试题的的数据，按课程分开存储为单个文件，作为关联和训练语料使用
    """
    def __init__(self):
        """
        定义变量
        """
        self.excel_reader = ExcelReader.ExcelReader()
        self.course_info = None
        self.exam_info = QuestionInformation.ExamquestionDictionary()
        self.rootpath = u'./../../data/course-knowledge-machine/20181122-200plus'
        self.isTest = False
    def setCourseInfo(self, course_info):
        self.course_info = course_info
        self.exam_info.course_info = course_info

    def courseExamQuestionGenerator(self, course_path_info):
        self.excel_reader.filepath =  course_path_info.examquestion_source_xlsx_filepath
        self.excel_reader.sheet_scope_indexes = [0]
        # 定义一个question对象

        #self.excel_reader.column_scope_names = [u'题目内容', u'选项A', u'选项B', u'选项C', u'选项D', u'选项E', u'答案',u'试题编号',u'题型名称',u'试题类别',u'难度', u'标注知识点']
        self.excel_reader.column_scope_names = QuestionInformation.column_head_dict
        QuestionInformation.resetColumnValue()
        excel_content_rows = self.excel_reader.readFile()
        self.exam_info.initByRows(excel_content_rows)

        # 语料用的文件
        self.createCorpusFile(course_path_info)
        # 生成excel试题文件, 正式跑的时候，不用该方法
        if self.isTest:
            self.createExcelFile()
        # 生成cypher用的文件, 知识点的关联部分还没有完成，现在的时间点还不能生成
        #self.createCypherFile()



    def createCypherFile(self, course):
        """
        数据生成cypher语句文件
        :param course: 
        :return: 
        """
        if not self.exam_info.examquestion_dict.__contains__(course):
            return

        exam_question_list = self.exam_info.examquestion_dict.get(course)
        # 将知识点和试题关联起来
        cypherlist = self.generateCypher(course,exam_question_list)

        # 保存数据
        course_path_info = CourseInfomation.CourseFilepath()
        course_path_info.courseware_source_directory = self.rootpath
        course_path_info.initByCourse(course)
        file_name = course_path_info.cypher_txt_filepath
        fout = open(file_name, 'w')
        for item in cypherlist:
            fout.write(item)
            fout.write('\n')
        fout.close()
        print 'cypher文件：{}已生成'.format(course.NewCourseName)
        return cypherlist

    def generateCypher(self,course, exam_question_list):
        """
        generate cypher 
        :return: 
        """
        # first make constraint
        # CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;
        # CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;
        # "MERGE ({0}:Knowledge {{code: '{1}'}})".format(node['key'],node['code'])
        # "MERGE ({0})-[:SOLVE]->({1})".format(knode['key'], qnode['key'])
        if len(exam_question_list) == 0:
            return
        cypherlist = []
        cypherlist.append("CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;")
        cypherlist.append("CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;")
        self.cypherlist.append("create index on:Question(databaseid);")
        for item in exam_question_list:
            exam_content = item.content
            if exam_content.startswith(u'<img'):
                continue
            k_list = item.knowledge_list
            for k in k_list:
                kname=None
                if isinstance(k, str):
                    if len(k.strip()) == 0:
                        continue
                    kname = k
                    md5code = MD5.getMd5(k)
                    md5code = md5code.upper()
                else:
                    if k.score < 0.45:
                        continue
                    md5code = k.code
                    kname = k.text
                kns = "MERGE (k:Knowledge {{code:'{0}'}}) on create set k.name='{1}'".format(md5code, kname)
                #kns = "MERGE (k:Knowledge {{code:'{0}',name: '{1}'}})".format(md5code, k)
                #qns = "MERGE (q:Question {{code: '{0}',type:'{1}', category:'{2}',diff:'{3}',coursename:'{4}',courseid:'{5}', databaseid:'{6}', schoolname:'{7}'}})".format(item['questionid'], item['questiontype'], item['questioncate'],item['questiondiff'],item['coursename'],item['courseid'],item['databaseid'],item['schoolname'])
                qns = "MERGE (q:Question {{code:'{0}'}}) on create set q.type='{1}', q.category='{2}',q.diff='{3}',q.coursename='{4}',q.courseid='{5}', q.databaseid='{6}', q.schoolname='{7}'".format(
                    item.code, item.type, item.category, item.diff,
                    course.NewCourseName, course.CourseCode, course.ItemBankID, course.SchoolCode)
                rns = "MERGE (k)-[:CHECK]->(q);"
                com = kns + ' ' + qns + ' ' + rns
                cypherlist.append(com)
        return  cypherlist

    def createExcelFile(self):
        """
        按照课程，分别存储每个文件
        :return: 
        """
        for course in self.exam_info.examquestion_dict.keys():
            course_path_info = CourseInfomation.CourseFilepath()
            course_path_info.courseware_source_directory = self.rootpath
            course_path_info.initByCourse(course)
            file_name = course_path_info.examquestion_source_xlsx_filepath
            row_list = self.exam_info.examquestion_dict.get(course)
            column_data_list = []
            column_data_list.append(QuestionInformation.column_head_list)
            for exam_question in row_list:
                if exam_question.content.startswith(u'<img'):
                    continue
                column_data_list.append(exam_question.toList())
            sheet_datas = {}
            sheet_datas['sheet1'] = column_data_list
            ExcelWriter.writeExcelFile(course_path_info.examquestion_source_xlsx_filepath, sheet_datas)
            print 'Excel文件：{}已生成'.format(course.NewCourseName)

    def createCorpusFile(self, course_path_info):
        # 将结果按文件id输出
        course = course_path_info.course
        if self.exam_info.examquestion_dict.__contains__(course):
            file_name = course_path_info.examquestion_source_txt_filepath
            row_list = self.exam_info.examquestion_dict.get(course)
            fout = open(file_name, 'w')
            for item in row_list:
                fout.write(item.getContentAndAnswer())
                fout.write('\n')
            fout.close()
            print '语料文件：{}已生成'.format(course.NewCourseName)

        return
        # 下面的是生成全集的
        for course in self.exam_info.examquestion_dict.keys():
            course_path_info = CourseInfomation.CourseFilepath()
            course_path_info.courseware_source_directory = self.rootpath
            course_path_info.initByCourse(course)
            file_name = course_path_info.examquestion_source_txt_filepath
            row_list = self.exam_info.examquestion_dict.get(course)
            fout = open(file_name, 'w')
            for item in row_list:
                fout.write(item.getContentAndAnswer())
                fout.write('\n')
            fout.close()
            print '语料文件：{}已生成'.format(course.NewCourseName)



    def createGoodResult2Excel4PersonCheck(self, course_path_info):
        """
        # 将好的结果输出excel，让人工进行审核
        :param course_path_info: 
        :return: 
        """
        course = course_path_info.course
        if not self.exam_info.examquestion_dict.__contains__(course):
            return

        exam_question_list = self.exam_info.examquestion_dict.get(course)
        # 将知识点和试题关联起来
        column_data_list = []
        column_data_list.append(QuestionInformation.getGoodCorrelationData())

        exam_index = 1
        for exam_question in exam_question_list:
            knowledge_list = exam_question.knowledge_list
            k_index = 1
            for k in knowledge_list:
                if isinstance(k, str):
                    if len(k.strip()) == 0:
                        continue
                    kname = k
                    kscore =u''
                else:
                    if k.score < 0.45:
                        continue
                    kscore = k.score
                    kname = k.text
                kscore = u'{}%'.format(round(kscore*100, 2))
                row = []
                if k_index == 1:
                    exam_index_unicode  = UnicodeConvertor.numToUnicode(exam_index)
                    row.append(exam_index_unicode)
                    row.append(exam_question.getOnlyContentAndAnswer())
                else:
                    row.append(u'')
                    row.append(u'')
                row.append(kname)
                row.append(kscore)
                row.append(u'')
                row.append(u'')
                row.append(u'')

                column_data_list.append(row)
                k_index += 1

            exam_index += 1

        sheet_datas = {}
        sheet_datas['sheet1'] = column_data_list
        ExcelWriter.writeExcelFile(course_path_info.correlation_good_xls_filepath, sheet_datas)
        print 'Excel文件：{}已生成'.format(course.NewCourseName)


    def getQuestionAndAnswer(self, question_row):
        """
        从试题和答案中，组合成一个内容
        :param question_row: 
        :return: 
        """
        question_content = question_row[1]
        question_answer = question_row[7]
        answer_content = ''
        if str(question_answer).__contains__('A'):
            answer_content = answer_content + ', ' + str(question_row[2])
        if str(question_answer).__contains__('B'):
            answer_content = answer_content + ', ' + str(question_row[3])
        if str(question_answer).__contains__('C'):
            answer_content = answer_content + ', ' + str(question_row[4])
        if str(question_answer).__contains__('D'):
            answer_content = answer_content + ', ' + str(question_row[5])
        if str(question_answer).__contains__('E'):
            answer_content = answer_content + ', ' + str(question_row[6])

        answer_content = str(answer_content)
        if len(answer_content):
            answer_content = answer_content[1:]
        knowledge = ''
        if len(question_row) > 12:
            knowledge = str(question_row[12])
        content =  '{}:: {} 答案：{}'.format(knowledge, question_content, answer_content)

        return content



if __name__ == '__main__':
    #read_excel()
    er = ExamQuestionProcessor()
    er.isTest = True
    course_path_info = CourseInfomation.CourseFilepath()
    course_path_info.courseware_source_directory = er.rootpath
    course_path_info.examquestion_source_xlsx_filepath = u'{}/q-xlsx/20181122-200plus.xlsx'.format(er.rootpath)
    course_info = CourseInfomation.CourseDictionary()
    er.setCourseInfo(course_info)
    er.courseExamQuestionGenerator(course_path_info)


    print ''