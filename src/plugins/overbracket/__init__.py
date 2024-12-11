import random
from nonebot import on_message
from nonebot.adapters import Event

from src.common.config import plugin_config

obr = on_message(priority=25, block=False)


@obr.handle()
async def make_lbracket(event: Event):
    if not plugin_config.overbracket_enable:
        return
    msg = event.get_message().extract_plain_text()
    if len(msg) == 0:
        return
    last = msg[-1]
    if plugin_config.overbracket_nohalfsize and last in "([{":
        text = "半角异端！"
        chance = plugin_config.overbracket_purpose_chance
    elif last in plugin_config.overbracket_brackets:
        text = last
        chance = plugin_config.overbracket_purpose_chance
    else:
        text = random.choice(plugin_config.overbracket_brackets)
        chance = plugin_config.overbracket_base_chance

    assert 0 <= chance <= 1, "存在错误的概率数值，正确范围为 0~1 之间（包含两端）"

    if random.random() < chance:
        await obr.finish(text)