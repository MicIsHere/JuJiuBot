import random
import asyncio

from pathlib import Path
from nonebot import on_command, on_message, on_notice, get_driver, get_bot, logger
from nonebot.adapters.onebot.v11 import MessageSegment, Message, permission, GroupMessageEvent
from nonebot.rule import keyword, startswith, to_me, Rule
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from src.common.config import BotConfig, GroupConfig, UserConfig
from src.common.utils import is_bot_admin

from .wiki import WikiVoice

from ...common.utils.manager_message import alert_call

wiki = WikiVoice()
operator = 'Pallas'
greeting_voices = [
    '交谈1',
    '交谈2',
    '交谈3',
    '晋升后交谈1',
    '晋升后交谈2',
    '信赖提升后交谈1',
    '信赖提升后交谈2',
    '信赖提升后交谈3',
    '闲置',
    '干员报到',
    '精英化晋升1',
    '编入队伍',
    '任命队长',
    '戳一下',
    '信赖触摸',
    '问候',
]

# prts wiki 现在不让下载了
# 虽然可以通过加上 referer: https://prts.wiki/ 来绕过限制
# 但是人家既然加了 referer，就是不希望被爬，所以还是不爬了
# 请下载 https://huggingface.co/MistEO/Pallas-Bot/resolve/main/voices/voices.zip
# 解压放到 resource/voices/ 文件夹下（参考 resource/voices/path_structure.txt）

# wiki.download_voices(operator, 'char_485_pallas')

target_msgs = ['牛牛', '帕拉斯']


async def message_equal(bot: "Bot", event: "Event", state: T_State) -> bool:
    raw_msg = event.raw_message
    for target in target_msgs:
        if target == raw_msg:
            return True
    return False


call_me_cmd = on_message(
    rule=Rule(message_equal),
    priority=13,
    block=False,
    permission=permission.GROUP)


@call_me_cmd.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent, state: T_State):
    config = BotConfig(event.self_id, event.group_id)
    if not config.is_cooldown('call_me'):
        return
    config.refresh_cooldown('call_me')

    msg: Message = MessageSegment.record(
        file=Path(wiki.get_random_voice(operator, greeting_voices)).read_bytes())
    await call_me_cmd.finish(msg)


to_me_cmd = on_message(
    rule=to_me(),
    priority=14,
    block=False,
    permission=permission.GROUP)


@to_me_cmd.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent, state: T_State):
    config = BotConfig(event.self_id, event.group_id)
    if not config.is_cooldown('to_me'):
        return
    config.refresh_cooldown('to_me')

    if len(event.get_plaintext().strip()) == 0 and not event.reply:
        msg: Message = MessageSegment.record(
            file=Path(wiki.get_random_voice(operator, greeting_voices)).read_bytes())
        await to_me_cmd.finish(msg)


all_notice = on_notice(
    priority=1,
    block=False)


@all_notice.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    if event.notice_type == 'notify' and event.sub_type == 'poke' and event.target_id == event.self_id:
        is_group_notice = True

        # 尝试将群号赋值，如果抛出无属性异常则判定为私聊触发。
        # 赋值在之后的版本中会变为None
        try:
            active_notice_id = event.group_id
            # 加个判定解决
            if active_notice_id is None:
                is_group_notice = False
        except AttributeError:
            active_notice_id = event.target_id
            # 设置是否为群通知
            is_group_notice = False

        config = BotConfig(event.self_id, active_notice_id)
        if not config.is_cooldown('poke'):
            return
        config.refresh_cooldown('poke')

        delay = random.randint(1, 3)
        await asyncio.sleep(delay)
        config.refresh_cooldown('poke')

        # 判断不是群通知
        if not is_group_notice:
            logger.info("ready to send friend_poke for user {}".format(event.user_id))
            await get_bot(str(event.self_id)).call_api('friend_poke', **{
                'user_id': event.user_id
            })
            return

        logger.info("ready to send group_poke for user {} in group {}".format(event.user_id, event.group_id))
        await get_bot(str(event.self_id)).call_api('group_poke', **{
            "group_id": event.group_id,
            "user_id": event.user_id
        })

    elif event.notice_type == 'group_increase':
        if event.user_id == event.self_id:
            msg = '我是来自菊酒屋的菊酒牛牛，会在这里休息一段时间......虽然这么说，我渴望以美酒和戏剧被招待，更渴望走向战场。'
            alert_call("入群提示", "已加入群聊".format(event.group_id))
        elif await is_bot_admin(event.self_id, event.group_id):
            msg: Message = MessageSegment.at(event.user_id) + MessageSegment.text(
                '波奇酱，欢迎加入这盛大的庆典！我是来自菊酒屋的菊酒牛牛......要来一杯美酒么？')
        else:
            return
        await all_notice.finish(msg)

    elif event.notice_type == 'group_admin' and event.sub_type == 'set' and event.user_id == event.self_id:
        msg: Message = MessageSegment.record(
            file=Path(wiki.get_voice_filename(operator, '任命助理')).read_bytes())
        await all_notice.finish(msg)

    elif event.notice_type == 'friend_add':
        msg: Message = MessageSegment.record(
            file=Path(wiki.get_voice_filename(operator, '精英化晋升2')).read_bytes())
        await all_notice.finish(msg)

    # 被禁言自动退群
    elif event.notice_type == 'group_ban' and event.sub_type == 'ban' and event.user_id == event.self_id:
        alert_call("被禁言提示", "已退出群聊 {}".format(event.group_id))
        await get_bot(str(event.self_id)).call_api('set_group_leave', **{
            'group_id': event.group_id,
        })

    # 被踢了拉黑该群（所以拉黑了又能做什么呢）
    elif event.notice_type == 'group_decrease' and event.sub_type == 'kick_me':
        alert_call("被踢群提示", "已被群聊 {} 踢出".format(event.group_id))
        
        GroupConfig(event.group_id).ban()
        UserConfig(event.operator_id).ban()
