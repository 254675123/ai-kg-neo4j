# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-07-16
program       : *_* word factory *_*

"""

from database import Neo4jHandler
import Queue
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
class WordFactory:
    """
    CHAR net generator.
    merge (c1:CHAR {name:'国'}) 
    merge (c2:CHAR {name:'家'})
    merge (c1)-[r:NEXT]-(c2) 
    on create set r.weight = 1
    on match set r.weight = r.weight + 1
    return c1, c2
    """
    def __init__(self):
        """
        initialize local variables.
        """
        self.neo4jdriver = Neo4jHandler.Neo4jHandler(None)
        #self.cypherlist = []
        self.sentcypherlist = []
        self.nousecharlist = []
        self.hasquerydict = {}
        self.inqueue = {}
        #self.cypherlist.append("CREATE CONSTRAINT ON (c:WORD) ASSERT c.name IS UNIQUE;")
        self.wordposlist = []
        # 把停用词做成字典
        self.stopwords = {}
        fstop = open('./../data/stopwords-single.txt', 'r')
        for eachWord in fstop:
            self.stopwords[eachWord.strip().decode('utf-8', 'ignore')] = eachWord.strip().decode('utf-8', 'ignore')
        fstop.close()

    def generateWord(self):
        # 查找关系总数
        total_count = self.getRelationTotalCount()
        threshold = total_count / 10
        print 'total count:' + str(threshold)
        # 获取关系数范围的节点
        #charlist = self.getSpecifyRelationCound(50,0)
        queue_char = self.getSpecifyRelationCound(10, 0)
        # 遍历每一个节点，查找它的下一个字
        self.getWordlistQueue(queue_char, 10, 0)

        # 根据字典生成词
        words = self.generator()
        print len(words)

    def generator(self):
        print 'generate word start.'
        words = []
        # 先将词放入队列
        q = Queue.Queue()
        for key in self.hasquerydict.keys():
            if self.stopwords.__contains__(key):
                continue
            val_tup_list = self.hasquerydict[key]
            for val_tup in val_tup_list:
                nx_word = val_tup[0]
                count = val_tup[1]
                if key == nx_word:
                    continue
                new_tup = (key+nx_word, count, nx_word)
                q.put(new_tup)

        # 从队列中一步一步往后移
        while not q.empty():
            pre_tup = q.get()
            pre_count = pre_tup[1]
            pre_word = pre_tup[2]
            if not self.hasquerydict.__contains__(pre_word):
                words.append(pre_tup[0])
            else:
                cur_tup_list = self.hasquerydict[pre_word]
                for cur_tup in cur_tup_list:
                    cur_count = cur_tup[1]
                    if cur_count >= pre_count:
                        new_tup = (pre_tup[0]+cur_tup[0], cur_count, cur_tup[0])
                        q.put(new_tup)
                    elif not words.__contains__(pre_tup[0]):
                        words.append(pre_tup[0])
        print 'generate word end.'
        return words


    def getRelationTotalCount(self):
        """
        match (n:CHAR)-[r:NEXT]-(m:CHAR)  return count(r)
        :return: 
        """
        total_count = 0
        res = self.neo4jdriver.cypherexecuter("match (n:CHAR)-[r:NEXT]-(m:CHAR)  return max(r.weight)")
        record = res.records()
        for rec in record:
            total_count = rec[0]
            break
        return total_count



    def getSpecifyRelationCound(self, mincount=0, maxcount=0):
        """
        获取指定关系数的字集
        :param mincount: 
        :param maxcount: 
        :return: 
        """
        print 'get char list start.'

        ns = None
        if maxcount == 0:
            ns = "match (n:CHAR)-[r:NEXT]->(m:CHAR) where r.weight > {0} return distinct n.name".format(mincount)
        else:
            ns = "match (n:CHAR)-[r:NEXT]->(m:CHAR) where r.weight > {0} and r.weight < {1} return distinct n.name".format(mincount,maxcount)

        res = self.neo4jdriver.cypherexecuter(ns)
        record = res.records()
        #charlist = []
        q = Queue.Queue()
        for rec in record:
            char = rec[0]
            #charlist.append(char)
            if self.stopwords.__contains__(char):
                continue
            q.put(char)
            self.inqueue[char]=''
            print char
        #return charlist
        print 'get char list over.'
        return q

    def getWordlistQueue(self, charqueue, mincount=0, maxcount=0):
        if charqueue.empty():
            return

        print 'create single word dict start.'
        while not charqueue.empty():
            char = charqueue.get()
            del self.inqueue[char]
            if self.nousecharlist.__contains__(char) or self.hasquerydict.__contains__(char):
                continue

            ns = None
            if maxcount == 0:
                ns = "match (n:CHAR)-[r:NEXT]->(m:CHAR) where r.weight > {0} and n.name = '{1}' return m.name, r.weight".format(mincount, char)
            else:
                ns = "match (n:CHAR)-[r:NEXT]->(m:CHAR) where r.weight > {0} and r.weight < {1}  and n.name = '{1}'  return m.name, r.weight".format(
                    mincount, maxcount, char)

            res = self.neo4jdriver.cypherexecuter(ns)
            record = res.records()

            hasexist = False

            charlist = []
            tuplist = []
            for rec in record:
                hasexist = True
                ch = rec[0]
                count = rec[1]
                tup = (ch, count)
                tuplist.append(tup)
                if not self.hasquerydict.__contains__(ch) and not self.nousecharlist.__contains__(ch) \
                        and not self.inqueue.__contains__(ch):
                    charqueue.put(ch)
                    self.inqueue[ch] = ''

            if hasexist == False:
                self.nousecharlist.append(char)
                continue

            self.hasquerydict[char] = tuplist

        print 'create single word dict over.'


    def getWordlistIterate(self, charlist, mincount=0, maxcount=0):
        if len(charlist) == 0:
            return

        for char in charlist:
            if self.nousecharlist.__contains__(char):
                continue

            ns = None
            if maxcount == 0:
                ns = "match (n:CHAR)-[r:NEXT]->(m:CHAR) where r.weight > {0} and n.name = '{1}' return m.name, r.weight".format(mincount, char)
            else:
                ns = "match (n:CHAR)-[r:NEXT]->(m:CHAR) where r.weight > {0} and r.weight < {1}  and n.name = '{1}'  return m.name, r.weight".format(
                    mincount, maxcount, char)

            res = self.neo4jdriver.cypherexecuter(ns)
            record = res.records()

            hasexist = False

            charlist = []
            tuplist = []
            for rec in record:
                hasexist = True
                ch = rec[0]
                count = rec[1]
                tup = (ch, count)
                tuplist.append(tup)
                charlist.append(ch)

            if hasexist == False:
                self.nousecharlist.append(char)
                continue

            self.getWordlistIterate(charlist,mincount,maxcount)
            self.hasquerydict[char] = tuplist

if __name__ == "__main__":
    sr = WordFactory()
    #sr.generateCypher()
    sr.generateWord()


    print 'split over'