# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-9-29
program       : *_* sentence preprocess  *_*

"""
import re
import sys

from tool.convertor import UnicodeConvertor

reload(sys)
sys.setdefaultencoding('utf-8')

class SenPreprocess:
    """
    read sentence one by one.
    """

    def __init__(self):
        """
        initialize local variables.
        """
        # 定义正则
        self.__init_re_date()
        self.__init_re_level()
        self.__init_re_vip_words()
        self.__init_re_currency()

        # 结尾是小括号
        self.re_racket_end = ur'([（(].+?[)）]$)'
        self.re_racket_mid = ur'([（(].+?[)）])'

        # 强调符号列表
        self.signlist = [u'：',u':',u'——',u'=',u'＝']

        # 页码数字, 末尾是数字的，与前面的有分隔
        self.re_noues_pagenum = ur'([\s　]+[0123456789]+$)'

        # 包含数字的
        self.re_nouse_number = ur'([0123456789.]+)'

        # 存储符号对的字典
        self.sign_dict = {}
        self.sign_pairs = [(u'“', u'”'),(u'‘', u'’'),(u'《', u'》')]

    def __init_re_vip_words(self):
        # 抽取重点词
        # [也简]称[为]xx， 这里的xx就是知识点
        self.re_def_1 = ur'(也称.+?[\s,.;，：；、。—])'
        self.re_def_2 = ur'(称[之]*为.+?[\s,.;，：；、。—])'
        self.re_def_3 = ur'([^无]所谓[^的\s,.;，：；、。]+?[\s,.;，：；、。—])'
        self.re_def_4 = ur'(《[^《》]+?》)'
        self.re_def_5 = ur'(“[^“”]+?”)'
        self.re_def_strip = u'也称之为所谓,.;，：；、。— '
        self.re_def_strip_vip = u'《》“” '
        self.re_define = []
        self.re_define.append(self.re_def_1)
        self.re_define.append(self.re_def_2)
        self.re_define.append(self.re_def_3)
        self.re_define.append(self.re_def_4)

    def __init_re_date(self):
        # 定义属于时间格式的，去掉不要
        # 第一种时间格式 2016-12-12 或者2016/12/12
        self.re_date_1 = ur'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        # 第二种时间格式 2016-12-12 14:34
        self.re_date_2 = ur'(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s\d{1,2}:\d{1,2})'
        # 第三种时间格式 2016年12月12日
        self.re_date_3 = ur'(\d{4}[\s]*年\d{1,2}[\s]*月\d{1,2}[\s]*日)'
        self.re_date_31 = ur'(\d{4}[\s]*年\d{1,2}[\s]*月)'
        self.re_date_32 = ur'(\d{4}[\s]*年)'
        # 第四种时间格式，只包含月和日
        self.re_date_4 = ur'(\d{1,2}[\s]*月\d{1,2}[\s]*日)'
        self.re_date_4_1 = ur'(\d{1,2}[\s]*日)'
        # 第五种时间格式，只包含年的区间
        self.re_date_5 = ur'(\d{1,4}[年]*[-~—至]\d{1,4}[年间]*)'
        self.re_date_6 = ur'(\d{1,4}[年][-~—]*至今)|(\d{1,4}[年]*[-~—]至今)'
        self.re_date_71 = ur'(\d{1,2}世纪\d{1}0年代)|(\d{1,2}世纪[初中末][期]*)'
        self.re_date_72 = ur'(\d{1,2}[-~—]*\d{1,2}世纪)'
        self.re_date_7 = ur'(公元[前]{0,1}\d{1,2}世纪[-~—至初中末]*)'
        self.re_date = [self.re_date_5, self.re_date_6,
                        self.re_date_3, self.re_date_31, self.re_date_4, self.re_date_1,
                        self.re_date_2]

        self.re_date_remove = [self.re_date_1,self.re_date_2,self.re_date_3,
                               self.re_date_31, self.re_date_32, self.re_date_4,
                               self.re_date_4_1]

    def __init_re_currency(self):
        # 货币的检查
        self.re_currency_1 = ur'(\d+[\s万]*元)'
        self.re_currency_2 = ur'(\d+[\s万]*股)'

        self.re_currency = []
        self.re_currency.append(self.re_currency_1)
        self.re_currency.append(self.re_currency_2)

    def __init_re_level(self):
        # 对于表达层次关系的标签，比如：第一章，第五节，一、（十二），1.2，（7）等等
        # 我们把 章作为第一级层，节为第二级层，大写中文数字为三级层，带小括号的中文数字为四级层
        # 阿拉伯数字为五级层，带小括号的阿拉伯数字为六级层。
        self.re_num_1 = ur'(第[\s]*[一二三四五六七八九零十百千万亿]+[\s]*章)'
        self.re_num_1_1 = ur'(第[\s]*[0123456789]+[\s]*章)'
        self.re_num_2 = ur'(第[\s]*[一二三四五六七八九零十百千万亿]+[\s]*节)'
        self.re_num_2_1 = ur'(第[\s]*[0123456789]+[\s]*节)'
        self.re_num_3 = ur'([一二三四五六七八九零十百千万亿]+[：、，．,.\s　]+)'
        self.re_num_4 = ur'([（(][\s]*[一二三四五六七八九零十百千万亿]+[\s]*[)）])'
        self.re_num_5 = ur'([0123456789]+?[：、，．,.\s　]+)'
        self.re_num_6 = ur'(([0123456789]+[\s]*.)+[0123456789][：、，．,\s　])'
        self.re_num_7 = ur'([（(]{0,1}[\s]*[0123456789]+[\s]*[)）])'
        self.re_num_7_1 = ur'(〈[\s]*[0123456789]+[\s]*〉)'
        self.re_num_8 = ur'([⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇])'
        self.re_num_9 = ur'([①②③④⑤⑥⑦⑧⑨⑩])'


        self.re_level = []
        self.re_level.append((self.re_num_1, 1))
        self.re_level.append((self.re_num_1_1, 1))
        self.re_level.append((self.re_num_2, 2))
        self.re_level.append((self.re_num_2_1, 2))
        self.re_level.append((self.re_num_3, 3))
        self.re_level.append((self.re_num_4, 4))
        self.re_level.append((self.re_num_6, 6))
        self.re_level.append((self.re_num_5, 5))
        self.re_level.append((self.re_num_7, 7))
        self.re_level.append((self.re_num_8, 8))
        self.re_level.append((self.re_num_9, 9))


    def preprocess_content_rows(self, content_rows):
        """
        对读取出来的docx信息，进行预处理
        :param content_rows: 
        :return: 
        """

        result = []
        if len(content_rows) < 3:
            return result

        #result.append(content_rows[0])
        #result.append(content_rows[1])
        for line in content_rows:
            # 如果包含问号，直接忽略
            if line.__contains__(u'?') or line.__contains__(u'？'):
                continue
            # 处理目录的页码
            line = self.removePageNum(line)
            # 处理陈述句，如果结尾有句号的，去掉
            line = line.strip(u'.。§ ')
            # 预处理特定词后缀
            line = self.processSuffix(line)
            # 先判断层次
            nlevel, nline = self.judgeLevel(line)
            if nlevel > 0:
                result.append(line)
            else:
                self.find_VIP_words(line, result)
        return result

    def find_VIP_words(self, line, result):
        for re_pattern in self.re_define:
            pattern = re.compile(re_pattern)
            vip_words = pattern.findall(line)

            for word_unstrip in vip_words:
                word = word_unstrip.strip(self.re_def_strip)
                word = ''.join(word.split())
                if self.statisPairs(word) == False:
                    continue
                result.append(word)

    def find_VIP_words_by_pattern(self, line):
        result = []
        for re_pattern in [self.re_def_4, self.re_def_5]:
            pattern = re.compile(re_pattern)
            vip_words = pattern.findall(line)

            for word_unstrip in vip_words:
                word = word_unstrip.strip(self.re_def_strip_vip)
                word = ''.join(word.split())
                if len(word) == 0:
                    continue
                result.append(word)
        return result

    def enlargeVipWords(self, origin_words, q):
        # string decode之后就是unicode了
        if isinstance(q, str):
            q = q.decode('utf-8')
        vip_words = self.find_VIP_words_by_pattern(q)
        all_words = origin_words + vip_words
        return all_words



    def process(self, sen):
        # 结果是一个列表，一句话可能要拆分成多个，大部分都不需要拆分
        pre_list = []

        # 处理陈述句，如果结尾有句号的，去掉
        sen = sen.strip(u'.。')

        # 如果包含问号，直接忽略
        if sen.__contains__(u'?') or sen.__contains__(u'？'):
            return pre_list


        # 如果结尾是概要，或者简介，导论，就去掉该词
        #if sen.endswith(u'概要') or sen.endswith(u'概述') or sen.endswith(u'简介') or sen.endswith(u'导论') or sen.endswith(u'总论'):
        #    sen = sen[:-2]
        #    if sen.endswith(u'的'):
        #        sen = sen[:-1]
        # 前缀处理，必须在去掉层级编号后，才可以处理，所以这里不处理


        # 预处理特定词后缀
        sen = self.processSuffix(sen)

        # 对于重点强调的是时间，则去掉时间内容
        for re_pat in self.re_date:
            pattern = re.compile(re_pat)
            res = pattern.findall(sen)
            if res:
                for one_res in res:
                    if isinstance(one_res, unicode):
                        sen = sen.replace(one_res, u'')
                    elif isinstance(one_res, tuple):
                        for one in one_res:
                            if len(one) == 0:
                                continue
                            sen = sen.replace(one, u'')

        # 中间如果有空格，对于中文要去掉，对于英文要保留

        #清空两边字符
        sen = sen.strip()
        sen = sen.strip(u'、：．，｛｝.,:{}')
        sen = sen.strip()

        # 消除中间空白,
        #sen = self.removeMidSpace4Chinese(sen)
        # 如果编号写在一行，则需要处理成多行
        # 处理换行符号 \n
        if sen.__contains__('\n'):
            candi_line_lst = sen.split('\n')
            for candi_line in candi_line_lst:
                self.processMultiLine(pre_list, candi_line)
        else:
            self.processMultiLine(pre_list, sen)

        return pre_list


    def processSuffix(self, line):
        if line.endswith(u'课堂笔记'):
            line = line.replace(u'课堂笔记','')
        if line.endswith(u'FAQ'):
            line = line.replace(u'FAQ','')
        if line.endswith(u'关键词汇'):
            line = line.replace(u'关键词汇','')
        if line.endswith(u'拓展资源'):
            line = line.replace(u'拓展资源','')

        return line.strip()

    def processMultiLine(self, pre_list ,sen):
        flag = False
        pre_sen = None
        suf_sen = None

        for re_pat in self.re_level:
            pattern = re.compile(re_pat[0])
            res = pattern.match(sen)
            if res:
                flag = True
                match_content = res.group()
                match_length = len(match_content)
                pre_sen = sen[:match_length]
                suf_sen = sen[match_length:]
                break
        if flag:
            for re_pat in [self.re_num_4, self.re_num_5, self.re_num_7, self.re_num_8, self.re_num_9]:
                #index = index + 1
                pattern = re.compile(re_pat)
                # 对于suf_sen再尝试进行分隔
                grps = pattern.findall(suf_sen)
                if grps:
                    for gp in grps:
                        suf_sen = suf_sen.replace(gp, u';')

                    break

            # 将分隔符统一成英文的分号
            suf_sen = suf_sen.replace(u'；', u';')

        # 如果flag=true 说明，可以尝试分拆的
        if flag:
            sub_sen_list = suf_sen.split(u';')
            for subsen in sub_sen_list:
                subsen = self.removeBracket(subsen)
                subsen_length = len(subsen)
                if subsen_length > 1 :
                    pre_list.append(pre_sen + subsen)
        # flag = false说明该行不是所需要的
        elif len(sen.strip()) > 1:
            pre_list.append(sen)

    def removeBracket(self, sen):
        # 对陈述句后面，带有小括号性的解释
        # 如果结尾是带小括号的，则把小括号扔掉
        pattern = re.compile(self.re_racket_mid)
        res_list = pattern.findall(sen)
        for item in res_list:
            sen = sen.replace(item, '')

        return sen

    def removeMidSpace4Chinese(self, sen):
        """
        删除中文之间的空格，英文之间的不要删
        :param sen: 
        :return: 
        """
        pre_ch = None
        cur_ch_iscn = False
        cur_ch_isalpha = False
        pre_ch_isalpha1 = False
        pre_ch_isalpha2 = False
        res = []
        for ch in sen:
            if UnicodeConvertor.is_empty(ch):
                # 如果前面是空格，继续跳过，多个空格只保留一个即可
                if UnicodeConvertor.is_empty(pre_ch):
                    continue
                else:
                    cur_ch_isalnum = False

            else:
                cur_ch_iscn = UnicodeConvertor.is_chinese(ch)
                cur_ch_isalpha = ch.isalpha()
                # 如果当前是数字或者英文，前一个是空格，再前一个是数字或者英文，中间的空格保留一个
                if cur_ch_iscn == False and cur_ch_isalpha == True and UnicodeConvertor.is_empty(pre_ch) and  pre_ch_isalpha2 == True:
                    res.append(u' ')
                res.append(ch)

            pre_ch = ch
            pre_ch_isalpha2 = pre_ch_isalpha1
            pre_ch_isalpha1 = cur_ch_isalpha and cur_ch_iscn == False

        return ''.join(res)
    def removePageNum(self, sen):
        # 对陈述句后面，带有小括号性的解释
        # 如果结尾是带小括号的，则把小括号扔掉
        pattern = re.compile(self.re_noues_pagenum)
        res_list = pattern.findall(sen)
        for item in res_list:
            sen = sen.replace(item, '')
        return sen


    def removeByRegexPattern(self, pattern_list, sen):
        """
        如果符合正则的，不要该句子
        :param pattern_list: 
        :param sen: 
        :return: 
        """

        for pattern in pattern_list:
            pattern = re.compile(pattern)
            res_list = pattern.findall(sen)
            if len(res_list) > 0:
                sen = u''
                break

        return sen


    def statisPairs(self, sen):
        """
        统计行中的符号对，是否成对出现，不成对的去掉
        成对的符号：“”，《》
        :param sen: 
        :return: 
        """
        # 先初始化符号字典
        for pair in self.sign_pairs:
            self.sign_dict[pair[0]] = 0
            self.sign_dict[pair[1]] = 0

        # 赋值
        for ch in sen:
            if self.sign_dict.__contains__(ch):
                self.sign_dict[ch] += 1

        # 判断结果
        flag = True
        for pair in self.sign_pairs:
            left_sign_count = self.sign_dict[pair[0]]
            right_sign_count = self.sign_dict[pair[1]]
            if left_sign_count <> right_sign_count:
                flag = False
                break


        return flag

    def getPreSectionByIndex(self, sen):

        if len(sen) > 30:
            gotit = False
            for sign in self.signlist:

                index = sen.find(sign)
                if index < 30 and index > 1:
                    gotit = True
                    sen = sen[:index]
                    break
            if gotit == False:
                sen = u''
        if sen.__contains__(u'，') or sen.__contains__(u'、'):
            sen = u''


        return sen

    def getAutoNumCode(self, level):
        num_code = u'1'
        level_code_lst =[]

        for i in range(level):
            level_code_lst.append(num_code)
            if i < level:
                level_code_lst.append(u'.')

        level_code_lst.append(num_code)
        code = ''.join(level_code_lst) + u'、'

        return code
    def judgeLevel(self, line):
        flag = False
        level = -1
        index = 0
        depth = 0

        for re_pat in self.re_level:
            index = re_pat[1]
            pattern = re.compile(re_pat[0])
            res = pattern.match(line)
            if res:
                flag = True
                match_content = res.group()
                dotsplit = match_content.split(u'.')
                depth = len(dotsplit) - 1
                match_length = len(match_content)
                line = line[match_length:]
                #line = line.replace(match_content, '')

                break
        # 是否匹配了模式，如果没有匹配，level返回-1
        if flag :
            level = index

        return level + depth, line

if __name__ == "__main__":
    sp = SenPreprocess()
    sen = u'( 1) 一般经营大宗商品买卖, 商品购销量大, 企业规模相应较'
    pattern = re.compile(sp.re_num_7)
    res = pattern.findall(sen)
    content = res[0]
    content1 = content.strip(u'也称为所谓,.;，：；、。—')
    sen = u'过电话来进行的访谈调查就称为电话访谈,国内称这种形式的访谈为“调查会”或“座谈会”'
    pattern = re.compile(sp.re_def_2)
    res = pattern.findall(sen)
    content = res[0]
    content1 = content.strip(u'也称为,.;，：；、。—')

    sen = u'二 集束柱2、拱顶、拱券和沉重的墙3、彩色玻璃4、雕刻艺术，二者有明显不同'
    res = pattern.match(sen)

    sen = u'什么是简单的逻辑方法'
    sen = sen[3:]

    sen = u'3423'
    lst = sen.split(u'.')
    sen = u'3423.33.42'
    lst = sen.split(u'.')

    sen = u'600 000元转为短期贷款。'
    res = sp.removeMidSpace4Chinese(sen)

    code = sp.getAutoNumCode(0)
    code = sp.getAutoNumCode(1)
    code = sp.getAutoNumCode(2)
    print res