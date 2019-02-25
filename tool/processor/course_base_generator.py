# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-12-17
program       : *_* read excel data  *_*

"""
from domain import CourseInfomation
from tool.reader import ExcelReader
from domain import FilePath

class CourseBaseGenerator:
    """
    基础课程信息得相关处理

    """

    def __init__(self, course_source_filename):
        """
        initialize data
        """

        # course对象
        self.course_info = CourseInfomation.CourseDictionary(course_source_filename)
        self.excel_reader = ExcelReader.ExcelReader()

        self.course_base_dict = {}
        self.course_base_list = []
        self.current_base_course = None
        self.max_index = 0

    def getCourseInformationList(self, course_id_list):
        """
        通过课程的id列表，获取课程的完全信息，包括名称，所在院校，题库信息等
        :param course_id_list: 
        :return: 
        """
        result_list = []

        course_code_dict = self.course_info.course_code_dict
        for course_items in course_id_list:
            course_code = long(course_items[0])
            course_base_name = course_items[1]
            course_code = str(course_code).decode('utf-8')
            if course_code_dict.__contains__(course_code):
                course = course_code_dict.get(course_code)
                # 对course设置基础课程名称和编码
                course.coursebase_name = course_base_name
                self.generateCourseBaseCode(course)

                course_info = course.toStringByColumns()
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
                result_dict[course.SchoolName + course_name] = course
        return result_dict

    def outputfile(self, filepath, result_list):
        # 输出文档
        fout = open(filepath, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(result_list))

        fout.close()

    def loadBaseCourse(self, base_course_file):
        if not FilePath.fileExist(base_course_file):
            return
        f_input = open(base_course_file, 'r')
        for line in f_input:
            line = line.strip('\n')
            cb = CourseInfomation.CourseBase()
            cb.initByString(line)
            self.course_base_list.append(cb)
            self.current_base_course = cb

    def generateCourseBaseCode(self, course):
        index = 0
        if self.course_base_dict.__contains__(course.coursebase_name):
            self.current_base_course = self.course_base_dict.get(course.coursebase_name)
            course.coursebase_code = self.current_base_course.coursebase_code
            course.coursebase_index = self.current_base_course.coursebase_index
        else:
            if self.current_base_course is None:
                index = 1

            else:
                index = self.current_base_course.coursebase_index

            if self.max_index >= index:
                self.max_index += 1
            else:
                self.max_index = index

            course.coursebase_code = 'open.bc.' + str(self.max_index)
            course.coursebase_index = self.max_index

            # 课程基础
            cb = CourseInfomation.CourseBase()
            cb.coursebase_code = course.coursebase_code
            cb.coursebase_name = course.coursebase_name
            cb.coursebase_index = course.coursebase_index
            self.course_base_dict[cb.coursebase_name] = cb

            self.current_base_course = cb

if __name__ == "__main__":
    course_source_file = 'course-20181026.txt'
    cp = CourseBaseGenerator(course_source_file)
    cp.excel_reader.filepath = u'D:/奥鹏/开发成果/错题本/错题本巩固练习--题库打通-2.xlsx'
    out_filepath = u'D:/奥鹏/开发成果/错题本/基础课程信息表生成-20190211.txt'
    cp.loadBaseCourse(out_filepath)
    cp.excel_reader.sheet_scope_indexes = [0]
    cp.excel_reader.column_scope_indexes = [0,3]
    course_id_list = cp.excel_reader.readFile()
    result_list = cp.getCourseInformationList(course_id_list)
    cp.outputfile(out_filepath, result_list)

    print 'over'