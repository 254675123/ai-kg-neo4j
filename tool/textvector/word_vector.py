# -*- coding:utf-8 -*-

import os
import sys

from gensim.models import KeyedVectors
from gensim.models.word2vec import LineSentence, Word2Vec
from domain import FilePath
from tool.processor import SentenceProcessor
from tool.reader import SentenceReader

reload(sys)
sys.setdefaultencoding("utf-8")


class TextVector:
    """
    文本向量，计算2个文本句子之间的相似度
    """

    def __init__(self, course_path_info_list):
        """
        initialize local variables.
        """
        # 定义分词器
        self.sentence_reader = SentenceReader.SentenceReader()
        self.sentence_processor = SentenceProcessor.SenPreprocess()
        # 训练样本文件
        self.course_path_info_list = course_path_info_list

        # 知识点集
        self.knowledge = None

    def generate_train_file(self):

        # 加载训练文本，训练文本有2部分组成，一部分是课件，一部分是试题

        # 检查语料文件是否已经生成, 如果已经生成，则不用再生成
        #if  FilePath.fileExist(self.course_path_info.vector_corpus_txt_filepath):
        #    return
        # 打开结果文件
        f_out = open(self.course_path_info_list[0].vector_corpus_txt_filepath, 'w')
        for course_path_info in self.course_path_info_list:

            # 第一步先加载课件
            if course_path_info.courseware_source_txt_filepath:
                for c_line in self.sentence_reader.splitSentence(course_path_info.courseware_source_txt_filepath):
                    f_out.write(' '.join(c_line))
                    f_out.write('\n')


            # 第二步加载试题
            if course_path_info.examquestion_source_txt_filepath and FilePath.fileExist(course_path_info.examquestion_source_txt_filepath):
                question = open(course_path_info.examquestion_source_txt_filepath, 'r')
                ids_lines = question.readlines()
                for line in ids_lines:
                    # line = "物权的分类:从设立的角度对他物权再做分类，可把其分为（）。,用益物权和担保物权"
                    line = line.strip('\n')
                    index = line.find('::')
                    if index < 0:
                        continue
                    k = line[0:index]
                    q = line[index + 2:]
                    q_words = self.sentence_reader.splitOneSentence(q)
                    q_words = self.sentence_processor.enlargeVipWords(q_words, q)
                    f_out.write(' '.join(q_words))
                    f_out.write('\n')

        # 第三步抽取的知识点也作为训练样本
        if self.knowledge:
            for k_key in self.knowledge:
                k_tup = self.knowledge[k_key]
                f_out.write(' '.join(k_tup[0]))
                f_out.write('\n')

        f_out.close()

    def train(self):

        # 先检查模型是否存在，如果存在，直接加载
        if FilePath.fileExist(self.course_path_info_list[0].vector_model_bin_filepath):
            print "语义模型已经存在，开始加载。"
            #self.model_loaded = Word2Vec.load_word2vec_format(self.model_file, binary=True)
            self.model_loaded = KeyedVectors.load_word2vec_format(self.course_path_info_list[0].vector_model_bin_filepath, binary=True)
            # 输出词典
            #self.output_dict(self.model_loaded.wv.index2word)
            return

        # 生成语料
        self.generate_train_file()
        # 加载语料
        #sentences = word2vec.Text8Corpus(self.train_output_result_file)
        sentences = LineSentence(self.course_path_info_list[0].vector_corpus_txt_filepath)
        # 训练skip-gram模型，默认window=5
        # 第一个参数是训练语料，第二个参数是小于该数的单词会被剔除，默认值为5, 第三个参数是神经网络的隐藏层单元数，默认为100
        # 注意：min_count = 1,就是所有词，如果设置大的话，会过滤掉小于的词
        print '正在训练模型...'
        model = Word2Vec(sentences, size=200, min_count=1, iter=1000)
        #model.wv.save(self.model_file)
        model.wv.save_word2vec_format(self.course_path_info_list[0].vector_model_bin_filepath, binary=True)
        self.model_loaded = model
    def pred_similarity(self, question_words, knowledge_words):
        # 判断问题和知识点之间的向量相似度
        print 'question_words:'+' '.join(question_words)
        print 'knowledge_words:' + ' '.join(knowledge_words)
        score = self.model_loaded.wv.n_similarity(question_words, knowledge_words)
        return score

    def output_dict(self, word_dict):
        filepath = u'./../data/course-knowledge-model/temp.dict'
        fout = open(filepath, 'w')  # 以写得方式打开文件
        for word in word_dict:
            fout.writelines(word)  # 将分词好的结果写入到输出文件
            fout.writelines('\n')
        fout.close()

    def readRegularKnowledgeList(self, knowledgefilepath):
        self.knowledge = {}
        if knowledgefilepath == '':
            return
        #words = open('./../data/79037-002_knowledge.txt', 'r')
        # zhongjicaiwukuaiji-auto-knowledge
        f = open(knowledgefilepath, 'r')
        ids_lines = f.readlines()
        index = 0
        for line in ids_lines:
            index += 1
            if index == 1:
                continue
            line = line.strip('\n')
            line_k = line.split(' ')
            if len(line_k) < 2:
                continue

            line_k_code = line_k[0]
            line_k_word = line_k[1]
            #line_k_confidence = line_k[2]
            line_k_confidence = 100

            if self.knowledge.__contains__(line_k_word):
                continue
            words = self.sentence_reader.splitOneSentence(line_k_word)
            words = self.sentence_processor.enlargeVipWords(words, line_k_word)
            tup = (words,line_k_confidence,line_k_code)
            self.knowledge[line_k_word] = tup
            tup = (line_k_word, line_k_confidence, line_k_code)



if __name__ == "__main__":
    sr = TextVector()
    sr.coursename = u'福师《中国古代文学》'
    sr.train()

    filepath = u'./../data/course-knowledge-tgt-docx/{}.txt'.format(sr.coursename)
    sr.readRegularKnowledgeList(filepath)
    question = u' 《文心雕龙》一共有五十篇，包括总论五篇，文体论二十篇，创作论十九篇，批评论五篇，最后一篇《序志》是总结全书的自序。这部书是中国古代文学理论著作是最系统的一部。（  ) 答案：正确 '
    q_words = sr.sentence_reader.splitSentenceCanRepeat(question)
    q_words = sr.sentence_processor.enlargeVipWords(q_words, question)
    for k_key in sr.knowledge.keys():
        k_tup = sr.knowledge.get(k_key)
        k_words = k_tup[0]
        if len(k_words) == 0:
            continue
        score = sr.pred_similarity(q_words, k_words)
        print '知识点：{}  得分：{}'.format(k_key, score)



