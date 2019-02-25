# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-09-26
program       : *_*  change chinese num to digital num  *_*

"""
import re
import sys
from operator import itemgetter, attrgetter
reload(sys)
sys.setdefaultencoding('utf-8')


class MultiTree:
    """
    多叉树.

    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.schoolname = None
        self.coursename = None
        self.rootnode = TreeNode()

        # 维护一个字典，用于快速定位节点
        self.nodedict = {}
    def initTree(self, schoolname, coursename, coursecode):
        self.schoolname = schoolname
        self.coursename = coursename
        self.rootnode.name = coursename
        self.rootnode.code = coursecode

        self.nodedict[coursename] = self.rootnode

    def addNode(self, parentNode, name, level):
        if self.nodedict.__contains__(name):
            exist_node = self.nodedict[name]
            # 已经存在的节点，在下层，当前的level在上层，这个时候返回空，保持当前的层次在下层
            if exist_node.level >= level:
                exist_node = None
            return exist_node

        childNode = self.__createNode(parentNode,name, level)
        if parentNode is None:
            self.rootnode.addNode(childNode)

        else:
            parentNode.addNode(childNode)
            childNode.parent = parentNode

            self.nodedict[name] = childNode


        return childNode

    def __createNode(self,parentnode, name, level):
        n_node = TreeNode()
        n_node.name = name
        size = len(parentnode.children)
        n_node.code = parentnode.code + '.' + str(size + 1)
        n_node.level = level

        return n_node

    def findNode(self, nodename):
        res = None
        if self.nodedict.__contains__(nodename):
            res = self.nodedict[nodename]

        return res

    def findParentNode(self, curnode, nlevel):
        # 根据当前节点，往上面找，找到层级和nlevel相同的上级节点
        if curnode is None:
            return None
        res = None
        while curnode.parent:
            p_node = curnode.parent
            if nlevel == p_node.level:
                res = p_node.parent
                break
            elif nlevel > p_node.level:
                res = p_node
                break
            else:
                curnode = p_node
        if res is None:
            res = self.rootnode
        return res

    def sort(self):
        pass

class TreeNode:
    """
    树节点
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.name = None
        self.code = None
        self.level = 0
        self.children = []
        self.parent = None
        # 用于排序的序号
        self.seq = 0
        self.myid = None

    def addNode(self, node):
        self.children.append(node)


    def sort(self):
        # 按seq 序号排序
        #self.children = sorted(self.children, key=itemgetter(1))
        # 对象的比较 排序  cmp=lambda x,y : cmp(x[2], y[2])
        if len(self.children) > 1:
            self.children = sorted(self.children, cmp=lambda x,y: cmp(x.seq, y.seq))
