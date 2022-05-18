from typing import TYPE_CHECKING

from khl import Message
from khl_card.accessory import *
from khl_card.card import Card
from khl_card.modules import *
from khl_card.types import ThemeTypes

if TYPE_CHECKING:
    from ..bot import GenshinBot

help_messages = '''[!!help] 显示帮助信息'''


def registry(genshin_bot: 'GenshinBot'):
    @genshin_bot.command(name='help')
    async def reply_help(msg: Message):
        await msg.delete()
        card = Card(Section(Kmarkdown(f'```\n{help_messages}\n```')), theme=ThemeTypes.SUCCESS)
        await msg.ctx.channel.send([card.build()], temp_target_id=msg.author.id)

    @genshin_bot.command(name='bind')
    async def bind(msg: Message, *cookie: str):
        await msg.delete()
        cookie = ' '.join(cookie)
        if genshin_bot.cookies.add_cookie(msg.author.id, cookie):
            await msg.ctx.channel.send('添加成功', temp_target_id=msg.author.id)
        else:
            await msg.ctx.channel.send('添加失败', temp_target_id=msg.author.id)
