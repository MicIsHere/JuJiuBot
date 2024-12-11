import random

from nonebot import on_regex
from nonebot.exception import IgnoredException
from nonebot.params import RegexGroup

from src.common.config import plugin_config

question = on_regex(r"^([?？¿!！¡\s]+)$", priority=6, block=False)


@question.handle()
async def _(rgx: tuple = RegexGroup()):
    if not plugin_config.questionmark_enable:
        return
    if not rgx:
        raise IgnoredException
    mark = rgx[0] \
        .replace("¿", "d").replace("?", "¿").replace("？", "¿").replace("d", "?") \
        .replace("¡", "d").replace("!", "¡").replace("！", "¡").replace("d", "!")
    
    if random.random() < plugin_config.questionmark_trigger_rate & (str(mark) != " "):
        await question.send(mark)
