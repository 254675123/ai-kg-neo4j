# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-10-26
program       : *_*  将老师打标的试题和知识点，按课程编号整理，以方便与抽取的知识点进行合并 *_*

"""
from tool.reader import ExcelReader
from tool.convertor import UnicodeConvertor
from domain import CourseInfomation
from domain import QuestionInformation
from domain import MD5
from tool.reader import ExcelWriter
import cypher_generator_processor
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class TeacherQuestionProcessor:
    """
    将老师打标的试题和知识点，按课程编号整理，以方便与抽取的知识点进行合并
    """
    def __init__(self):
        """
        定义变量
        """
        # 读取excel文件对象
        self.excel_reader = ExcelReader.ExcelReader()

        # 保存读取excel内容的字典对象
        self.course_exam_dict = {}

        # 试题编号对应知识点的字典
        self.exam_knowledge_dict = {}
        # 是否测试
        self.isTest = False



    def getCourseKnwoledgeByTeacher(self, course_id):
        """
        指定course_id，获取该课程的知识点
        :param course_id: 
        :return: 
        """
        k_list = []
        if not self.course_exam_dict.__contains__(course_id):
            return k_list

        row_list = self.course_exam_dict.get(course_id)
        for row in row_list:
            k_list.append(row[2])

        return k_list

    def getExamKnwoledgeByTeacher(self, exam_id):
        """
        指定exam_id，获取该的知识点
        :param course_id: 
        :return: 
        """
        if not self.exam_knowledge_dict.__contains__(exam_id):
            return None
        k_desc = self.exam_knowledge_dict.get(exam_id)
        return k_desc

    def getExamKnwoledgeByTeacher_split(self, exam_id):
        """
        指定exam_id，获取该的知识点
        :param course_id: 
        :return: 
        """
        k_list = []
        if not self.exam_knowledge_dict.__contains__(exam_id):
            return k_list
        k_desc = self.exam_knowledge_dict.get(exam_id)
        k_desc_list = k_desc.split(';')
        for k in k_desc_list:
            k_list.append(k)
        return k_list

    def get_course_exam_dict(self, root_path):
        """
        读取文件夹下面老师打标的excel文件，按课程编号组合成字典返回
        :param root_path: 
        :return: 
        """
        print '开始读取老师打标数据'
        file_path_list = self.get_filename_from_dir(root_path)
        file_index = 0
        file_total = len(file_path_list)
        for file_path in file_path_list:
            print '正在读取第{}/{}篇文件'.format(file_index, file_total)
            print '{}'.format(file_path)
            file_index += 1
            excel_content_rows = self.read_excel_file(file_path)
            # 如果没有内容，或者内容不够的，提示后，跳过
            if len(excel_content_rows) == 0 or len(excel_content_rows[0]) < 3:
                print '文件{}内容不符合规范，无法有效读取内容，已跳过。'.format(file_path)
                continue

            # 内容有效，将数据放入字典
            self.__set_course_exam_dict(excel_content_rows)

            # 测试用
            # if self.isTest == True:
            #     break
        print '结束读取老师打标数据'
        #return self.course_exam_dict, self.exam_knowledge_dict

    def __set_course_exam_dict(self, excel_content_rows):
        """
        设置数据到字典中
        :param excel_content_rows: 
        :return: 
        """
        for row in excel_content_rows:
            if len(str(row[0])) == 0 or len(str(row[1]))==0 or len(str(row[2]))== 0:
                continue
            # 课程编号
            course_id = int(row[0])
            course_code = u'{}'.format(course_id)
            if self.course_exam_dict.__contains__(course_code):
                exam_list = self.course_exam_dict.get(course_code)
                exam_list.append(row)
            else:
                exam_list = []
                exam_list.append(row)
                self.course_exam_dict[course_code] = exam_list

            # 试题编号与知识点对应
            exam_id = row[1]
            if self.exam_knowledge_dict.__contains__(exam_id):
                print '试题编号重复'
            else:
                self.exam_knowledge_dict[exam_id] = row[2]

    def read_excel_file(self, file_path):
        """
        读取excel文件，指定sheet和column，读取对应内容
        :param file_path: 
        :return: 
        """
        # 读取指定的文件和sheet范围
        self.excel_reader.filepath = file_path
        #self.excel_reader.sheet_scope_indexes = [0]
        # 定义一个question对象

        # 指定列的范围 = [u'课程编号', u'试题编号', u'标注知识点']
        self.excel_reader.column_scope_names = {u'课程编号':-1, u'试题编号':-1, u'标注知识点':-1}
        excel_content_rows = self.excel_reader.readFile()

        return excel_content_rows

    def get_filename_from_dir(self, dir_path):
        """
        获取文件夹下面的文件信息
        :param dir_path: 
        :return: 
        """
        file_list = []
        if not os.path.exists(dir_path):
            return file_list

        for sub_dir_name in os.listdir(dir_path):
            # sub_dir_name 子文件夹名称
            sub_dir_path = '{}/{}'.format(dir_path, sub_dir_name)
            for item in os.listdir(sub_dir_path):
                basename = os.path.basename(item)
                # print(chardet.detect(basename))   # 找出文件名编码,文件名包含有中文
                if basename.__contains__('~'):  # 临时文件不要
                    continue
                # windows下文件编码为GB2312，linux下为utf-8
                try:
                    decode_str = basename.decode("GBK")
                    # decode_str = basename.decode("GB2312")
                except UnicodeDecodeError:
                    decode_str = basename.decode("utf-8")

                file_path = u'{}/{}'.format(sub_dir_path, decode_str)
                file_list.append(file_path)

        return file_list

if __name__ == '__main__':

    rootpath = './../../data/course-knowledge-teacher'
    tqp = TeacherQuestionProcessor()
    tqp.get_course_exam_dict(rootpath)