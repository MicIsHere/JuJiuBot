import httpx
from nonebot import logger, on_message, on_regex
from nonebot.rule import fullmatch
from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment
from httpx import AsyncClient
from nonebot import on_startswith
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

matcher = on_startswith("牛牛对联 ", ignorecase=False)
notfindarg = on_message(fullmatch(("牛牛对联"), ignorecase=False), priority=7)


@matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    arg = str(event.message).replace("牛牛对联 ", "")
    logger.info("已获取到上联: " + arg)
    url = f'https://seq2seq-couplet-model.rssbrain.com/v0.2/couplet/' + arg
    async with httpx.AsyncClient() as client:
        res = await client.get(url=url)
    res = res.json()
    result = '\n'.join(['➤' + res['output'][n] for n in range(1)])
    if result == "➤":
        logger.info("未找到关联下联")
        await matcher.finish("看来是很怪异的上联呢。")
    elif result == "➤您的输入太长了":
        logger.info("上联过长: " + result)
        await matcher.finish("上联太长了，完全对不出来。")
    else:
        logger.info("已找到关联下联: " + result)
        await matcher.finish(result.replace("➤",""))

@notfindarg.handle()
async def _notfindarg(bot: Bot, event: GroupMessageEvent):
    logger.info("未输入上联")
    await matcher.finish("请告诉我上联是什么。")
