from contextlib import suppress

from nonebot import logger, on_command
from nonebot.adapters import Bot as BaseBot, Event as BaseEvent, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule, to_me
from nonebot_plugin_alconna.uniseg import UniMessage

from .config import config
from .statistics import cache_bot_info
from .templates import render_current_template


def check_empty_arg_rule(arg: Message = CommandArg()):
    return not arg.extract_plain_text()


def trigger_rule():
    rule = Rule(check_empty_arg_rule)
    if config.ps_need_at:
        rule = rule & to_me()
    return rule


_cmd, *_alias = config.ps_command

stat_matcher = on_message(fullmatch(("牛牛状态"), ignorecase=False), priority=7)

@stat_matcher.handle()
async def _(bot: BaseBot, event: BaseEvent):
    with suppress(Exception):
        await cache_bot_info(bot, event)
    try:
        ret = await render_current_template()
    except Exception:
        logger.exception("获取运行状态图失败")
        await UniMessage("貌似出了一些我不能解决的事情呢。").send(
            reply_to=config.ps_reply_target,
        )
    else:
        await UniMessage.image(raw=ret).send(reply_to=config.ps_reply_target)
