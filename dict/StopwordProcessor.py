
# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-08-17
program       : *_* process stop word  *_*

"""
import logging
#from tool import HanlpSplitor
class StopwordProcessor:
    """
    stop word processor 
    """
    def __init__(self):

        self.wordlist = []
        self.worddict = {}
        #self.splitor = HanlpSplitor.HanlpSplitor()

    def writeFile(self):
        logging.info('start write dictionary file.')
        fin = open('./../data/stopwords-pre-v20180817.txt', 'w+')
        fin.writelines(self.wordlist)
        fin.flush()
        fin.close()

    def readFile(self):

        words = open('./../data/stopwords.txt', 'r')
        ids_lines = words.readlines()
        for line in ids_lines:
            line = line.strip('\n')
            if line == '':
                continue
            if self.worddict.__contains__(line):
                continue
            self.worddict[line] = ''
            self.wordlist.append(line + '\n')


if __name__ == "__main__":
    sr = StopwordProcessor()
    sr.readFile()
    sr.writeFile()
    print 'split over'