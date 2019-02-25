# -*- coding:utf-8 -*-

import os
import sys
import gensim
from gensim.models import Doc2Vec
from tool.reader import SentenceReader
from domain import FilePath

reload(sys)
sys.setdefaultencoding("utf-8")

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

class TextVector:
    """
    文本向量，计算2个文本句子之间的相似度
    """

    def __init__(self):
        """
        initialize local variables.
        """
        # 定义分词器
        self.sentence_reader = SentenceReader.SentenceReader()
        # 分类目录数据
        self.catalog_code_dict = {}

        self.stopwords = [u'学', u'类', u'中国', u'国际', u'国外', u'西方']
        # 获取第二层的分类
        self.snd_level_catalog = []

        self.model = None

        self.index_catalog = {}

    def generate_train_file(self):
        self.sentence_words_dict = {}
        # 加载训练文本，训练文本有2部分组成，一部分是课件，一部分是试题

        # 检查语料文件是否已经生成, 如果已经生成，则不用再生成
        #if  FilePath.fileExist(self.course_path_info.vector_corpus_txt_filepath):
        #    return
        catalog_corpus_file = u'D:/pythonproject/open-neo4j-service/data/course-base/本科专业目录-catalog.corpus.txt'
        catalog_xls_file = u'D:/pythonproject/open-neo4j-service/data/course-base/本科专业目录-catalog.xlsx.txt'
        # 打开结果文件
        f_out = open(catalog_corpus_file, 'w')

        # 第一步先加载分类目录

        if FilePath.fileExist(catalog_xls_file):
            fin = open(catalog_xls_file, 'r')  # 以读的方式打开文件
            # 以第二层为判断点
            # 合并第二层以下的点为一行
            level_snd_list = []
            write_line = ''
            first_code = ''
            first_name = ''
            index = 0
            for line in fin:
                arr = line.split()
                code_line = arr[0]
                name_line = arr[1]
                code_section_list = code_line.split('.')
                if index == 0:
                    first_code = code_line
                    first_name = name_line

                if len(code_section_list) == 1 :
                    name_line1 = self.preprocessSent(name_line)
                    #c_line_words = self.sentence_reader.splitSentenceCanRepeat(name_line1)
                    c_line_words = self.sentence_reader.splitOneSentence(name_line1)
                    c_line_words = self.postWordList(c_line_words)
                    #section_name = ' '.join(c_line_words)
                    f_out.write(' '.join(c_line_words))
                    f_out.write('\n')
                    self.catalog_code_dict[name_line] = (code_line, name_line, c_line_words)
                elif len(code_section_list) == 2 :

                    if len(level_snd_list) > 0:
                        write_line = ' '.join(level_snd_list)
                        write_line1 = self.preprocessSent(write_line)
                        #c_line_words = self.sentence_reader.splitSentenceCanRepeat(write_line1)
                        c_line_words = self.sentence_reader.splitOneSentence(write_line1)
                        c_line_words = self.postWordList(c_line_words)
                        section_name = ' '.join(c_line_words)
                        f_out.write(section_name)
                        f_out.write('\n')
                        self.catalog_code_dict[first_name] = (first_code, first_name, c_line_words)
                        # 第二层的数据
                        self.snd_level_catalog.append((first_code, first_name, section_name, c_line_words))
                    # 重置列表为空列表
                    level_snd_list = []
                    level_snd_list.append(name_line)
                    first_code = code_line
                    first_name = name_line
                else:
                    level_snd_list.append(name_line)

                index += 1
            # 最后一项
            write_line = ' '.join(level_snd_list)
            write_line1 = self.preprocessSent(write_line)
            #c_line_words = self.sentence_reader.splitSentenceCanRepeat(write_line1)
            c_line_words = self.sentence_reader.splitOneSentence(write_line1)
            c_line_words = self.postWordList(c_line_words)
            section_name = ' '.join(c_line_words)
            f_out.write(section_name)
            f_out.write('\n')
            self.catalog_code_dict[first_name] = (first_code, first_name, c_line_words)

            # 第二层的数据
            self.snd_level_catalog.append((first_code, first_name, section_name, c_line_words))

        f_out.close()

    def postWordList(self, word_list):

        result_list = []
        for word in word_list:
            if word == u'学':
                continue
            if word.startswith(u'概'):
                continue

            result_list.append(word)

        return result_list

    def preprocessSent(self, sent):
        """
        预处理，比如处理最后是学字
        :param sent: 
        :return: 
        """
        if isinstance(sent, str):
            sent = sent.decode('utf-8')

        if len(sent) < 3:
            return sent
        # 去掉，学，类，中国，国外，国际等对分类，干扰的词汇
        for stopword in self.stopwords:
            if sent.__contains__(stopword):
                sent = sent.replace(stopword, u' ')

        return sent


    def train(self):
        # 加载数据
        documents = []
        # 使用count当做每个句子的“标签”，标签和每个句子是一一对应的
        count = 0
        for words_tuple in self.snd_level_catalog:

            words = words_tuple[3]
            self.index_catalog[count] = words_tuple[1]
            # 这里documents里的每个元素是二元组，具体可以查看函数文档
            documents.append(gensim.models.doc2vec.TaggedDocument(words, [str(count)]))
            count += 1
            if count % 10000 == 0:
                print '{} has loaded...'.format(count)

        # 模型训练
        self.model = Doc2Vec(dm=1, size=200, window=8, min_count=1, workers=4, epochs=2000)
        self.model.build_vocab(documents)
        self.model.train(documents, total_examples=self.model.corpus_count, epochs=self.model.epochs)
        # 保存模型
        model_file = u'D:/pythonproject/open-neo4j-service/data/course-base/本科专业目录-catalog.d2v.model'
        self.model.save(model_file)

    def test_doc2vec(self):
        # 加载模型
        #model = Doc2Vec.load('models/ko_d2v.model')
        model = self.model
        # 与标签‘0’最相似的
        print(model.docvecs.most_similar('0'))
        # 进行相关性比较
        print(model.docvecs.similarity('0', '1'))
        # 输出标签为‘10’句子的向量
        print(model.docvecs['10'])
        # 也可以推断一个句向量(未出现在语料中)
        #words = u"여기 나오는 팀 다 가슴"
        course_name = u'比较教育学'
        words = self.sentence_reader.splitOneSentence(course_name)
        vector = model.infer_vector(words)
        sims = model.docvecs.most_similar([vector], topn=len(model.docvecs))

        for sim in sims:
            name = self.index_catalog.get(int(sim[0]))
            print '{}, {}'.format(name, sim[1])

        # 也可以输出词向量
        #print(model[u'가슴'])



if __name__ == "__main__":
    tv = TextVector()
    tv.generate_train_file()
    tv.train()
    tv.test_doc2vec()
