from nonebot import logger, on_message, on_regex
from nonebot.rule import fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from httpx import AsyncClient
import base64
from re import findall
from sys import exc_info
import httpx

hitokoto = on_message(fullmatch(("牛牛回声"), ignorecase=False), priority=7)


@hitokoto.handle()
async def hit():
    try:
        async with AsyncClient() as client:
            req_url = "https://v1.hitokoto.cn/?c=a&c=b&c=c&c=d&c=h"
            res = await client.get(req_url, timeout=120)
            text = res.json()['hitokoto']
            who = res.json()['from']
    except Exception as e:
        logger.warning(e)
        await hitokoto.finish("嗯..波奇酱。我好像把这件事情搞砸了...")
    await hitokoto.finish(text + "\n----" + who)
