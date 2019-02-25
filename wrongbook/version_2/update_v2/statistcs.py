# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-12-13
program       : *_* statistcs knowledge and question in neo4j*_*

"""
import os
import sys
from database import Neo4jHandler
from domain import FilePath

reload(sys)
sys.setdefaultencoding('utf-8')

class Statistics:
    """
    statistics data in neo4j.
    
    模糊查询库中的数据
    match(p:Knowledge)-[r:CHILD]->(c:Knowledge) where p.code=~'open.bc.1.*' return p,c
    
    """

    def __init__(self):
        """
        initialize local variables.
        """
        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)


    def execute(self, filepath):
        """
        执行统计任务
        :return: 
        """
        # 第一步先获取到那些试题是需要统计的，要得到试题id的列表
        print '获取需要评估的试题列表'
        exam_id_list = self.getExamIdList(filepath)

        # 第二步生成查询语句
        print '生成查询试题推荐的语句'
        cypher_list = self.getCypherList(exam_id_list)

        # 第三步执行查询，返回结果计数数组
        print '执行查询语句'
        #count_list = self.getRecommendCount(cypher_list)
        # 保存试题与推荐的数
        print '试题与推荐数'
        count_list = self.loadRecommendFromFile()
        self.saveExamAndRecommend(exam_id_list, count_list)

        # 统计推荐0的情况，第一种是关联不上知识点的推荐0，第二种是只关联一个知识点，没有其他试题可推
        zero_dict = self.getRecommendCountFor0(exam_id_list, count_list)
        print '没有关联知识点的数量为：{}， 只关联一个知识点的数量为：{}'.format(zero_dict['0'], zero_dict['1'])

        # 第四步统计结果输出, 统计数据分布[区间计数]
        print '统计分布'
        distribution_dict = self.getDistribution(count_list)
        # 计算分布占比,并打印
        print '计算区间占比'
        self.computeDistributionRate(distribution_dict)
        pass

    def loadRecommendFromFile(self):
        filepath = u'./../../../data/course-knowledge-machine/20181217-800plus-combine/recommend_list.txt'
        f_input = open(filepath, 'r')
        line = f_input.read()
        count_list = line.split(',')
        return count_list
    def saveExamAndRecommend(self, exam_id_list, count_list):
        filepath = u'./../../../data/course-knowledge-machine/20181217-800plus-combine/exam_recommend.txt'
        fout = open(filepath, 'w')
        for exam_id, count in zip(exam_id_list, count_list):
            fout.write('{}   {}'.format(exam_id, count))
            fout.write('\n')

        fout.close()

    def computeDistributionRate(self, distribution_dict):
        """
        计算占比
        :param distribution_dict: 
        :return: 
        """
        count_total = 0.0
        for key, val in distribution_dict.items():
            count_total += val

        distribution_rate = []
        for key, val in distribution_dict.items():
            rate = float(val) / count_total
            distribution_rate.append((key, rate))

        print distribution_rate

    def getDistribution(self, count_list):
        """
        计算数据列表的区域分布
        区域分布分为几个范围0, 1-2, 3-5, 6-10, 11-20,21+
        
        :param count_list: 
        :return: 
        """
        distribution_dict = {}
        distribution_dict['0'] = 0
        distribution_dict['1-2'] = 0
        distribution_dict['3-5'] = 0
        distribution_dict['6-10'] = 0
        distribution_dict['11-20'] = 0
        distribution_dict['21+'] = 0
        for count in count_list:
            if count == 0:
                distribution_dict['0'] += 1
            elif count > 0 and count < 3:
                distribution_dict['1-2'] += 1
            elif count > 2 and count < 6:
                distribution_dict['3-5'] += 1
            elif count > 5 and count < 11:
                distribution_dict['6-10'] += 1
            elif count > 10 and count < 21:
                distribution_dict['11-20'] += 1
            else:
                distribution_dict['21+'] += 1

        # 打印分布

        return distribution_dict

    def getRecommendCountFor0(self, exam_id_list, count_list):
        index = 0
        length = len(count_list)
        zero_dict = {}
        zero_dict['0']=0
        zero_dict['1']=0

        for exam_id, count in zip(exam_id_list, count_list):
            count = int(count.strip())
            if count > 0:
                index += 1
                continue
            cypherstatement = "match (rq)-[:SAME]-(m)-[:CHECK]-(n) where rq.code='{}' return count(n)".format(exam_id)
            # 再统计是否有知识点
            index += 1
            print '正在处理第{}/{}题'.format(index, length)
            with self.neo4jdriver.driver.session() as session:
                with session.begin_transaction() as tx:
                    result = tx.run(cypherstatement).records()
                    zero_count = 0
                    for record in result:
                        zero_count = record[0]
                    if zero_count == 1:
                        zero_dict['1'] += 1
                    else:
                        zero_dict['0'] += 1
        return zero_dict

    def getRecommendCount(self, cypher_list):
        """
        执行查询语句，记录结果数据
        :param cypher_list: 
        :return: 
        """
        length = len(cypher_list)
        index = 0
        count_list = []
        for cypherstatement in cypher_list:
            index += 1
            print '正在处理第{}/{}题'.format(index, length)
            with self.neo4jdriver.driver.session() as session:
                with session.begin_transaction() as tx:
                    result = tx.run(cypherstatement).records()
                    for record in result:
                        count_list.append(record[0])
        print count_list
        return count_list

    def getCypherList(self, exam_id_list):
        """
        根据试题id生成查询语句
        
        :param exam_id_list: 
        :return: 
        """
        cypher_list = []
        template = "match (rq)-[:SAME]->(rqg)<-[:CHECK]-(k)-[:CHECK]->(res) where rq.code='{}' return count(res)"
        for exam_id in exam_id_list:
            cypher_list.append(template.format(exam_id))

        return cypher_list

    def getExamIdList(self, filepath):
        """
        读取试题列表
        :param filepath: 
        :return: 
        """
        exam_id_list = []
        f_in = open(filepath, 'r')
        for line in f_in:
            exam_id_list.append(line.strip('\n'))
        return exam_id_list

if __name__ == "__main__":
    s = Statistics()
    #filepath = u'20181122-200plus'
    filedirectory = u'20181217-800plus-combine'
    filename = u'processed_exam_question.txt'
    rootpath = u'./../../../data/course-knowledge-machine/{}/{}'.format(filedirectory, filename)

    s.execute(rootpath)