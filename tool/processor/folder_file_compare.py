
# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-08-23
program       : *_*  auto correlate the subject and the knowledge *_*

"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os

def get_filename_from_dir(dir_path):
    file_list = []
    if not os.path.exists(dir_path):
        return file_list

    for item in os.listdir(dir_path):
        basename = os.path.basename(item)
        # print(chardet.detect(basename))   # 找出文件名编码,文件名包含有中文

        # windows下文件编码为GB2312，linux下为utf-8
        try:
            decode_str = basename.decode("GBK")
            # decode_str = basename.decode("GB2312")
        except UnicodeDecodeError:
            decode_str = basename.decode("utf-8")

        file_list.append(decode_str)

    return file_list


def compare():
    folder1 = u'D:/pythonproject/open-neo4j-service/data/course-knowledge-machine/20181026-600plus/c-docx'
    folder2 = u'D:/奥鹏/学生服务中心标注/文科课程电子辅导资料第一批600plus-doc'

    folder1_file_list = get_filename_from_dir(folder1)
    folder2_file_list = get_filename_from_dir(folder2)
    file_name_dict = {}
    for file1 in folder1_file_list:
        file_name = os.path.splitext(file1)[0]
        file_name_dict[file_name] = None

    for file2 in folder2_file_list:
        arr = os.path.splitext(file2)
        file_name = arr[0]
        file_ext = arr[1]
        if file_name_dict.__contains__(file_name):
            continue
        if file_ext == u'.pdf':
            continue
        file_name = file_name.replace(u'（', u'(')
        file_name = file_name.replace(u'）', u')')
        if file_name_dict.__contains__(file_name):
            continue
        print file2



compare()