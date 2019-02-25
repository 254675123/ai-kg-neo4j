# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-08-23
program       : *_*  auto correlate the subject and the knowledge *_*

"""
import os
import sys

import AssociateQKV4ForDocx
from extract.docxextract import TreeFactory
from extract.newordextract import NGram
from tool import ExcelToTxt
from tool.reader import PdfReader

reload(sys)
sys.setdefaultencoding('utf-8')

class AutoCorrelation:
    """
    word net generator.
    """
    def __init__(self):
        """
        initialize local variables.
        该类用于整合所有类在一起，来协同完成试题与知识点的自动关联工作；
        1. 从给定的pdf文件（课程课件），需要转换成txt格式，该文件用于抽取知识点；
        2. 从给定的excel文件（题库导出试题），需要转换成txt格式，该文件用于概念语义网的训练；
        3. 在以上两步骤都完成的情况下，执行自动关联步骤，完成整个工作。
        """
        # 获取文件名称作为课程名称（课程的文件名称即为课程名称）
        self.coursename = None
        # 用于产生知识点的源文件路径，该文件为pdf文件格式（非扫描），或者txt文件格式
        self.knowledgesourcefilepath = None
        self.knowledgetargetfilepath = None
        self.knowledgemidfilepath = None
        # 用于产生试题的源文件路径，该文件为excel文件格式，或者txt文件格式
        self.questionsourcefilepath = None
        self.questiontargetfilepath = None
        self.questionresultfilepath = None

        # 用于抽取docx文档中的知识树
        self.treefactory = TreeFactory.TreeFactory()

    def fileFormatValidating(self):
        """
        检查knowledgefilepath 和questionfilepath的文件格式
        :return: False , True
        """
        if self.knowledgesourcefilepath is None or self.questionsourcefilepath is None:
            # 这种情况下，属于路径未赋值，返回false
            print '未知文件路径，请设置知识和问题的源文件路径。'
            return False

        if not self.knowledgesourcefilepath.endswith('.docx'):
            # 这种情况下，属于非法格式，返回false
            print 'Knowledge 文件格式错误，只允许是docx。'
            return False

        if not self.questionsourcefilepath.endswith('.xlsx') and not self.questionsourcefilepath.endswith('.txt'):
            # 这种情况下，属于非法格式，返回false
            print 'Question 文件格式错误，只允许是xlsx和txt。'
            return False

        return True

    def knowledgeSourceFileProcess(self):
        """
        处理知识点的源文件
        :return: 
        """
        # pdf 格式，需要进行转换
        if self.knowledgesourcefilepath.endswith('.pdf'):
            pdf = PdfReader.PdfReader()
            pdf.changePdfToText(self.knowledgesourcefilepath)
            self.knowledgesourcefilepath = pdf.resfilepath

        # 生成knowledge的目标文件名称
        fileNames = os.path.splitext(self.knowledgetargetfilepath)
        self.knowledgetargetfilepath = fileNames[0] + '-knowledge.txt'

        # 生成question的结果文件名称
        self.questionresultfilepath = fileNames[0] + '-result.txt'

    def extractKnowledgeFromSourceFile(self):
        """
        from source file中提取知识点
        :return: 
        """
        ngram = NGram.NGram()
        ngram.inputfile = self.knowledgesourcefilepath
        ngram.outputfile = self.knowledgetargetfilepath
        ngram.extractHotwords()


    def questionSourceFileProcess(self):
        """
        处理试题的源文件
        :return: 
        """
        # excel 格式，需要进行转换
        if self.questionsourcefilepath.endswith('.xlsx'):
            excel = ExcelToTxt.ExcelReader()

            excel.readFile(self.questionsourcefilepath, self.questiontargetfilepath)
            self.questionsourcefilepath = excel.trainfilepath
            self.questiontargetfilepath = excel.testfilepath

    def questionGenerateWordnet(self):
        """
        在源问题文件的基础上产生概念语义网
        :return: 
        """
        wg = tool.graphnet.semanticnet.WordnetGenerator.WordnetGenerator()
        wg.coursename = self.coursename
        wg.sourcefilepath = self.questionsourcefilepath
        wg.generateNode()

    def questionAndKnowledge(self):
        """
        对试题与知识点进行自动关联，并将关联结果生成文件
        :return: 
        """
        aq = AssociateQKV4ForDocx.AssociateQKByKeyword()
        aq.knowledgefilepath = self.knowledgetargetfilepath
        aq.questionfilepath = self.questiontargetfilepath
        aq.outputfilepath = self.questionresultfilepath
        aq.executeAssociate()

    def getQuestionSourceData(self, coursename):
        """
        从题库中提取指定课程的试题
        :param coursename: 课程名称
        :return: 
        """
        # 按照课程名称，获取试题
        #pass

        # 这里默认导出了数据文件
        self.questionsourcefilepath = u'./../data/course-question-src/{}.xlsx'.format(coursename)
        self.questiontargetfilepath = u'./../data/course-question-tgt/{}.xlsx'.format(coursename)
        self.questionresultfilepath = u'./../data/knowledge-question-result/{}.txt'.format(coursename)
        tt = os.path.abspath(self.questionsourcefilepath)
        return  tt

    def associateFlow(self):
        """
        关联流程，按步骤执行即可
        :return: 
        """
        # 第一步：检测源文件是否有效
        if False == self.fileFormatValidating():
            return
        # 第二步：处理课程源文件，生成知识点
        #self.knowledgeSourceFileProcess()
        #self.extractKnowledgeFromSourceFile()
        # 从word文档中抽取
        #
        print '正在抽取知识树...'
        self.treefactory.inputfile = self.knowledgesourcefilepath
        self.treefactory.outputfile = self.knowledgetargetfilepath
        self.treefactory.outputmidfilepath = self.knowledgemidfilepath
        self.treefactory.extractKnowledge()
        print '知识树抽取完成。'

        # 第三步：处理试题源文件，生成训练和测试样本
        print '开始获取试题数据...'
        self.questionSourceFileProcess()
        print '开始生成试题词网...'
        self.questionGenerateWordnet()
        print '试题数据获取、试题词网生成完成。'

        # 第四步：将知识点和试题进行关联
        print '开始关联试题与知识点...'
        self.questionAndKnowledge()
        print '完成试题与知识点的关联。'

    def get_filename_from_dir(self, dir_path):
        file_list = []
        if not os.path.exists(dir_path):
            return file_list

        for item in os.listdir(dir_path):
            basename = os.path.basename(item)
            # print(chardet.detect(basename))   # 找出文件名编码,文件名包含有中文

            # windows下文件编码为GB2312，linux下为utf-8
            try:
                decode_str = basename.decode("GB2312")
            except UnicodeDecodeError:
                decode_str = basename.decode("utf-8")

            file_list.append(decode_str)

        return file_list

    def batchProcessAssociate1(self):
        """
        批量处理多个课程的自动关联工作
        :return: 
        """

        # 指定一个文件夹，该文件夹用来存放多个课程的pdf课件
        # 逐个课件处理
        # 首先指定根目录位置,从该目录读取pdf课件
        srcrootpath = './../data/course-knowledge-scr-docx'
        tgtrootpath = './../data/course-knowledge-tgt-docx'
        midrootpath = './../data/course-knowledge-mid-docx'
        # os.walk(path)这个函数得到的结果是一个或多个tuple，
        # 或者使用os.listdir(path)函数能得到文件夹下所有文件（包括文件夹）的名称，但是无法获取子文件夹的状态
        count = 0
        filelist = self.get_filename_from_dir(srcrootpath)
        # 然后是对每一个文件进行处理
        for f in filelist:
            count = count + 1
            self.coursename = os.path.splitext(f)[0]
            print '开始处理文件：{}'.format(f)
            self.knowledgesourcefilepath = srcrootpath + '/' + f
            self.knowledgetargetfilepath = tgtrootpath + '/' + self.coursename + '.txt'
            self.knowledgemidfilepath = midrootpath + '/' + self.coursename + '-mid.txt'

            self.questionsourcefilepath = self.getQuestionSourceData(self.coursename)
            self.associateFlow()

            print '第{0}篇 课程：{1} 处理完成；'.format(count, f)

        print '所有课程处理完毕，共处理：{0}篇'.format(count)


    def batchProcessAssociate2(self):
        """
        批量处理多个课程的自动关联工作
        :return: 
        """

        # 指定一个文件夹，该文件夹用来存放多个课程的pdf课件
        # 逐个课件处理
        # 首先指定根目录位置,从该目录读取pdf课件
        rootpath = './../data/course-knowledge'
        # os.walk(path)这个函数得到的结果是一个或多个tuple，
        # 个数取决于路径下是否有文件夹：如果没有文件夹的话，那么只有一个tuple，如果有的话，
        # 假如有3个，那么就会有4个tuple。
        # 而每个tuple中有三项：
        # 1.当前文件夹的路径(str类型）
        # 2.当前文件夹中的所有文件夹名称（list类型）
        # 3.当前文件夹中所有文件的名称
        # 所以，当只需要遍历当前文件夹下的文件时，只需要取出i[2]即可。

        # 这里的for是为了处理文件夹的嵌套，如果只有根目录是文件夹，那么for就执行一次。
        count = 0
        for item in os.walk(rootpath):
            filelist = item[2]

            # 然后是对每一个文件进行处理
            for f in filelist:
                f1 = f.decode('gbk', 'ignore')
                print f
                print f1

                count = count + 1
                self.knowledgesourcefilepath = rootpath + '/' + f
                self.questionsourcefilepath = self.getQuestionSourceData(f)
                self.associateFlow()

                print '第{0}篇 课程：{1} 处理完成；'.format(count, f)

        print '所有课程处理完毕，共处理：{0}篇'.format(count)

if __name__ == "__main__":
    sr = AutoCorrelation()
    sr.batchProcessAssociate1()