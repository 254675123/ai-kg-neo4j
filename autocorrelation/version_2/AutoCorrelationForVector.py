# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-08-23
program       : *_*  auto correlate the subject and the knowledge *_*

"""
import os


import AssociateQKV4ForVector
from domain import CourseInfomation
from extract.docxextract import TreeFactory
from domain import QuestionInformation
from tool.processor import CourseProcessor, SentenceProcessor
from domain import FilePath
from tool.reader import ExcelWriter
import exam_question_processor
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class AutoCorrelation:
    """
    word net generator.
    """
    def __init__(self, corese_scop_excel_file):
        """
        initialize local variables.
        
        该类用于整合所有类在一起，来协同完成试题与知识点的自动关联工作；
        1. 从给定的pdf文件（课程课件），需要转换成txt格式，该文件用于抽取知识点；
        2. 从给定的excel文件（题库导出试题），需要转换成txt格式，该文件用于概念语义网的训练；
        3. 在以上两步骤都完成的情况下，执行自动关联步骤，完成整个工作。
        """
        self.isTest = False
        # 当前文件的文件路径
        self.__curpath = os.path.dirname(os.path.realpath(__file__))
        # 获取文件名称作为课程名称（课程的文件名称即为课程名称）
        self.coursename = None
        # 用于产生知识点的源文件路径，该文件为pdf文件格式（非扫描），或者txt文件格式
        self.courseware_source_docx_filepath = None
        self.courseware_knowledge_txt_filepath = None
        self.courseware_source_txt_filepath = None
        # 用于产生试题的源文件路径，该文件为excel文件格式，或者txt文件格式
        self.questionsourcefilepath = None
        self.questiontargetfilepath = None
        self.questionresultfilepath = None

        # 用于抽取docx文档中的知识树
        self.treefactory = TreeFactory.TreeFactory()

        # 最终的统计结果，
        self.course_score_list = []
        # 已经处理完成的课程,key为schoolcode-coursecode
        self.course_processed_dict = {}
        # 匹配效果不好的课程-试题
        self.course_bad_examquestion = {}
        # 未识别的课程
        self.course_unrecongnized = []
        # 未在范围内的课程
        self.course_over_scope = []

        # 定义句子处理器
        self.sentence_processor = SentenceProcessor.SenPreprocess()
        # 定义试题处理器
        self.exam_processor = exam_question_processor.ExamQuestionProcessor()

        # course 处理器
        self.course_processor = CourseProcessor.CourseProcessor()
        self.exam_processor.setCourseInfo(self.course_processor.course_info)

        # 先初始化课程的范围
        self.__initCourseScope(corese_scop_excel_file)
        self.__initSchoolScope()


    def __initCourseScope(self, corese_scop_excel_file):
        """
        用来初始化处理课程的范围，该课程范围由excel指定
        :return: 
        """
        # 指定课程范围的文件
        filepath = '{}/../../data/course-base/{}'.format(self.__curpath, corese_scop_excel_file)
        self.school_course_scope_dict = self.course_processor.getNeedCourseDict(filepath)

        print '初始化课程列表结束'
    def __initSchoolScope(self):
        """
        设定学校范围
        :return: 
        """
        self.school_dict = {}
        self.school_dict[u'北航'] = u'北京航空航天大学'
        self.school_dict[u'北交'] = u'北京交通大学'
        self.school_dict[u'福师'] = u'福建师范大学'
        self.school_dict[u'华师'] = u'华中师范大学'
        self.school_dict[u'吉大'] = u'吉林大学'
        self.school_dict[u'地大'] = u'中国地质大学(北京)'

    def getSchoolNameFromFileName(self, filename):
        """
        从文件名称中，获取到课程名称，文件名称为：福师《外国法制史》.docx
        从文件名称抽取出院校名称，这里抽取的名称：福师
        :param filename: 
        :return: 
        """
        if len(filename) < 2:
            return ''
        schoolname = filename[0:2]
        if self.school_dict.__contains__(schoolname):
            schoolname = self.school_dict.get(schoolname)

        return schoolname

    def getCourseNameFromFileName(self, filename):
        """
        从文件名称中，获取到课程名称，文件名称为：福师《外国法制史》.docx
        从文件名称抽取出课程名称，这里抽取出中括号内的名称：外国法制史
        :param filename: 
        :return: 
        """
        course_list = self.sentence_processor.find_VIP_words_by_pattern(filename)
        course_name = ''
        if len(course_list) > 0:
            course_name = course_list[0]
            course_name = str(course_name).replace(u'（',u'(')
            course_name = str(course_name).replace(u'）', u')')
        return course_name

    def fileFormatValidating(self):
        """
        检查knowledgefilepath 和questionfilepath的文件格式
        :return: False , True
        """
        if self.courseware_source_docx_filepath is None or self.questionsourcefilepath is None:
            # 这种情况下，属于路径未赋值，返回false
            print '未知文件路径，请设置知识和问题的源文件路径。'
            return False

        if not self.courseware_source_docx_filepath.endswith('.docx'):
            # 这种情况下，属于非法格式，返回false
            print 'Knowledge 文件格式错误，只允许是docx。'
            return False

        if not self.questionsourcefilepath.endswith('.xlsx') and not self.questionsourcefilepath.endswith('.txt'):
            # 这种情况下，属于非法格式，返回false
            print 'Question 文件格式错误，只允许是xlsx和txt。'
            return False

        return True



    def questionSourceFileProcess(self, course_path_info):
        """
        处理试题的源文件
        :return: 
        """
        self.exam_processor.courseExamQuestionGenerator(course_path_info)


    def questionAndKnowledge(self, course_path_info):
        """
        对试题与知识点进行自动关联，并将关联结果生成文件
        :return: 
        """
        aq = AssociateQKV4ForVector.AssociateQKByKeyword(course_path_info)
        aq.preprocessor = self.treefactory.preprocesser
        aq.examquestion_info = self.exam_processor.exam_info
        aq.executeAssociate()
        # 保存关联差/坏的结果，让人工来修正
        self.course_bad_examquestion[course_path_info.course] = aq.bad_examquestion_list
        self.saveBadExamquestion(course_path_info, aq.bad_examquestion_list)

        # 保存好的结果，让人工审核
        self.exam_processor.createGoodResult2Excel4PersonCheck(course_path_info)

        # 保留统计结果
        cypherlist = self.exam_processor.createCypherFile(course_path_info.course)
        self.saveCourseCypher(course_path_info.cypher_txt_filepath, cypherlist)


        # 同时将统计结果保存为文件
        self.saveProcessedCourse(course_path_info.courseware_source_directory,aq.course_score)
    def saveBadExamquestion(self, course_path_info, bad_examquestion_list):
        if len(bad_examquestion_list) == 0:
            return

        column_data_list = []
        column_data_list.append(QuestionInformation.column_head_list)
        for exam_question_tup in bad_examquestion_list:
            exam_row_list = exam_question_tup[0].toList()
            exam_row_list[0] = course_path_info.course.SchoolName
            exam_row_list[1] = course_path_info.course.NewCourseName
            # 电脑打标
            k_list = []
            for restful in exam_question_tup[1]:
                k_list.append(restful.toDescription())
            exam_row_list.append(u';'.join(k_list))
            column_data_list.append(exam_row_list)
        sheet_datas = {}
        sheet_datas['sheet1'] = column_data_list
        ExcelWriter.writeExcelFile(course_path_info.correlation_bad_xls_filepath, sheet_datas)
        print '文件：{}已生成'.format(course_path_info.course.NewCourseName)

        pass

    def saveCourseCypher(self,filepath, cypherlist):
        if cypherlist is None or filepath is None:
            return

        fout = open(filepath, 'w')
        fout.write('\n'.join(cypherlist))
        fout.close()


    def saveProcessedCourse(self,rootpath, course_score):
        if course_score is None:
            return
        self.course_score_list.append(course_score)
        output_mid_filepath = '{}/statistics-mid.txt'.format(rootpath)
        fout = open(output_mid_filepath, 'a')
        fout.write(course_score.toString())
        fout.write('\n')
        fout.close()
        course_key = '{}-{}'.format(course_score.school_code, course_score.course_code)
        self.course_processed_dict[course_key] = course_score


    def loadProcessedCourse(self, rootpath):
        output_mid_filepath = '{}/statistics-mid.txt'.format(rootpath)
        if not FilePath.fileExist(output_mid_filepath):
            return
        fout = open(output_mid_filepath, 'r')
        lines = fout.readlines()
        for one_course_str in lines:
            course_score = CourseInfomation.CourseScore()
            course_score.initByString(one_course_str)
            key = '{}-{}'.format(course_score.school_code, course_score.course_code)
            self.course_processed_dict[key] = course_score
            self.course_score_list.append(course_score)
        fout.close()



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
        self.questiontargetfilepath = u'./../data/course-question-tgt/{}.txt'.format(coursename)
        self.questionresultfilepath = u'./../data/knowledge-question-result/{}.txt'.format(coursename)
        tt = os.path.abspath(self.questionsourcefilepath)
        return  tt

    def associateFlow(self, course_path_info):
        """
        关联流程，按步骤执行即可
        :return: 
        """
        # 第一步：检测源文件是否有效
        #if False == self.fileFormatValidating():
        #    return
        # 第二步：处理课程源文件，生成知识点
        #self.knowledgeSourceFileProcess()
        #self.extractKnowledgeFromSourceFile()
        # 从word文档中抽取
        #
        print '正在转换docx到txt，并抽取知识树...'
        self.treefactory.course_filepath = course_path_info
        self.treefactory.extractKnowledge()
        #self.knowledgemidfilepath = self.treefactory.wordreader.outputmidfilepath
        print '知识树抽取完成。'

        # 第三步：处理试题源文件，生成训练和测试样本
        print '开始获取试题数据...'
        self.questionSourceFileProcess(course_path_info)
        #print '开始生成试题词网...'
        #self.questionGenerateWordnet()
        #print '试题数据获取、试题词网生成完成。'
        print '试题数据获取完成。'


        # 第四步：将知识点和试题进行关联
        print '开始关联试题与知识点...'
        self.questionAndKnowledge(course_path_info)
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

    def batchProcessAssociate1(self, dirname):
        """
        批量处理多个课程的自动关联工作
        :return: 
        """

        # 指定一个文件夹，该文件夹用来存放多个课程的pdf课件
        # 逐个课件处理
        # 首先指定根目录位置,从该目录读取pdf课件
        srcrootpath = './../../data/course-knowledge-machine/'+ dirname
        c_rootpath = srcrootpath + '/c-docx'
        #q_rootpath = srcrootpath + '/q-xlsx'
        self.loadProcessedCourse(srcrootpath)
        # os.walk(path)这个函数得到的结果是一个或多个tuple，
        # 或者使用os.listdir(path)函数能得到文件夹下所有文件（包括文件夹）的名称，但是无法获取子文件夹的状态
        count = 0
        filelist = self.get_filename_from_dir(c_rootpath)
        # 然后是对每一个文件进行处理
        for f in filelist:
            count = count + 1
            self.coursename = os.path.splitext(f)[0]
            # 判断该课程是否在需要处理的范围之内，如果不是，则跳过该课程
            current_coursename = self.getCourseNameFromFileName(self.coursename)
            current_schoolname = self.getSchoolNameFromFileName(self.coursename)
            if not self.school_course_scope_dict.__contains__(current_schoolname+current_coursename):
                self.course_over_scope.append(f)
                continue

            # 如果课程名称中包含英语，不处理
            if current_coursename.__contains__(u'英语'):
                continue

            # 如果该课程在需要处理的范围内，则开始处理
            print '开始处理文件：{}'.format(f)
            course = self.school_course_scope_dict.get(current_schoolname+current_coursename)
            if len(course.SchoolName) == 0:
                self.course_unrecongnized.append(f)
                continue
            # 如果课程已经被处理了，跳过
            course_key = '{}-{}'.format(course.SchoolCode, course.CourseCode)
            if self.course_processed_dict.__contains__(course_key):
                print '第{0}篇 课程：{1} 已处理过；'.format(count, f)
                continue
            course_path_info = CourseInfomation.CourseFilepath()
            # 指定课件的源文件路径
            course_path_info.courseware_source_directory = srcrootpath
            course_path_info.courseware_source_docx_filepath = c_rootpath + '/' + f
            #course_path_info.examquestion_source_xlsx_filepath = q_rootpath + '/' + current_coursename + '.xlsx'
            course_path_info.initByCourse(course)

            # 如果已经关联过了，不用再次关联

            self.associateFlow(course_path_info)

            print '第{0}篇 课程：{1} 处理完成；'.format(count, f)

            # 测试时，先跑4个文件即可
            if self.isTest:
                if count > 4:
                    break

        print '所有课程处理完毕，共处理：{0}篇'.format(count)

        # 开始统计结果
        print '开始统计结果。'
        statistics_filepath = '{}/statistics.txt'.format(srcrootpath)
        self.statistics(statistics_filepath)
        print '统计结果结束。'

        # 关联差的数据保存
        combine_bad_filepath = '{}/combine_bad.xls'.format(srcrootpath)
        self.combineBadExamquestion(combine_bad_filepath)

    def combineBadExamquestion(self, combine_bad_filepath):
        column_data_list = []
        column_data_list.append(QuestionInformation.column_head_list)
        for course in self.course_bad_examquestion.keys():
            bad_examquestion_list = self.course_bad_examquestion.get(course)
            for exam_question_tup in bad_examquestion_list:
                exam_row_list = exam_question_tup[0].toList()
                exam_row_list[0] = course.SchoolName
                exam_row_list[1] = course.NewCourseName
                # 电脑打标
                #k_list = []
                #for restful in exam_question_tup[1]:
                #    k_list.append(restful.toDescription())
                #exam_row_list.append(u';'.join(k_list))
                column_data_list.append(exam_row_list)
        sheet_datas = {}
        sheet_datas['sheet1'] = column_data_list
        ExcelWriter.writeExcelFile(combine_bad_filepath, sheet_datas)
        print '文件：合并文件已生成'


    def statistics(self, statistics_filepath):
        """
        对course_score_list中的结果，进行统计
        :return: 
        """
        # bad course list
        bad_course_list = []
        # 课程的数量分布统计变量
        n_coure_count_more50 = 0
        n_coure_score_less50 = 0

        f_stat = open(statistics_filepath, 'w')
        # 统计所有课程，百分比的分布情况
        n_coure_score = CourseInfomation.CourseScore()
        for course_score in self.course_score_list:
            n_coure_score.score_scope_more60_count += course_score.score_scope_more60_count
            n_coure_score.score_scope_between5060_count += course_score.score_scope_between5060_count
            n_coure_score.score_scope_between4050_count += course_score.score_scope_between4050_count
            n_coure_score.score_scope_less40_count += course_score.score_scope_less40_count

            course_descrip = course_score.getDescription()
            f_stat.write('\n'.join(course_descrip))
            f_stat.write('\n\n')

            # 如果50分以上的超过50%，则more50+1
            if (course_score.score_scope_between5060_rate+course_score.score_scope_more60_rate) > 0.5:
                n_coure_count_more50 += 1
            else:
                n_coure_score_less50 += 1
                bad_course_list.append(course_score)

        f_stat.write('所有课程的汇总统计：')
        course_descrip = n_coure_score.getDescription()
        f_stat.write('\n'.join(course_descrip))
        f_stat.write('\n\n')

        # 统计课程所在区域的分布情况
        n_coure_count_total = n_coure_score_less50 + n_coure_count_more50
        n_coure_score_less_rate = float(n_coure_score_less50) / n_coure_count_total
        n_coure_count_more_rate = float(n_coure_count_more50) / n_coure_count_total
        ns = '50%以上的试题得分大于50分的课程数量：{}  占比：{}'.format(n_coure_count_more50, n_coure_count_more_rate)
        print ns
        ns = '50%以上的试题得分小于50分的课程数量：{}  占比：{}'.format(n_coure_score_less50, n_coure_score_less_rate)
        print ns

        # 保存bad course信息
        print 'bad course information.'
        for bad_course in bad_course_list:

            course_descrip = bad_course.getDescription()
            f_stat.write('\n'.join(course_descrip))
            f_stat.write('\n')

        # 保存未识别的课程
        f_stat.write('\n\n')
        f_stat.write('未识别的课程：')
        f_stat.write('\n'.join(self.course_unrecongnized))
        f_stat.write('\n\n')
        f_stat.write('超出范围的课程：')
        f_stat.write('\n'.join(self.course_over_scope))
        f_stat.close()

    def getCourseName(self, filename):
        """
        从文件名称中，获取课程名称
        :return: 
        """



if __name__ == "__main__":
    # 该文件放在course-base下面
    corese_scop_excel_file = 'course-scope-200plus-20181122.xlsx'
    # 该文件夹放在course-knowledge-machine下面
    dirname = '20181122-200plus'
    sr = AutoCorrelation(corese_scop_excel_file)
    #sr.isTest = True

    sr.batchProcessAssociate1(dirname)