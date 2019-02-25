# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-09-26
program       : *_*  change chinese num to digital num  *_*

"""
import re
import sys



reload(sys)
sys.setdefaultencoding('utf-8')


class CnNumConvertor:
    """
    change chinese num to digital num.

    """

    def __init__(self):
        """
        initialize local variables.
        """
        #self.cn2digital =

CN_NUM = {
    u'〇': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'零': 0,
    u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4, u'伍': 5, u'陆': 6, u'柒': 7, u'捌': 8, u'玖': 9, u'貮': 2, u'两': 2,
}

CN_UNIT = {
    u'十': 10,
    u'拾': 10,
    u'百': 100,
    u'佰': 100,
    u'千': 1000,
    u'仟': 1000,
    u'万': 10000,
    u'萬': 10000,
    u'亿': 100000000,
    u'億': 100000000,
    u'兆': 1000000000000,
}

common_used_numerals_tmp ={u'零':0, u'一':1, u'二':2, u'两':2, u'三':3, u'四':4, u'五':5, u'六':6, u'七':7, u'八':8, u'九':9, u'十':10, u'百':100, u'千':1000, u'万':10000, u'亿':100000000}
# common_used_numerals= dict(zip(common_used_numerals_tmp.values(), common_used_numerals_tmp.keys())) #反转
# print(common_used_numerals)
def chinese2digits(uchars_chinese):
    total = 0
    r = 1              #表示单位：个十百千...
    for i in range(len(uchars_chinese) - 1, -1, -1):
        print(uchars_chinese[i])
        val = common_used_numerals_tmp.get(uchars_chinese[i])
        if val >= 10 and i == 0:  #应对 十三 十四 十*之类
            if val > r:
                r = val
                total = total + val
            else:
                r = r * val
                #total =total + r * x
        elif val >= 10:
            if val > r:
                r = val
            else:
                r = r * val
        else:
            total = total + r * val

    return total
print (chinese2digits(u'五百二十') )
print ( "-------------------------" )
print (  chinese2digits(u'十八') )
print ( "-------------------------" )
print ( chinese2digits(u'一亿零一'))



def chinese_to_arabic(cn):
    unit = 0  # current
    ldig = []  # digest
    for cndig in reversed(cn):
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000 or unit == 100000000:
                ldig.append(unit)
                unit = 1
        else:
            dig = CN_NUM.get(cndig)
            if unit:
                dig *= unit
                unit = 0
            ldig.append(dig)
    if unit == 10:
        ldig.append(10)
    val, tmp = 0, 0
    for x in reversed(ldig):
        if x == 10000 or x == 100000000:
            val += tmp * x
            tmp = 0
        else:
            tmp += x
    val += tmp
    return val

print (chinese_to_arabic(u'五百二十'))
print ("-------------------------")
print (chinese_to_arabic(u'十八'))
print ("-------------------------")
print (chinese_to_arabic(u'一亿零一'))
print (chinese_to_arabic(u'壹拾贰'))






