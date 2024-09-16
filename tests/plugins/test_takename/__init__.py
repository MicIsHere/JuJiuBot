import random
from nonebot import require, logger, get_bot
from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import Message
from nonebot import logger, on_message, on_regex
from nonebot.rule import fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment, Message

from src.plugins.repeater.model import Chat
from src.common.config import BotConfig
from src.common.utils import is_bot_admin

change_name_sched = require('nonebot_plugin_apscheduler').scheduler


hitokoto = on_message(fullmatch(("牛牛测试"), ignorecase=False), priority=7)

@hitokoto.handle()
async def change_name():
    rand_messages = Chat.get_random_message_from_each_group()

    logger.info(get_bot())

    if not rand_messages:
        print(rand_messages)
        logger.info("no rand!")
        return

    for group_id, target_msg in rand_messages.items():
        logger.info("for!")

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

        logger.info(bot)

        try:
            logger.info("call!")
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
        await hitokoto.finish("来自开发者下发测试: "+str(group_id)+" group nickname -> "+str(card))
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
                    'card': random.choice(['帕拉斯', '牛牛', '牛牛喝酒', '牛牛干杯', '牛牛继续喝'])
                })

            # 戳一戳
            await bot.call_api('send_group_msg', **{
                'message': Message('[CQ:poke,qq={}]'.format(target_user_id)),
                'group_id': group_id
            })

            config.update_taken_name(target_user_id)

        except ActionFailed:
            # 可能牛牛退群了
            continue