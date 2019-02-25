# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-09-26
program       : *_*  extract knowledge from docx  *_*

"""
import os
import sys

import TreeFactory

reload(sys)
sys.setdefaultencoding('utf-8')

class ExtractFromDocx:
    """
    extract knowledge from docx.
    
    抽取规则说明
    1. 开头位置有院校名字和课程名字，作为知识点的标签
    
    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.inputfilepath = None
        self.outputfilepath = None
        self.outputmidfilepath = None
        self.treefactory = TreeFactory.TreeFactory()

        self.targetfile_list = []

    def batchProcessDocx(self):
        """
        批量处理多个课程的自动关联工作
        :return: 
        """

        # 指定一个文件夹，该文件夹用来存放多个课程的docx课件
        # 逐个课件处理
        # 首先指定根目录位置,从该目录读取docx课件
        rootpath = self.inputfilepath

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
                #f1 = f.decode('gbk', 'ignore')
                print f
                #print f1

                count = count + 1
                sourcefilepath = self.inputfilepath + '/' + f
                targetfilepath = self.outputfilepath + '/' + f + '.txt'
                midfilepath = self.outputmidfilepath + '/' + f + '-mid.txt'
                self.targetfile_list.append(targetfilepath)
                self.treefactory.inputfile = sourcefilepath
                self.treefactory.outputfile = targetfilepath
                self.treefactory.outputmidfilepath = midfilepath
                self.treefactory.extractKnowledge()

                print '第{0}篇 课程：{1} 处理完成；'.format(count, f)

        print '所有课程处理完毕，共处理：{0}篇'.format(count)

        print '开始合并输出...'
        self.combineResultfile()
        print '合并输出完成。'

    def combineResultfile(self):
        """
        将结果文件合并，方便检查问题
        :return: 
        """
        targetfilepath = u'./../data/all.txt'
        fout = open(targetfilepath, 'w')
        for filepath in self.targetfile_list:
            ftemp = open(filepath, 'r')
            fout.write('\n')
            for line in ftemp:
                fout.write(line)
            ftemp.close()

        fout.close()

if __name__ == "__main__":
    sr = ExtractFromDocx()
    sr.inputfilepath = u'D:/奥鹏/学生服务中心标注/to 张超林--电子辅导资料第二批269门/'
    sr.outputfilepath = u'./../data/course-knowledge-tgt'
    sr.outputmidfilepath = u'./../data/course-knowledge-mid-docx'
    sr.batchProcessDocx()