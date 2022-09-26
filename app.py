# -*- coding=utf-8 -*-
'''

开心Python Flask Django 学习交流q群：217840699


Author  : J.sky
Mail    : bosichong@qq.com


特别感谢以下二位大佬的鼎力支持！

Author  : rcddup
Mail    : 410093793@qq.com

Author  : andywu1998
Mail    : 1078539713@qq.com


'''
__version__ = "1.1.0"

import random

import click
from flask import Flask, render_template, jsonify, request

from .APPconfig import AppConfig
from .PrintPreview import PrintPreview
from .Psmrcddup import Generator

app = Flask('web')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.secret_key = 'secret string'

# APP配置文件对象
appConfig = AppConfig()


# 程序配置文件对象


@app.route('/')
def index():
    # appConfig.isINI()
    return render_template("index.html", )


@app.route('/api_getConfigJson')
def getConfigJson():
    '''
    打开程序首页后加载程序的默认配置
    '''
    # print(appConfig.loadINI())
    rs = {'config': appConfig.loadINI(), }
    return jsonify(rs)


@app.route('/api_createPSM', methods=['POST'])
def createPSM():
    '''
    创建一组口算题的配置,接收前端送来的一组口算题配置，判断配置是否合法。
    '''
    jsondata = request.get_json()
    # print(jsondata)
    rs = {"info": isZeroA(jsondata["step"], jsondata["signum"],
                          jsondata["multistep"], jsondata["symbols"], jsondata["number"], jsondata["div"]["remainder"],
                          jsondata["is_result"])}
    return jsonify(rs)


@app.route('/api_producePSM', methods=['POST'])
def producePSM():
    '''
    接受前端发来的口算题配置生成口算题并保存到文件
    '''
    jsondata = request.get_json()
    isok = produce_PSM(jsondata)
    rs = getRstr(isok)
    return jsonify(rs)


def getRstr(isok):
    '''
    根据判断返回口算题是否生成的提示文字
    :param isok bool
    :return bool
    '''
    if isok:
        rs = {"info": "口算题生成完毕！"}
    else:
        rs = {"info": "口算题生成失败！"}
    return rs


#############################

def isZeroA(step, signum, multistep, symbols, number, remainder, is_result):
    '''
    运算中除数<=0的判断,及除法结果有余数是不能是用求算数项
    '''

    if step == 1 and signum == 4:
        if multistep[1][0] <= 0:
            return 0  # 除数不能为0
        if remainder != 2 and is_result == 1:
            return 0  # 求算数项是不能有余数

    # 多步运算时除法余数为零判断
    if step > 1:
        if (4 in symbols[0] and multistep[1][0] <= 0) or (
                4 in symbols[1] and multistep[2][0] <= 0) or (
                4 in symbols[2] and multistep[3][0] <= 0):
            return 0
        if (remainder != 2 and is_result == 1) or (remainder != 2 and step > 1):
            return 0  # 求算数项是不能有余数，多步的运算的时候不能有余数

    str_number = str(number)
    if step == 1:
        if signum == 1:
            return "加法口算题" + str_number + "道|||"
        elif signum == 2:
            return "减法口算题" + str_number + "道|||"
        elif signum == 3:
            return "乘法口算题" + str_number + "道|||"
        elif signum == 4:
            return "除法口算题" + str_number + "道|||"
        else:
            raise Exception("没有这个题型哦")
    elif step == 2:
        return "两步计算口算题" + str_number + "道|||"

    elif step == 3:
        return "三步计算口算题" + str_number + "道|||"


def produce_PSM(json_data):
    '''发布口算题保存.docx文件'''
    psm_list = []  # 口算题列表
    psm_title = []  # 标题列表
    print(json_data)
    if len(json_data[0]) == 0:
        print('还没有添加口算题到列表中哈！')  # 打印测试
        return 0
    else:
        # 循环生成每套题
        for i in range(json_data[1]["juanzishu"]):
            templist = getPsmList(json_data)  # 生成一页口算题
            random.shuffle(templist)  # 随机打乱
            psm_list.append(templist)  # 添加到list 准备后期打印
            # 为生成的文件起名r
            # psm_title.clear()

        for i in range(json_data[1]["juanzishu"]):
            psm_title.append(json_data[1]["jz_title"])
        # print(self.psm_title)
        subtit = json_data[1]["inf_title"]

        pp = PrintPreview(psm_list, psm_title,
                          subtit, col=json_data[1]["lieshu"], )
        pp.produce()  # 生成docx
        psm_list.clear()  # 清空打印列表。
        appConfig.saveAll(json_data)  # 保存所有配置项
        # self.movdocx()
        return 1


