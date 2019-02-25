# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-12-11
program       : *_* delete knowledge from database *_*

"""
import os
import sys

from tool.saver import KnowledgeSaver
from domain import FilePath
from domain import KnowledgeInformation
reload(sys)
sys.setdefaultencoding('utf-8')

class KnowledgeDeleter:
    """
    delete knowledge data from dababase.
    """

    def __init__(self):
        """
        initialize local variables.
        """

        # 已经处理的文件
        self.processed_file = []

    def execute(self, filepath):
        """
        批量处理多个课程的知识点保存工作
        :return: 
        """

        # 逐个课程处理
        # 首先指定根目录位置,从该目录读取excel课件
        rootpath = u'./../../../data/course-knowledge-machine/{}/c-kwg-txt'.format(filepath)
        saved_filepath = u'./../../../data/course-knowledge-machine/{}/knowledge-save'.format(filepath)

        # os.walk(path)这个函数得到的结果是一个或多个tuple，
        # 个数取决于路径下是否有文件夹：如果没有文件夹的话，那么只有一个tuple，如果有的话，
        # 假如有3个，那么就会有4个tuple。
        # 而每个tuple中有三项：
        # 1.当前文件夹的路径(str类型）
        # 2.当前文件夹中的所有文件夹名称（list类型）
        # 3.当前文件夹中所有文件的名称
        # 所以，当只需要遍历当前文件夹下的文件时，只需要取出i[2]即可。
        self.loadProcessedFile(saved_filepath)

        # 这里的for是为了处理文件夹的嵌套，如果只有根目录是文件夹，那么for就执行一次。
        count = 0
        for item in os.walk(rootpath):
            filelist = item[2]

            # 然后是对每一个文件进行处理
            for f1 in filelist:
                if f1.startswith('~'):
                    continue
                #f1 = f.decode('gbk', 'ignore')
                if self.processed_file.__contains__(f1):
                    continue


                print '开始处理:' + f1
                count = count + 1
                sourcefilepath = rootpath + '/' + f1
                # if count < 77:
                #    continue
                k_list = []
                # 遍历文件夹，生成所有数据
                f_input = open(sourcefilepath, 'r')
                for line in f_input:
                    k = KnowledgeInformation.Knowledge()
                    k.initByString(line.strip())
                    k_list.append(k.toDict())

                self.saveProcessedFile(saved_filepath, f1)
                print '第{0}篇 课程：{1} 处理完成；'.format(count, f1)

        print '所有课程处理完毕，共处理：{0}篇'.format(count)
        print  '未读取到数据的文件有：'

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

if __name__ == "__main__":
    deleter = KnowledgeDeleter()
    #filepath = u'20181122-200plus'
    filepath = u'20181217-800plus-combine'
    deleter.execute(filepath)