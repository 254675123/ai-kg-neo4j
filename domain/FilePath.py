# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-10-11
program       : *_*  define course information *_*
"""
import os
def mkdir(path):
    # 引入模块


    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)

        #print path + ' 创建成功'
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        #print path + ' 目录已存在'
        return False


def fileExist(filepath):
    """
    os模块中的os.path.exists()方法用于检验文件是否存在。
    其实这种方法还是有个问题，假设你想检查文件“test_data”是否存在，
    但是当前路径下有个叫“test_data”的文件夹，这样就可能出现误判。为了避免这样的情况，可以这样:
    只检查文件os.path.isfile("test-data")
    通过这个方法，如果文件”test-data”不存在将返回False，反之返回True。
    即是文件存在，你可能还需要判断文件是否可进行读写操作。
    使用os.access()方法判断文件是否可进行读写操作。
    os.access(path, mode), path为文件路径，mode为操作模式，有这么几种:
    os.F_OK: 检查文件是否存在;
    os.R_OK: 检查文件是否可读;
    os.W_OK: 检查文件是否可以写入;
    os.X_OK: 检查文件是否可以执行
    :param filepath: 
    :return: 
    """
    isExist = os.path.exists(filepath)
    isFile = os.path.isfile(filepath)
    if isExist and isFile:
        return True
    else:
        return False

# 定义要创建的目录
#mkpath = "d:\\qttc\\web\\"
# 调用函数
#mkdir(mkpath)