def getPsmList(json_data):
    '''
    根据配置文件生成一套口算题的所有题
    :param json_data 口算题的所有配置
    :return list 最终的口算题页
    '''
    templist = []
    for j in json_data[0]:
        # print(j)
        g = Generator(addattrs=j["add"], subattrs=j["sub"], multattrs=j["mult"], divattrs=j["div"],
                      symbols=j["symbols"], multistep=j[
                "multistep"], number=j["number"], signum=j["signum"], step=j["step"],
                      is_result=j["is_result"], is_bracket=j["is_bracket"], )
        templist = templist + g.generate_data()
    return templist


def q_PSM(json_data):
    '''
    命令行快速生成口算题
    :json_data 口算题配置文件
    '''
    psm_list = []  # 口算题列表
    psm_title = []  # 标题列表
    for i in range(json_data[1]["juanzishu"]):
        templist = getPsmList(json_data)  # 生成一页口算题
        random.shuffle(templist)  # 随机打乱
        psm_list.append(templist)  # 添加到list 准备后期打印
        # 为生成的文件起名r
        # psm_title.clear()

    for i in range(json_data[1]["juanzishu"]):
        psm_title.append(json_data[1]["jz_title"])

    subtit = json_data[1]["inf_title"]  # 小标题
    pp = PrintPreview(psm_list, psm_title,
                      subtit, col=json_data[1]["lieshu"], )
    pp.produce()  # 生成docx
    psm_list.clear()  # 清空打印列表。
    return 1


@app.cli.command("go")
@click.option('--id', default='0', help='口算题标识，根据标识可以快速生成口算题卷子')
@click.option('--q', default=3, help='需要打印的卷子数量')
@click.option('--row', default=3, help='口算卷子题的列数')
@click.option('--tit', default='小学生口算题', help='口算题卷子标题设置')
@click.option('--st', default='姓名：__________ 日期：____月____日 时间：________ 对题：____道', help='口算题标卷子副标题')
def one_click_creation(id, q, row, tit, st):
    '''
    命令行快速创建并生成口算题卷子

    '''

    if id == '0':
        click.echo("快生成口算题卷子的标识列表地址：")
        for v in psm_data.values():
            click.echo(v["id"] + "   :" + v["info"])
    elif id in psm_data:
        # click.echo(id)
        tempdata = {'juanzishu': q, 'lieshu': row, 'jz_title': tit, 'inf_title': st, }
        psm_data[id]["data"].append(tempdata)
        # click.echo(psm_data[id]["data"])
        if q_PSM(psm_data[id]["data"]):
            click.echo("口算题生成完毕！")
        else:
            click.echo("口算题生成失败！")

    else:
        click.echo("没有该题型，或是标识符号打错了！")


psm_data = {
    "a01": {"id": "a01", "info": "10以内加法口算题54道", "data":
        [[{'signum': 1, 'step': 1, 'number': 54, 'is_result': 0, 'is_bracket': 0, 'add': {'carry': 1},
           'sub': {'abdication': 1}, 'mult': {}, 'div': {'remainder': 2},
           'multistep': [[1, 9], [1, 9], [1, 9], [1, 9], [1, 99]], 'symbols': [[1], [2], [1]]}]]
            },
    "a02": {"id": "a02", "info": "10以内减法口算题54道", "data":
        [[{'signum': 2, 'step': 1, 'number': 54, 'is_result': 0, 'is_bracket': 0, 'add': {'carry': 1},
           'sub': {'abdication': 1}, 'mult': {}, 'div': {'remainder': 2},
           'multistep': [[1, 9], [1, 9], [1, 9], [1, 9], [1, 99]], 'symbols': [[1], [2], [1]]}]]
            },
    "a03": {"id": "a03", "info": "10以内加减法混合口算题54道", "data":
        [[{'signum': 1, 'step': 1, 'number': 27, 'is_result': 0, 'is_bracket': 0, 'add': {'carry': 1},
           'sub': {'abdication': 1}, 'mult': {}, 'div': {'remainder': 2},
           'multistep': [[1, 9], [1, 9], [1, 9], [1, 9], [1, 99]], 'symbols': [[1], [2], [1]]},
          {'signum': 2, 'step': 1, 'number': 27, 'is_result': 0, 'is_bracket': 0, 'add': {'carry': 1},
           'sub': {'abdication': 1}, 'mult': {}, 'div': {'remainder': 2},
           'multistep': [[1, 9], [1, 9], [1, 9], [1, 9], [1, 99]], 'symbols': [[1], [2], [1]]}]]
            },

}
