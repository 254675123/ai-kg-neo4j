# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-11-14
program       : *_*  save knowledge information *_*
"""
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from tool.httprequest import HttpRequester

class KnnCategory:
    """
        catalog information.
        """

    def __init__(self):
        """
        initialize local variables.
        """
        # 设置源文件，中间文件，结果文件的路径
        self.course_path_info = None
        pass

    def generate_train_file(self):

        # 加载训练文本，训练文本有2部分组成，一部分是分类目录，一部分是课程名称

        # 检查语料文件是否已经生成, 如果已经生成，则不用再生成
        #if  FilePath.fileExist(self.course_path_info.vector_corpus_txt_filepath):
        #    return
        # 打开语料文件，准备写入语料
        f_out = open(self.course_path_info.vector_corpus_txt_filepath, 'w')

        # 第一步先加载分类目录
        if self.course_path_info.courseware_source_txt_filepath:
            for c_line in self.sentence_reader.splitSentence(self.course_path_info.courseware_source_txt_filepath):
                f_out.write(' '.join(c_line))
                f_out.write('\n')


        # 第二步加载试题




        f_out.close()
