import contextlib
import random

from nonebot import on_regex, get_driver
from nonebot.exception import IgnoredException
from nonebot.internal.adapter import Event
from nonebot.params import RegexGroup

from .config import *

with contextlib.suppress(ImportError):
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as Event
cfg = Config.parse_obj(get_driver().config.dict())



question = on_regex(r"^([?？¿!！¡\s]+)$", priority=6, block=False)


@question.handle()
async def _(rgx: tuple = RegexGroup()):
    if not rgx:
        raise IgnoredException
    mark = rgx[0] \
        .replace("¿", "d").replace("?", "¿").replace("？", "¿").replace("d", "?") \
        .replace("¡", "d").replace("!", "¡").replace("！", "¡").replace("d", "!")
    
    if str(mark) != " ":
        await question.send(mark)
