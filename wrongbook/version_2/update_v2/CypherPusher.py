# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-09
program       : *_* push cyhper data to neo4j *_*

"""
import os
import sys

from database import Neo4jHandler
from domain import FilePath

reload(sys)
sys.setdefaultencoding('utf-8')

class CypherPusher:
    """
    push data to neo4j.
    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)
        # 从文件中没有读取出数据的文件列表
        self.emptyfile_list = []

        # 已经处理的文件
        self.processed_file = []

        # 排除的文件，这些文件有问题
        self.exclude_files = []



    def executePush(self, filepath):
        """
        批量处理多个课程的自动关联工作
        :return: 
        """

        # 指定一个文件夹，该文件夹用来存放多个课程的excel题库
        # 逐个课程处理
        # 首先指定根目录位置,从该目录读取excel课件
        rootpath = u'./../../../data/course-knowledge-machine/{}/cypher-txt'.format(filepath)
        out_filepath = u'./../../../data/course-knowledge-machine/{}/processed_cypher'.format(filepath)
        exclude_filepath = u'./../../../data/course-knowledge-machine/{}/bad-english-or-imgage'.format(filepath)
        # os.walk(path)这个函数得到的结果是一个或多个tuple，
        # 个数取决于路径下是否有文件夹：如果没有文件夹的话，那么只有一个tuple，如果有的话，
        # 假如有3个，那么就会有4个tuple。
        # 而每个tuple中有三项：
        # 1.当前文件夹的路径(str类型）
        # 2.当前文件夹中的所有文件夹名称（list类型）
        # 3.当前文件夹中所有文件的名称
        # 所以，当只需要遍历当前文件夹下的文件时，只需要取出i[2]即可。
        self.loadProcessedFile(out_filepath)
        self.loadExcludeFile(exclude_filepath)
        # 这里的for是为了处理文件夹的嵌套，如果只有根目录是文件夹，那么for就执行一次。
        count = 0
        for item in os.walk(rootpath):
            filelist = item[2]

            # 然后是对每一个文件进行处理
            for f in filelist:
                if f.startswith('~'):
                    continue
                #f1 = f.decode('gbk', 'ignore')
                if self.processed_file.__contains__(f):
                    continue
                if self.exclude_files.__contains__(f):
                    continue

                print '开始处理:' + f
                count = count + 1
                sourcefilepath = rootpath + '/' + f
                #if count < 77:
                #    continue
                # 遍历文件夹，生成所有数据
                cypherstatement = self.getCourseCypher(sourcefilepath)
                if len(cypherstatement) == 0:
                    self.emptyfile_list.append(f)
                else:
                    #pass
                    self.neo4jdriver.cypherexecuterlist(cypherstatement)

                self.saveProcessedFile(out_filepath, f)
                print '第{0}篇 课程：{1} 处理完成；'.format(count, f)

        print '所有课程处理完毕，共处理：{0}篇'.format(count)
        print  '未读取到数据的文件有：'
        for empty_filename in self.emptyfile_list:
            print empty_filename
        print 'push over.'

    def saveProcessedFile(self, filepath, data):
        f_out = open(filepath, 'a')
        f_out.write(data)
        f_out.write('\n')
        f_out.close()

    def loadProcessedFile(self, filepath):
        if not FilePath.fileExist(filepath):
            return
        f_input = open(filepath, 'r')
        for fname in f_input:
            fname = fname.strip('\n')
            if len(fname) == 0:
                continue
            self.processed_file.append(fname)

    def loadExcludeFile(self, filepath):
        for item in os.walk(filepath):
            filelist = item[2]

            # 然后是对每一个文件名称进行处理
            for f in filelist:
                coursename = os.path.splitext(f)[0]
                self.exclude_files.append(coursename)

    def getCourseCypher(self, filepath):
        """
        读取课程的cypher语句
        :param filepath: 
        :return: 
        """
        cypherlist = []

        f_cypher = open(filepath, 'r')
        for line in f_cypher:
            cypherlist.append(line)

        return cypherlist

if __name__ == "__main__":
    pusher = CypherPusher()
    #filepath = u'20181122-200plus'
    filepath = u'20181217-800plus-combine'
    # 知识点内部关系构建
    # 知识点与试题的关联构建
    pusher.executePush(filepath)