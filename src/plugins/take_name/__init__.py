import random
from numbers import Integral

from nonebot import require, logger, get_bot, on_message
from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import Message, Bot, GroupMessageEvent, permission
from nonebot.internal.rule import Rule
from nonebot.rule import fullmatch
from nonebot.typing import T_State
from pymongo import MongoClient

from src.plugins.repeater.model import Chat
from src.common.config import BotConfig, plugin_config
from src.common.utils import is_bot_admin

change_name_sched = require('nonebot_plugin_apscheduler').scheduler

blocklist_group = [787467591]
disable_can_block: bool = False

mongo_client = MongoClient(
    plugin_config.mongo_host, plugin_config.mongo_port, unicode_decode_error_handler='ignore')
mongo_db = mongo_client['JuJiuBot']
take_name_blocklist_mongo = mongo_db['take_name_blocklist']

@change_name_sched.scheduled_job('cron', minute='*/1')
async def change_name():
    rand_messages = Chat.get_random_message_from_each_group()
    if not rand_messages:
        return

    for group_id, target_msg in rand_messages.items():
        if random.random() > 0.002:  # 期望约每8个多小时改一次
            continue

        bot_id = target_msg['bot_id']
        config = BotConfig(bot_id, group_id)
        if config.is_sleep():
            continue

        target_user_id = target_msg['user_id']
        logger.info(
            'bot [{}] ready to change name by using [{}] in group [{}]'.format(
                bot_id, target_user_id, group_id))

        bot = get_bot(str(bot_id))

        if not bot:
            logger.error("no bot: " + str(bot_id))
            continue

        try:
            if group_id in blocklist_group:
                logger.info("bot [{}] blocked to change name by using [{}] in group [{}]")
                continue

            # 获取群友昵称
            info = await bot.call_api('get_group_member_info', **{
                'group_id': group_id,
                'user_id': target_user_id,
                'no_cache': True
            })
        except ActionFailed:
            # 可能这人退群了
            continue

        card = info['card'] if info['card'] else info['nickname']
        logger.info(
            'bot [{}] ready to change name to[{}] in group [{}]'.format(
                bot_id, card, group_id))
        try:
            # 改牛牛自己的群名片
            await bot.call_api('set_group_card', **{
                'group_id': group_id,
                'user_id': bot_id,
                'card': card
            })

            # 酒后夺舍！改群友的！
            if config.drunkenness() and await is_bot_admin(bot_id, group_id, True):
                await bot.call_api('set_group_card', **{
                    'group_id': group_id,
                    'user_id': target_user_id,
                    'card': random.choice(['菊酒牛牛', '牛牛', '牛牛喝酒', '牛牛干杯', '牛牛继续喝'])
                })

            # 戳一戳
            await bot.call_api('group_poke', **{
                'group_id': group_id,
                'user_id': target_user_id
            })

            config.update_taken_name(target_user_id)

        except ActionFailed:
            # 可能牛牛退群了
            continue

async def is_block_take_name(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    return event.get_plaintext().strip() in ['牛牛别改我名字', '牛牛不要改我名字', '牛牛不要改成我名字', '牛牛别改成我名字']

block_take_name = on_message(
    rule=Rule(is_block_take_name),
    priority=5,
    block=True,
    permission=permission.GROUP
)

@block_take_name.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if not disable_can_block:
        return
    take_name_blocklist_mongo.update_one(
        {'group_id': event.group_id},
        {'$set': {'qq_id': event.user_id}},
        upsert=True)