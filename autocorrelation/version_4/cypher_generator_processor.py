# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-10-29
program       : *_*  将知识点和试题，生成cypher语句 *_*

"""

from domain import MD5
from domain import FilePath
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def generateKnowledgeCypher(course_path_info):
    """
    generate cypher 
    :return: 
    """
    cypherlist = []
    # 检查文件
    if not FilePath.fileExist(course_path_info.courseware_knowledge_txt_filepath):
        return cypherlist
    cypherlist.append("CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;")
    cypherlist.append("CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;")
    cypherlist.append("create index on:Question(databaseid);")
    # 读取知识点文件,到一个字典文件中
    # 知识点内部的关系，暂时仅建立父子之间的直接关系
    k_dict = {}
    f_k = open(course_path_info.courseware_knowledge_txt_filepath, 'r')
    for k in f_k:
        k = k.strip('\n')
        k_arr = k.split(' ')
        if len(k_arr) < 2:
            continue
        k_dict[k_arr[0]] = k_arr[1]

    # 建立父子关系
    for k_code, k_name in k_dict.items():
        # 处理k_code，寻找上一级code
        k_code_arr = k_code.split('.')
        k_code_parent = '.'.join(k_code_arr[:-1])
        # 不存在父节点，就不用创建关系
        if not k_dict.__contains__(k_code_parent):
            continue
        # 存在父节点，创建父子关系
        k_name_parent = k_dict.get(k_code_parent)
        k_ns_child = "MERGE (k_child:Knowledge {{code:'{0}'}}) on create set k_child.name='{1}'".format(k_code, k_name)
        k_ns_parent = "MERGE (k_parent:Knowledge {{code:'{0}'}}) on create set k_parent.name='{1}'".format(k_code_parent, k_name_parent)
        k_ns_parent_child = "MERGE (k_parent)-[:CHILD]->(k_child);"

        com = k_ns_child + ' ' + k_ns_parent + ' ' + k_ns_parent_child
        cypherlist.append(com)

    return cypherlist


def generateExamAndKnowledgeCypher(course, exam_question_group_dict):
    """
    generate cypher 
    :return: 
    """
    # first make constraint
    # CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;
    # CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;
    # "MERGE ({0}:Knowledge {{code: '{1}'}})".format(node['key'],node['code'])
    # "MERGE ({0})-[:SOLVE]->({1})".format(knode['key'], qnode['key'])
    cypherlist = []
    if len(exam_question_group_dict.keys()) == 0:
        return cypherlist

    cypherlist.append("CREATE CONSTRAINT ON (c:Knowledge) ASSERT c.code IS UNIQUE;")
    cypherlist.append("CREATE CONSTRAINT ON (c:Question) ASSERT c.code IS UNIQUE;")
    cypherlist.append("create index on:Question(databaseid);")
    for item, subitem_list in exam_question_group_dict.items():
        exam_content = item.content
        if exam_content.startswith(u'<img'):
            continue

        # 试题组的关联
        for subitem in subitem_list:
            qns = "MERGE (q:Question {{code:'{0}'}}) on create set q.type='{1}', q.category='{2}',q.diff='{3}',q.coursename='{4}',q.courseid='{5}', q.databaseid='{6}', q.schoolname='{7}'".format(
                item.code, item.type, item.category, item.diff,
                course.NewCourseName, course.CourseCode, course.ItemBankID, course.SchoolCode)

            subqns = "MERGE (sq:Question {{code:'{0}'}}) on create set sq.type='{1}', sq.category='{2}',sq.diff='{3}',sq.coursename='{4}',sq.courseid='{5}', sq.databaseid='{6}', sq.schoolname='{7}'".format(
                subitem.code, subitem.type, subitem.category, subitem.diff,
                course.NewCourseName, course.CourseCode, course.ItemBankID, course.SchoolCode)

            rns = "MERGE (sq)-[:SAME]->(q);"

            com = qns + ' ' + subqns + ' ' + rns
            cypherlist.append(com)

        # 知识点与试题的关联
        k_list = item.knowledge_list
        for k in k_list:
            kname = None
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
            # kns = "MERGE (k:Knowledge {{code:'{0}',name: '{1}'}})".format(md5code, k)
            # qns = "MERGE (q:Question {{code: '{0}',type:'{1}', category:'{2}',diff:'{3}',coursename:'{4}',courseid:'{5}', databaseid:'{6}', schoolname:'{7}'}})".format(item['questionid'], item['questiontype'], item['questioncate'],item['questiondiff'],item['coursename'],item['courseid'],item['databaseid'],item['schoolname'])
            qns = "MERGE (q:Question {{code:'{0}'}}) on create set q.type='{1}', q.category='{2}',q.diff='{3}',q.coursename='{4}',q.courseid='{5}', q.databaseid='{6}', q.schoolname='{7}'".format(
                item.code, item.type, item.category, item.diff,
                course.NewCourseName, course.CourseCode, course.ItemBankID, course.SchoolCode)
            rns = "MERGE (k)-[:CHECK]->(q);"
            com = kns + ' ' + qns + ' ' + rns
            cypherlist.append(com)
    return cypherlist
