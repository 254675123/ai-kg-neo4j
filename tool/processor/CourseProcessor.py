# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-06
program       : *_* read excel data  *_*

"""
from domain import CourseInfomation
from tool.reader import ExcelReader


class CourseProcessor:
    """
    课程信息得相关处理
    
    """


    def __init__(self, course_source_filename):
        """
        initialize data
        """
        # course对象
        self.course_info = CourseInfomation.CourseDictionary(course_source_filename)
        self.excel_reader = ExcelReader.ExcelReader()

    def getCourseInformationList(self, course_id_list):
        """
        通过课程的id列表，获取课程的完全信息，包括名称，所在院校，题库信息等
        :param course_id_list: 
        :return: 
        """
        result_list = []

        course_code_dict = self.course_info.course_code_dict
        for course_items in course_id_list:
            course_id = long(course_items[0])
            course_id = str(course_id).decode('utf-8')
            if course_code_dict.__contains__(course_id):
                course = course_code_dict.get(course_id)
                course_info = course.toString()
                result_list.append(course_info)
        return result_list

    def getCourseInformationDict(self, course_id_list):
        """
        通过课程的id列表，获取课程的完全信息，包括名称，所在院校，题库信息等
        :param course_id_list: 
        :return: 
        """
        result_dict = {}

        course_code_dict = self.course_info.course_code_dict
        for course_items in course_id_list:
            course_id = long(course_items[0])
            course_id = str(course_id).decode('utf-8')
            if course_code_dict.__contains__(course_id):
                course = course_code_dict.get(course_id)
                course_name = course.NewCourseName
                course_name = str(course_name).replace(u'（', u'(')
                course_name = str(course_name).replace(u'）', u')')
                result_dict[course.SchoolName+course_name] = course
        return result_dict


    def outputfile(self, filepath, result_list):
        # 输出文档
        fout = open(filepath, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(result_list))

        fout.close()

    def getNeedCourseList(self, filepath):
        self.excel_reader.filepath = filepath
        self.excel_reader.sheet_scope_indexes = [0]
        self.excel_reader.column_scope_indexes = [1]
        course_id_list = self.excel_reader.readFile()
        result_list = self.getCourseInformationList(course_id_list)

        return result_list

    def getNeedCourseDict(self, filepath):
        self.excel_reader.filepath = filepath
        self.excel_reader.sheet_scope_indexes = [0]
        self.excel_reader.column_scope_indexes = [1]
        course_id_list = self.excel_reader.readFile()
        result_dict = self.getCourseInformationDict(course_id_list)

        return result_dict

if __name__ == "__main__":
    cp = CourseProcessor()
    cp.excel_reader.filepath = u'D:/奥鹏/学生服务中心标注/course-scope-200plus-20181122.xlsx'
    cp.excel_reader.sheet_scope_indexes = [0]
    cp.excel_reader.column_scope_indexes = [1]
    course_id_list = cp.excel_reader.readFile()
    result_list = cp.getCourseInformationList(course_id_list)
    out_filepath = u'D:/奥鹏/学生服务中心标注/文科课程系统自动打标签列表-20181122.txt'
    cp.outputfile(out_filepath,result_list)

    print 'over'