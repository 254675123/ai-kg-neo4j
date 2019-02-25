# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-08-15
program       : *_* sentence reader  *_*

课程名称处理，从5万多门课程中，筛选出基础课程名称

"""
import sys

from tool.convertor import UnicodeConvertor
from tool.splitor import HanlpSplitor

reload(sys)
sys.setdefaultencoding('utf-8')

class CoursePreprocess:
    """
    read sentence one by one.
    """

    def __init__(self):
        """
        initialize local variables.
        """
        # 标点符号与数字集，用于分割句子
        self.__splitwords = "[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:：“”。？~@#￥%……&*（）]+"
        self.__pattern = r'(第[一二三四五六七八九十零0123456789]+章)|(第[一二三四五六七八九十零0123456789]+节)|(附录[一二三四五六七八九十]*)'
        self.splitor = HanlpSplitor.HanlpSplitor()
        # 统计词得总数
        # 裁剪后的课程名称
        self.coursenameAftdict = {}
        # 裁剪前的课程名称
        self.coursenamePredict = {}
        # 无法处理的课程名称
        self.coursenameErrdict = {}
        self.outputerrfile = './../data/course-err-pre.txt'
        self.outputbasefile = './../data/course-baselist-pre.txt'
        self.outputfile = './../data/course-list-pre.txt'

    def readcoursename(self):
        courselist = []
        f_file = open('./../data/course-list.txt', 'r')
        count = 0
        for eachWord in f_file:
            count += 1
            eachWord = eachWord.strip()
            if eachWord == '':
                continue
            eachWord = eachWord.decode('utf-8', 'ignore')
            if self.coursenamePredict.__contains__(eachWord):
                continue
            else:
                self.coursenamePredict[eachWord] = ''

            # 分析课程名字的主要部分，如果后面是符号，或者是数字，则前面的部分为主要部分
            # 课程名有繁体名称，需要对名称做繁体转简体
            simple_sentence = self.splitor.simplechinese(eachWord)
            #simple_sentence = simple_sentence.decode('utf-8', 'ignore')
            coursename = self.getCourseName(simple_sentence)
            if coursename == '':
                continue
            if not self.coursenameAftdict.__contains__(coursename):
                self.coursenameAftdict[coursename] = ''
            # 拼音转换
            pinyin = self.splitor.pinyin(simple_sentence)
            #length = len(eachWord)
            tup = (coursename, eachWord, pinyin)
            courselist.append(tup)
            #self.stopwords[eachWord] = eachWord

            if count%1000 == 0 :
                print 'has processed {0} rows.'.format(count)

        # 关闭文件
        f_file.close()
        print 'start write result.'
        # 对列表按拼音升序排
        courselist = sorted(courselist, cmp=lambda x, y: cmp(x[2], y[2]))

        self.outputerrname()
        self.output(courselist)
        self.outputbasename()


    def getCourseName(self, course):

        course_chlist = []
        # 如果开头不是中文的，都作为不符合规则处理，需要人为参与
        startch = course[0]
        if not UnicodeConvertor.is_chinese(startch):
            if not self.coursenameErrdict.__contains__(course):
                self.coursenameErrdict[course] = ''
            return ''

        # 如果名称中包含中文的逗号，冒号，引号等特殊符号，需要人工处理
        if course.__contains__('，') or course.__contains__('：') or \
            course.__contains__('、') or course.__contains__('——') or \
            course.__contains__('《') or course.__contains__('“') or course.__contains__('【') :
            if not self.coursenameErrdict.__contains__(course):
                self.coursenameErrdict[course] = ''
            return ''


        # 如果名字有中文横线－，则取最后一段
        arr = course.split('－')
        if len(arr) > 1:
            course = arr[-1]
        arr = course.split('—')
        if len(arr) > 1:
            course = arr[-1]
        arr1 = course.split('-')
        if len(arr1) > 1:
            course = arr1[-1]

        # 如果名字中有中文逗号，或者顿号，或者引号等，无法处理的


        prech = ''
        prech2 = ''
        engword = []
        for ch in course:

            # 如果是汉字，添加到列表，继续
            if UnicodeConvertor.is_chinese(ch):
                if prech2.isalpha() and len(engword) > 0:
                    course_chlist.append(''.join(engword))
                    engword = []
                course_chlist.append(ch)
            elif ch.isdigit():
                break
            elif ch.isalpha():
                engword.append(ch)
            else:
                break
            # 如果是数字或者符号，则结束
            #elif ch == '+' and (prech == '+' or prech.isalpha()):
            #    course_chlist.append(ch)

            prech = ch
            prech2 = prech
        # 如果名称末尾有上、下的，可以去掉
        if len(course_chlist) > 0 and \
                (course_chlist[-1] == u'上' or course_chlist[-1] == u'下' or
                         course_chlist[-1] == u'一' or course_chlist[-1] == u'二' or
                         course_chlist[-1] == u'三' or course_chlist[-1] == u'四' or
                         course_chlist[-1] == u'五' or course_chlist[-1] == u'六' or
                         course_chlist[-1] == u'七' or course_chlist[-1] == u'八' or
                         course_chlist[-1] == u'九' or course_chlist[-1] == u'十'
                 ):
            del course_chlist[-1]
        if len(engword) > 1:
            course_chlist.append(''.join(engword))

        # 返回课程名字
        return ''.join(course_chlist)

    def outputerrname(self):

        fout = open(self.outputerrfile, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(self.coursenameErrdict.keys()))  # 将分词好的结果写入到输出文件
        fout.close()

    def outputbasename(self):

        fout = open(self.outputbasefile, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(self.coursenameAftdict.keys()))  # 将分词好的结果写入到输出文件
        fout.close()

    def output(self, courselist):
        index = 0
        wordlst = []
        for tup in courselist:

            ns = '{0} {1} {2}'.format(tup[0],tup[1], tup[2])
            wordlst.append(ns)


        fout = open(self.outputfile, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(wordlst))  # 将分词好的结果写入到输出文件
        fout.close()





if __name__ == "__main__":
    sr = CoursePreprocess()
    #sr.splitSentence('./../data/financial-course.txt')
    #for sentence in sr.getSentence('./../data/financial-course.txt'):
    #    print sentence
    sentence = u'愛節約的小寶寶'
    nn = sr.splitor.simplechinese(sentence)
    sr.readcoursename()


    print 'split over'