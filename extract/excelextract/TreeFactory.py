# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-09-26
program       : *_*  generate tree  *_*

"""
import Queue
import re
import sys

import ExcelReader
from domain import CourseInfomation, MultiTree
from tool.convertor import CnNumConvertor

reload(sys)
sys.setdefaultencoding('utf-8')


class TreeFactory:
    """
    树工厂.

    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.courseinfo = CourseInfomation.CourseDictionary()
        #self.courseinfo.initDictionary(u'./../data/dictionary/course.txt')

        self.excelreader = ExcelReader.ExcelReader()

        self.re_num_0 = ur'(第[一二三四五六七八九零十百千万亿0123456789]+[章节讲])'
        self.pattern = re.compile(self.re_num_0)

        self.outputfile = u'./../data/course-knowledge-tgt/'

    def generateTree(self, filepath):
        self.excelreader.readFile(filepath)

        # 生成树列表
        tree_list = []
        for rootid in self.excelreader.result.keys():
            children_set = self.excelreader.result[rootid]
            tree = self.createTree(rootid,children_set)
            if tree is None:
                print 'cannot create the tree by root id : '+ str(rootid)
            else:
                tree_list.append(tree)

        # 将树列表输出文件
        print 'output to files.'
        self.outputfile = self.outputfile + 'combine.txt'
        for tree in tree_list:
            coursename = tree.coursename
            #self.outputfile = self.outputfile + coursename + '.txt'
            self.outputTree(tree)

    def createTree(self, parentid, children_set):
        tree = None
        if len(children_set) == 0:
            return tree
        coursename = children_set[0].coursename
        course = self.courseinfo.getCourseByCoursename(coursename)
        if course is None:
            return tree
        tree = MultiTree.MultiTree()
        tree.initTree(course.SchoolName,course.NewCourseName,course.CourseCode)

        # 遍历children set，从中找到parent id是当前id的，作为孩子，直到找不到为止
        # 把每个孩子都放到队列中，每次从队列中获取
        q = Queue.Queue()

        children = self.addQueue(q, parentid, children_set)
        self.createTreeNode(q, children, tree.rootnode)

        # 从队列中取一个，创建树
        while not q.empty():
            item = q.get()
            children = self.addQueue(q, item[0].myid,children_set)
            self.createTreeNode(q, children, item[1])

        return tree

    def createTreeNode(self, q, children, parentnode):
        for child in children:
            node = MultiTree.TreeNode()
            node.parent = parentnode
            name_arr = child.name.split(' ')
            if len(name_arr) > 1:

                node.name = name_arr[1]
                node.code = name_arr[0]
                if node.code.__contains__(u':'):
                    name_arr2 = node.code.split(u':')
                    node.code = name_arr2[0]
            else:
                node.name = name_arr[0]
                node.code = '0'
            node.seq = self.createSeq(node.code)
            node.myid = child.myid
            parentnode.children.append(node)

            q.put((child, node))
        # 完成添加后，对节点做一次排序
        parentnode.sort()

    def createSeq(self, code):
        print 'code:'+code
        seq = 0
        if len(code.strip()) == 0:
            return seq
        res = self.pattern.match(code)
        if res:
            content = res.group()
            cont_num = content.strip(u'第章节讲')
            if str(cont_num).isdigit():
                seq = int(cont_num)
            else:
                seq = CnNumConvertor.chinese2digits(cont_num)

        else:
            cont_num = code.replace('.', '')
            cont_num = cont_num.replace('-', '')
            if str(cont_num).isdigit():
                seq = int(cont_num)

        print 'seq:' + str(seq)

        return seq
    def addQueue(self, q, parentid, children_set):
        # 先查找当前父亲有没有孩子节点，如果有，则加到队列中
        candi_list = self.findChildren(parentid, children_set)
        return candi_list

    def findChildren(self, parentid, children_set):
        # 从孩子集合中，查到需要的孩子
        res = []
        for child in children_set:
            if child.parentid == parentid:
                res.append(child)

        return res

    def outputTree(self, tree):
        k_list = []
        self.getKwgFromTree(k_list, tree.rootnode)

        # 输出文档
        fout = open(self.outputfile, 'a')  # 以写得方式打开文件
        fout.write('\n')
        fout.write('\n'.join(k_list))  # 将结果写入到输出文件

        fout.close()
    def getKwgFromTree(self, k_list, node):
        if node is None:
            return

        k_list.append(node.code + ' ' +node.name)

        if len(node.children) > 0:
            for child in node.children:
                self.getKwgFromTree(k_list, child)


if __name__ == '__main__':
    #read_excel()
    er = TreeFactory()
    filepath = u'D:/奥鹏/运营平台-产品中心/课程下的课件目录.xlsx'
    er.generateTree(filepath)
    #er.readFile('D:/0701.xlsx')