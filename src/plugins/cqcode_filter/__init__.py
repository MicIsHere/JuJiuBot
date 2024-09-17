from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor

@event_preprocessor
async def do_something(event: GroupMessageEvent):
    return