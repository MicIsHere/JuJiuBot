'''
Descripttion: 
version: 1.0
Author: Rene8028
Date: 2022-07-20 21:58:25
LastEditors: Rene8028
LastEditTime: 2022-07-20 22:54:46
'''


import datetime
from pathlib import Path
import sqlite3
from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP, Message, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot, Event
from nonebot.adapters.onebot.v11.message import Message
from nonebot import logger, on_message, on_regex
from nonebot.rule import fullmatch
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from typing import List
import random
from datetime import date
import time

data_dir = Path("data/jrrp2").absolute()
data_dir.mkdir(parents=True, exist_ok=True)
message: List[dict] = [
	{
		"expr": "jrrp == 100",
		"start": "！！！！！你今天的人品值是：",
		"end": "！100！100！！！！！"
	},
	{
		"expr": "jrrp == 99",
		"end": "！但不是 100……"
	},
	{
		"expr": "jrrp >= 90",
		"end": "！好评如潮！"
	},
	{
		"expr": "jrrp >= 60",
		"end": "！是不错的一天呢！"
	},
	{
		"expr": "jrrp > 50",
		"end": "！还行啦还行啦。"
	},
	{
		"expr": "jrrp == 50",
		"end": "！五五开……"
	},
	{
		"expr": "jrrp >= 40",
		"end": "！貌似还行？"
	},
	{
		"expr": "jrrp >= 20",
		"end": "！还……还行吧……？"
	},
	{
		"expr": "jrrp >= 11",
		"end": "！呜哇……"
	},
	{
		"expr": "jrrp >= 1",
		"end": "……（没错，是百分制）"
	},
	{
		"expr": "True",
		"end": "……"
	}
]

# '''数据库初始化'''
jdb = sqlite3.connect("data/jrrp2/jrrpdata.db")
cursor = jdb.cursor()

# '''表初始化'''
try:
    create_tb_cmd='''
    CREATE TABLE IF NOT EXISTS jdata
    (QQID int,
    Value int,
    Date text);
    '''
    cursor.execute(create_tb_cmd)
except:
    logger.error("cowJrrp Create data table failed")
    
#新增数据
def insert_tb(qqid,value,date):
    insert_tb_cmd = f'insert into jdata(QQID, Value, Date) values("{qqid}","{value}","{date}")'
    cursor.execute(insert_tb_cmd)
    jdb.commit()
#查询历史数据
def select_tb_all(qqid):
    select_tb_cmd = f'select *from jdata where QQID = {qqid}'
    cursor.execute(select_tb_cmd)
    return cursor.fetchall()
#查询今日是否存在数据
def select_tb_today(qqid,date):
    select_tb_cmd = f'select *from jdata where QQID = {qqid} and Date = {date}'
    cursor.execute(select_tb_cmd)
    results = cursor.fetchall()
    if results:
        return True
    return False
#判断是否本周
def same_week(dateString):
    d1 = datetime.datetime.strptime(dateString,'%y%m%d')
    d2 = datetime.datetime.today()
    return d1.isocalendar()[1] == d2.isocalendar()[1] \
              and d1.year == d2.year
#判断是否本月
def same_month(dateString):
    d1 = datetime.datetime.strptime(dateString,'%y%m%d')
    d2 = datetime.datetime.today()
    return d1.month == d2.month \
              and d1.year == d2.year

def get_jrrp(string: str):
    now = time.localtime()
    num = round(abs((get_hash("".join([
        "asdfgbn",
        str(now.tm_yday),
        "12#3$45",
        str(now.tm_year),
        "IUY"
    ])) / 3 + get_hash("".join([
        "QWERTY",
        string,
        "0*8&6",
        str(now.tm_mday),
        "kjhg"
    ])) / 3) / 527) % 1001)
    if num >= 970:
        num2 = 100
    else:
        num2 = round(num / 969 * 99)
    return num2

def rol(num: int, k: int, bits: int = 64):
    b1 = bin(num << k)[2:]
    if len(b1) <= bits:
        return int(b1, 2)
    return int(b1[-bits:], 2)

def get_hash(string: str):
    num = 5381
    num2 = len(string) - 1
    for i in range(num2 + 1):
        num = rol(num, 5) ^ num ^ ord(string[i])
    return num ^ 12218072394304324399

def get_msg(jrrp):
    start: str = "你今天的人品值是："
    end: str = "……"
    for msg_obj in message:
        if eval(msg_obj["expr"]):
            start = msg_obj.get("start") if msg_obj.get("start") else start
            end = msg_obj.get("end") if msg_obj.get("end") else end
            lumsg = start + str(jrrp) + end
            return lumsg

jrrp = on_message(fullmatch(("牛牛人品"), ignorecase=False), priority=7)
@jrrp.handle()
async def jrrp_handle(bot: Bot, event: Event):
    session = event.get_session_id()
    id = session.split('_')[2]
    lucknum = get_jrrp(id)
    if not select_tb_today(event.get_user_id(),date.today().strftime("%y%m%d")):
        insert_tb(event.get_user_id(),lucknum,date.today().strftime("%y%m%d"))
    result = get_msg(lucknum)
    reply = MessageSegment.reply(event.message_id)
    await jrrp.send(reply + result)

alljrrp = on_message(fullmatch(("牛牛历史人品"), ignorecase=False), priority=7)
@alljrrp.handle()
async def alljrrp_handle(bot: Bot, event: Event):
    alldata = select_tb_all(event.get_user_id())
    if alldata == None:
        await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您还没有过历史人品记录！'))
    times = len(alldata)
    allnum = 0
    for i in alldata:
        allnum = allnum + int(i[1])
    await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您一共使用了{times}天牛牛人品，您历史平均的人品指数是{round(allnum / times,1)}'))

monthjrrp = on_message(fullmatch(("牛牛本月人品"), ignorecase=False), priority=7)
@monthjrrp.handle()
async def monthjrrp_handle(bot: Bot, event: Event):
    alldata = select_tb_all(event.get_user_id())
    times = 0
    allnum = 0
    for i in alldata:
        if same_month(i[2]):
            times = times + 1
            allnum = allnum + int(i[1])
    if times == 0:
        await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您本月还没有过人品记录！'))
    await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您本月共使用了{times}天牛牛人品，平均的人品指数是{round(allnum / times,1)}'))

weekjrrp = on_message(fullmatch(("牛牛本周人品"), ignorecase=False), priority=7)
@weekjrrp.handle()
async def weekjrrp_handle(bot: Bot, event: Event):
    alldata = select_tb_all(event.get_user_id())
    if alldata == None:
        await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您还没有过历史人品记录！'))
    times = 0
    allnum = 0
    for i in alldata:
        if same_week(i[2]):
            times = times + 1
            allnum = allnum + int(i[1])
    if times == 0:
        await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您本周还没有过人品记录！'))
    await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您本周共使用了{times}次牛牛人品，平均的人品指数是{round(allnum / times,1)}'))
