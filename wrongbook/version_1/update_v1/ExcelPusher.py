# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-09
program       : *_* push excel data to neo4j *_*

"""
import os
import sys

from database import Neo4jHandler
from tool.reader import ExcelReader_v1

reload(sys)
sys.setdefaultencoding('utf-8')

class ExcelPusher:
    """
    push data to neo4j.
    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.__sleep_time_per_request = 0.01
        self.__sleep_time_per_request_none = 180.00
        self.__sleep_time_per_loop = 60

        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)
        self.reader = ExcelReader_v1.ExcelReader()
        # 从文件中没有读取出数据的文件列表
        self.emptyfile_list = []

    def executePush(self, directory_name):
        """
        批量处理多个课程的自动关联工作
        :return: 
        """

        # 指定一个文件夹，该文件夹用来存放多个课程的excel题库
        # 逐个课程处理
        # 首先指定根目录位置,从该目录读取excel课件
        rootpath = './../../../data/course-knowledge-teacher/{}'.format(directory_name)
        # os.walk(path)这个函数得到的结果是一个或多个tuple，
        # 个数取决于路径下是否有文件夹：如果没有文件夹的话，那么只有一个tuple，如果有的话，
        # 假如有3个，那么就会有4个tuple。
        # 而每个tuple中有三项：
        # 1.当前文件夹的路径(str类型）
        # 2.当前文件夹中的所有文件夹名称（list类型）
        # 3.当前文件夹中所有文件的名称
        # 所以，当只需要遍历当前文件夹下的文件时，只需要取出i[2]即可。

        # 这里的for是为了处理文件夹的嵌套，如果只有根目录是文件夹，那么for就执行一次。
        count = 0
        for item in os.walk(rootpath):
            filelist = item[2]

            # 然后是对每一个文件进行处理
            for f in filelist:
                if f.startswith('~'):
                    continue
                f1 = f.decode('gbk', 'ignore')
                print '开始处理:' + f1
                count = count + 1
                sourcefilepath = rootpath + '/' + f1
                #if count < 77:
                #    continue
                # 遍历文件夹，生成所有数据
                cypherstatement = self.reader.getCourseCypher(sourcefilepath)
                if len(cypherstatement) == 0:
                    self.emptyfile_list.append(f1)
                else:
                    #pass
                    self.neo4jdriver.cypherexecuterlist(cypherstatement)

                print '第{0}篇 课程：{1} 处理完成；'.format(count, f1)

        print '所有课程处理完毕，共处理：{0}篇'.format(count)
        print  '未读取到数据的文件有：'
        for empty_filename in self.emptyfile_list:
            print empty_filename
        print 'push over.'


if __name__ == "__main__":
    pusher = ExcelPusher()
    directory_list = []
    directory_list.append('course-subject-2018912')
    directory_list.append('course-subject-2018913')
    directory_list.append('course-subject-2018918')
    directory_list.append('course-subject-20181011')
    directory_list.append('course-subject-20181114')
    directory_list.append('course-subject-20181116')
    directory_list.append('course-subject-20181116-1')
    directory_list.append('course-subject-20181116-2')
    for directory_name in directory_list:
        pusher.executePush(directory_name)