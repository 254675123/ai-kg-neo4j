# -*- coding: utf-8 -*-
# coding=utf-8
"""
create_author : zhangcl
create_time   : 2018-11-05
program       : *_*  course exam question *_*
"""
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import xlwt

def writeExcelFile(filepath, sheet_datas):
    """
    保存若干个sheet中的数据
    :param filepath: excel文件名称，全路径
    :param sheet_datas: sheet的字典数据
    :return: 
    """
    wb = xlwt.Workbook()

    for s_sheet in sheet_datas.keys():
        # sheet的名称
        sheet = wb.add_sheet(s_sheet)
        # 单元格的格式
        style = 'pattern: pattern solid, fore_colour yellow; '  # 背景颜色为黄色
        style += 'font: bold on; '  # 粗体字
        style += 'align: horz centre, vert center; '  # 居中
        header_style = xlwt.easyxf(style)

        sheet_data = sheet_datas.get(s_sheet)
        row_count = len(sheet_data)
        for row in range(0, row_count):
            col_count = len(sheet_data[row])
            for col in range(0, col_count):
                content = sheet_data[row][col]
                if row == 0:  # 设置表头单元格的格式
                    sheet.write(row, col, content, header_style)
                else:
                    sheet.write(row, col, content)
    wb.save(filepath)



if __name__ == '__main__':
    # 二维数组
    datas = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h']]
    file_path = u'./../../data/course-knowledge-machine/20181026-600plus/q-src-xls/test.xls'

    wb = xlwt.Workbook()
    sheet = wb.add_sheet('test')  # sheet的名称为test

    # 单元格的格式
    style = 'pattern: pattern solid, fore_colour yellow; '  # 背景颜色为黄色
    style += 'font: bold on; '  # 粗体字
    style += 'align: horz centre, vert center; '  # 居中
    header_style = xlwt.easyxf(style)

    row_count = len(datas)
    col_count = len(datas[0])
    for row in range(0, row_count):
        col_count = len(datas[row])
        for col in range(0, col_count):
            if row == 0:  # 设置表头单元格的格式
                sheet.write(row, col, datas[row][col], header_style)
            else:
                sheet.write(row, col, datas[row][col])
    wb.save(file_path)