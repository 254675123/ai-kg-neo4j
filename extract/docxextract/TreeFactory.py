# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-09-26
program       : *_*  generate tree  *_*

"""
import os
import re
import sys

from domain import MultiTree
from domain import CourseInfomation
from tool.convertor import UnicodeConvertor
from tool.processor import SentenceProcessor
from tool.reader import WordReader
from tool.reader import TextReader

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
        self.__curpath = os.path.dirname(os.path.realpath(__file__))
        self.course_filepath = None
        self.course_filepath_list = []
        self.prefixwords = []
        self.middlewords = []
        self.suffixwords = []
        self.stopwords = {}
        self.wordreader = WordReader.WordReader()
        self.preprocesser = SentenceProcessor.SenPreprocess()
        self.teacher_processor = None
        self.re_level = self.preprocesser.re_level
        #self.ngram = NGram.NGram()

        self.__initStopwords__()
        self.__initSuffixwords__()
        self.__initPrefixwords__()
        self.__initMiddlewords__()
        self.__init_re()
        pass

    def __init_re(self):
        # 定义正则
        # 对于疑问句，比如：有哪些？ 有什么区别？ 有什么联系？有什么关系？有什么影响？ 等等
        # 这种内容去掉
        self.re_ask = ur'(有.*?$)'
        self.re_replace_bracket = ur'([（(][^（()）]*?[)）])'
        self.re_replace_bracket_semi = ur'([（(].+)'
        self.re_replace_keyi = ur'(可以.*?为$)'

        self.re_nouse_tag_graphtable = ur'([图表][\s]*[0123456789]+)'
        self.re_nouse_tag_percent = ur'(\d{1,2}%)'
        self.re_nouse_tag_seq_1 = ur'(第[一二三四五六七八九零十百千万亿]+[类步]{0,1})'
        self.re_nouse_tag_seq_2 = ur'(例[0123456789]+)'
        self.re_nouse_tag_seq = [self.re_nouse_tag_seq_1, self.re_nouse_tag_seq_2]

    def __initStopwords__(self):
        fstop = open(self.__curpath+'/../../data/dictionary/stopwords-pre-v20180817.txt', 'r')
        for eachWord in fstop:
            eachWord = eachWord.strip()
            eachWord = eachWord.decode('utf-8', 'ignore')
            #length = len(eachWord)
            #tup = (eachWord, length)
            #self.stopwordlist.append(tup)
            self.stopwords[eachWord] = eachWord
        fstop.close()

    def __initSuffixwords__(self):
        fstop = open(self.__curpath+'/../../data/dictionary/remove_words_suffix.txt', 'r')

        for eachWord in fstop:
            eachWord = eachWord.strip()
            eachWord = eachWord.decode('utf-8', 'ignore')
            #length = len(eachWord)
            #tup = (eachWord, length)
            #self.stopwordlist.append(tup)
            self.suffixwords.append(eachWord)
        fstop.close()

    def __initPrefixwords__(self):
        fstop = open(self.__curpath+'/../../data/dictionary/remove_words_prefix.txt', 'r')

        for eachWord in fstop:
            eachWord = eachWord.strip()
            eachWord = eachWord.decode('utf-8', 'ignore')
            #length = len(eachWord)
            #tup = (eachWord, length)
            #self.stopwordlist.append(tup)
            self.prefixwords.append(eachWord)
        fstop.close()

    def __initMiddlewords__(self):
        fstop = open(self.__curpath+'/../../data/dictionary/remove_words_middle.txt', 'r')

        for eachWord in fstop:
            eachWord = eachWord.strip()
            eachWord = eachWord.decode('utf-8', 'ignore')
            #length = len(eachWord)
            #tup = (eachWord, length)
            #self.stopwordlist.append(tup)
            self.middlewords.append(eachWord)
        fstop.close()

    def getFileContentRows(self):
        """
        按源文件的类型，获取
        :return: 
        """
        result_content_rows = []
        if self.course_filepath is not None:
            self.course_filepath_list.append(self.course_filepath)

        for course_filepath_info in self.course_filepath_list:
            file_type = course_filepath_info.sourse_filetype
            if file_type is None:
                continue
            if file_type == course_filepath_info.type_docx:
                # 从word文档中读取文本的内容
                self.wordreader.input_filepath = course_filepath_info.courseware_source_docx_filepath
                self.wordreader.output_filepath = course_filepath_info.courseware_source_txt_filepath
                self.wordreader.readText()
                content_rows = self.wordreader.docx_content
                result_content_rows = result_content_rows + content_rows
            elif file_type == course_filepath_info.type_text:
                # 从txt文档中读取文本的内容
                txtreader = TextReader.TextReader()
                txtreader.filepath = course_filepath_info.courseware_source_txt_filepath
                txtreader.readText()
                content_rows = txtreader.content_rows
                result_content_rows = result_content_rows + content_rows
        return result_content_rows

    def getTeacherTagCourse(self):
        """
        获取老师打标记的课程id列表
        :return: 
        """
        teacher_kwg_list = []
        if self.teacher_processor is None:
            return teacher_kwg_list

        for course_path_info in self.course_filepath_list:
            course = course_path_info.course

            kwg_list = self.teacher_processor.getCourseKnwoledgeByTeacher(course.CourseCode)
            teacher_kwg_list += kwg_list

        return teacher_kwg_list

    def generatetree(self):
        # 开始读取数据
        print '开始读取数据...'
        content_rows = self.getFileContentRows()
        print '读取数据结束，共读取{}行.'.format(len(content_rows))

        # 对文本内容进行处理，只需要重点的部分，非重点不要
        print '开始预处理原始数据...'
        result = self.preprocesser.preprocess_content_rows(content_rows)
        content_count = len(result)
        print '预处理数据结束，处理后共有{}行.'.format(len(result))

        # 读取老师打标签的知识点
        teacher_kwg_list = self.getTeacherTagCourse()
        result += teacher_kwg_list
        # 如果没有重点内容，则抽取结束
        if len(result) == 0:
            return

        # 第二步，生成知识树
        # 设置知识点树的根节点，并设置树的院校名称、课程名称标签
        print '开始生成知识树...'
        tree = MultiTree.MultiTree()
        self.setSchoolAndCourse(tree, result)

        # 记录当前层
        preline_level = -1
        pre_curnode = None
        curnode = tree.rootnode
        reset_flag = False
        pre_reset_flag = False
        process_count = 0
        for line in result:
            process_count += 1
            print '正在处理第{}行'.format(process_count)
            if process_count <= content_count:
                # 如果是停用词，直接过
                line = line.strip()
                if self.stopwords.__contains__(line):
                    continue
                #
                line = self.preProcessSentence(line)
                if len(line) == 0:
                    continue

                # u'1、成本费用利润率：反映企业每付出单位成本费用，所能取得利润的能力。'
                if str(line).__contains__(u'控制结构——选择结构'):
                    print line
                # 判断层级
                nlevel, nline = self.judgeLevel(line)
                nline = self.postProcessSentence(nline)
                if nline == '':
                    continue

                if self.stopwords.__contains__(nline):
                    continue
            else:
                # 这些都是老师标注的知识点，不需要处理，直接作为知识点
                nlevel = 1  # 放在根节点的下面，1为章的层次，2为节的层次
                nline = line # 对保存的知识点不进行处理

            # 如果当前的行 和 前一行的level 是同一级的，则应该回复前一个节点
            if pre_reset_flag == False and reset_flag and nlevel > curnode.level and nlevel == preline_level:
                curnode = pre_curnode
                pre_curnode = pre_curnode.parent
            # 层级序号，0为最高层，数字越大，层级越低
            # 0. 如果层级为-1，暂时pass
            # 1. 如果新行的层级，比当前的层级低，则将新行作为当前节点的子节点
            # 2. 如果新行的层级，和当前的层级相同，则新行作为当前父节点的子节点
            # 3. 如果新行的层级，比当前的层级高，则需要往上返回，找到新行层级的上一层级
            if nlevel == -1:
                tree.addNode(curnode, nline, 100)
            elif nlevel > curnode.level:
                n_node = tree.addNode(curnode, nline, nlevel)
                reset_flag = self.getResetFlag(n_node, nlevel)
                # 将当前层次
                if n_node:
                    pre_curnode = curnode
                    curnode = n_node

            elif nlevel == curnode.level:
                n_node = tree.addNode(curnode.parent, nline, nlevel)
                reset_flag = self.getResetFlag(n_node, nlevel)
                # 因为层次相同，仅需要赋值当前节点
                if n_node:
                    pre_curnode = curnode
                    curnode = n_node

            elif nlevel < curnode.level:
                # 先直接找节点，如果有，则不用操作
                find_node = tree.findNode(nline)
                if find_node is None:
                    # 从树中查找当前节点，及其父节点
                    p_node = tree.findParentNode(curnode, nlevel)
                    if p_node is None:
                        continue
                    n_node = tree.addNode(p_node, nline, nlevel)
                    reset_flag = self.getResetFlag(n_node, nlevel)
                    if n_node:
                        pre_curnode = curnode
                        curnode = n_node
                else:
                    pre_curnode = curnode
                    curnode = find_node
            # 将当前行的level保存
            preline_level = nlevel
            pre_reset_flag = reset_flag
        print '知识树生成完成.'
        return tree

    def getResetFlag(self, node, nlevel):
        # 如果node的level 比nlevel的值小，则需要复位
        flag = False

        if node is None:
            return flag

        if node.level < nlevel:
            flag = True

        return flag

    def outputTree(self, tree):
        k_list = []
        self.getKwgFromTree(k_list, tree.rootnode)

        # 输出文档
        fout = open(self.course_filepath_list[0].courseware_knowledge_txt_filepath, 'w')  # 以写得方式打开文件
        fout.write('\n'.join(k_list))  # 将结果写入到输出文件
        fout.close()

    def getKwgFromTree(self, k_list, node):
        if node is None:
            return

        k_list.append(node.code + ' ' +node.name)

        if len(node.children) > 0:
            for child in node.children:
                self.getKwgFromTree(k_list, child)


    def judgeLevel(self, line):
        flag = False
        level = -1
        index = 0
        for re_pat in self.re_level:
            index = re_pat[1]
            pattern = re.compile(re_pat[0])
            res = pattern.match(line)
            if res:
                flag = True
                match_content = res.group()
                match_length = len(match_content)
                line = line[match_length:]
                #line = line.replace(match_content, '')

                break
        # 是否匹配了模式，如果没有匹配，level返回-1
        if flag :
            level = index



        return level, line

    def preProcessSentence(self, line):
        """
        原文本的文本处理
        :param line: 
        :return: 
        """

        # 文本中有日期的不要
        nline = self.preprocesser.removeByRegexPattern(self.preprocesser.re_date_remove, line)

        if len(nline) > 0:
            # 文本中有货币数字的不要
            nline = self.preprocesser.removeByRegexPattern(self.preprocesser.re_currency, nline)

        # 存在\ 或者 / 的用顿号替换
        nline = nline.replace(u'/', u'、')
        nline = nline.replace(u'\\', u'、')

        # 存在回车换行的，保留前一部分
        multi_lines = nline.split('\n')
        if len(multi_lines) > 1:
            nline = multi_lines[0]

        return nline

    def postProcessSentence(self, line):
        """
        去掉前缀的文本处理
        :param line: 
        :return: 
        """
        line = line.strip()
        line = line.strip(u'、：．，｛｝.,:{}')
        line = line.strip()

        # 去掉符合正则的部分
        line = self.removeReSection(line)

        # 可能还有前缀
        level, line = self.judgeLevel(line)
        # 去掉后缀词
        line = self.removeSuffixSection(line)
        # 去掉前缀词
        line = self.removePrefixSection(line)
        # 包含词的处理
        line = self.removeMiddleSection(line)
        # 对于有破折号,冒号，等号等部分进行处理
        line = self.parseDashSection(line)

        # 可能还有前缀
        level, line = self.judgeLevel(line)

        # 去掉中间空格
        line = self.preprocesser.removeMidSpace4Chinese(line)

        # 如果还有数字在里面，则去掉
        pattern_list = [self.preprocesser.re_nouse_number]
        line = self.preprocesser.removeByRegexPattern(pattern_list, line)

        # 如果长度大于20，并且包含逗号的，不要
        if len(line) > 20 and (line.__contains__(u',') or line.__contains__(u'，') or len(line) > 30):
            line = u''
        # 如果还有以特殊符号开头的，不要扔掉
        if len(line) > 0 and line[0] <> u'《' and line[0] <> u'“'  and (
            UnicodeConvertor.is_other(line[0]) or UnicodeConvertor.is_other(line[-1])):
            line = u''
        # 单引号在cypher语句中是有特殊涵义的
        if line.__contains__(u"'"):
            line = line.replace(u"'", u"’")

        line = line.strip()
        line = line.strip(u'、：．，｛｝.,:{}')
        line = line.strip()

        if len(line) < 2:
            line = u''

        return line

    def removeReSection(self, line):
        # 先去掉成对的括号
        pattern = re.compile(self.re_replace_bracket)
        res = pattern.findall(line)
        if res:
            for one_res in res:
                line = line.replace(one_res, '')

        # 有的时候存在半括号情况
        pattern = re.compile(self.re_replace_bracket_semi)
        res = pattern.findall(line)
        if res:
            for one_res in res:
                line = line.replace(one_res, '')

        # 对于存在 表 3， 图3 之类的也不要
        pattern = re.compile(self.re_nouse_tag_graphtable)
        res = pattern.findall(line)
        if res:
            line = u''

        if len(line) > 0:
            for re_pat in self.re_nouse_tag_seq:
                pattern = re.compile(re_pat)
                res = pattern.findall(line)
                if res and len(res[0]) == len(line):
                    line = u''

        # 对于存在百分比的行，不要
        if len(line) > 0:
            pattern = re.compile(self.re_nouse_tag_percent)
            res = pattern.findall(line)
            if res:
                line = u''

        return line

    def removeMiddleSection(self, line):
        # 如果包含任何一个词的，该行就不要了
        for midword in self.middlewords:
            if line.__contains__(midword) :
                line = u''
                break
        return line
    def removePrefixSection(self, line):
        if line.startswith(u'怎'):
            line = u''

        # # 如果开头是“什么是”，也需要去掉
        for prefixword in self.prefixwords:
            length = len(prefixword)
            if line.startswith(prefixword) :
                line = line[length:]


        return line

    def removeSuffixSection(self, line):
        # 如果结尾是“分为”，则该行不要
        if line.endswith(u'分为'):
            line = u''

        # 如果结尾是概要，或者简介，导论，就去掉该词
        for suffixword in self.suffixwords:
            length = len(suffixword)
            if line.endswith(suffixword) :
                line = line[:-length]
                if line.endswith(u'的'):
                    line = line[:-1]


        return line
    def parseDashSection(self, line):

        # 破折号情况
        if line.__contains__(u'——'):
            splitarr = line.split(u'——')
            second = splitarr[1]
            if len(second) == 0 or second.__contains__(u'包括') or \
                    second.__contains__(u'以下') or \
                    second.__contains__(u'主要有') or second.endswith(u'为例'):
                line = splitarr[0]

            # 如果破折号后面的是举例
        # 逗号情况，
        if line.__contains__(u'，'):
            splitarr = line.split(u'，')
            secend = splitarr[1]
            if len(secend) == 0 or secend.__contains__(u'包括') or secend.__contains__(u'以下') or secend.__contains__(u'主要有'):
                line = splitarr[0]

        # 如果句子有冒号的，则只取第一个冒号前面的内容
        if len(line) > 0:
            line = line.replace(u'：', u':')
            index = line.find(u':')
            if index > 0 and self.isInBrackets(index, line) == False:
                line = line.split(u':')[0]

        # 如果句子有等号的，则只取第一个等号前面的内容
        if len(line) > 0:
            line = line.replace(u'＝', u'=')
            line = line.split(u'=')[0]

        # 如果句子有句号的，则只取第一个句号前面的内容
        if len(line) > 0:
            #line = line.replace(u'＝', u'=')
            line = line.split(u'。')[0]

        return line

    def isInBrackets(self, index, line):
        flag = False

        # 首先判断是否为引号，或者中括号强调，如果有，则不用处理下面的内容
        if len(line) > 0:
            left_index = line.find(u'《')
            right_index = line.find(u'》')

            left_index1 = line.find(u'“')
            right_index1 = line.find(u'”')

            if (index > left_index and right_index > index) or (index > left_index1 and right_index1 > index):
                flag = True

        return flag

    def setSchoolAndCourse(self, tree, result):
        schoolname = u'奥鹏教育'
        coursename = self.course_filepath_list[0].course.coursebase_name
        coursecode = self.course_filepath_list[0].course.coursebase_code
        # level 默认是0
        #tree.rootnode.level = 0
        tree.initTree(schoolname,coursename,coursecode)

    def extractKnowledge(self):
        k_tree = self.generatetree()
        # 再使用ngram分析纯文本内容
        #k_list = self.generatelist()
        self.outputTree(k_tree)

    def generatelist(self):
        # 直接调研ngram方法
        fileNames = os.path.splitext(self.wordreader.output_filepath)

        self.ngram.maxComputefreq = 10
        self.ngram.maxOutputfreq = 15
        self.ngram.inputfile = self.wordreader.output_filepath
        self.ngram.outputfile = fileNames[0] +  '-ngram' + fileNames[1]
        self.ngram.extractHotwords()

        k_list = []
        f = open(self.ngram.outputfile)
        for k in f:
            k_list.append(k)

        return k_list


if __name__ == "__main__":

    pusher = TreeFactory()
    sen = u'“诗史”'
    sen = pusher.postProcessSentence(sen)
    sen = u'协议出让33.4%表 2．招标出让22%图3．折扣（discount为'
    pattern = re.compile(pusher.re_nouse_tag_percent)
    res = pattern.findall(sen)

    pusher.outputfile = u'./../data/course-knowledge-tgt/抽取模板.txt'
    pusher.inputfile = u'D:/奥鹏/学生服务中心标注/文科课程电子辅导资料-docx/抽取模板.docx'
    course_filepath = CourseInfomation.CourseFilepath()
    course_filepath.sourse_filetype = course_filepath.type_text
    course_filepath.courseware_source_txt_filepath = u'./../../data/other/中级财务会计.txt'
    course_filepath.courseware_knowledge_txt_filepath = u'./../../data/other/中级财务会计-kwg.txt'
    course = CourseInfomation.Course()
    course.CourseCode = '1000'
    course_filepath.course = course
    pusher.course_filepath = course_filepath


    pusher.extractKnowledge()
    print 'over.'
