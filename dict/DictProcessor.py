
# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_* process dict file  *_*

"""
import logging
class DictProcessor:
    """
    file processor 
    """
    def __init__(self):

        self.wordlist = []

    def writeFile(self):
        logging.info('start write dictionary file.')
        fin = open('./../data/financial-dict-01.txt', 'w+')
        fin.writelines(self.wordlist)
        fin.flush()
        fin.close()

    def readFile(self):
        words = open('./../data/financial-dict.txt', 'r')
        # image_ids = open('image_ids', 'r')
        ids_lines = words.readlines()
        for line in ids_lines:
            line = line.strip('\n')
            if line == '':
                continue
            arr = line.split('；')
            for word in arr:
                #word = word.lstrip('“')
                #word = word.rstrip('”')
                word = word.lstrip(',')
                word = word.lstrip('&')
                if word.isdigit():
                    continue
                if word.__contains__('〔') or word.__contains__('(') or word.__contains__('…'):
                    continue
                length = len(word)
                if length > 15 or length < 4:
                    continue
                self.wordlist.append(word + '\n')


if __name__ == "__main__":
    sr = DictProcessor()
    sr.readFile()
    sr.writeFile()
    print 'split over'