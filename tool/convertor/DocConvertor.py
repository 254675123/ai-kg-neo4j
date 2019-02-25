# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-09-25
program       : *_* convert doc to docx  *_*

"""
import sys
import pickle
import re
import  codecs
import string
import shutil



class DocConvertor:
    """
        convert doc to docx.
        """

    def __init__(self):
        """
        initialize data
        """
        self.filepath = None
        self.result = []
