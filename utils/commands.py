from typing import TYPE_CHECKING

from khl import Message
from khl_card.accessory import *
from khl_card.card import Card
from khl_card.modules import *
from khl_card.types import ThemeTypes, NamedColor

from .genshin.genshin import Sign

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

    @genshin_bot.command(name='unbind')
    async def unbind(msg: Message, index: int):
        await msg.delete()
        if genshin_bot.cookies.remove_cookie(msg.author.id, index - 1):
            await msg.ctx.channel.send('解除绑定成功', temp_target_id=msg.author.id)
        else:
            await msg.ctx.channel.send('解除绑定失败', temp_target_id=msg.author.id)

    @genshin_bot.command(name='list')
    async def cookies_list(msg: Message):
        await msg.delete()
        cookies = genshin_bot.cookies.list_cookies(msg.author.id)
        if cookies is None:
            await msg.ctx.channel.send('当前没有绑定信息', temp_target_id=msg.author.id)
            return
        else:
            card = Card(Header('绑定列表'), color=NamedColor.YELLOW)
            for i in range(len(cookies)):
                card.append(Section(Kmarkdown(f'{i + 1}. {cookies[i].replace(cookies[i][5:-5], "*********", 1)}')))
            await msg.ctx.channel.send([card.build()], temp_target_id=msg.author.id)

    @genshin_bot.command(name='sign')
    async def sign(msg: Message):
        await msg.delete()
        cookies = genshin_bot.cookies.list_cookies(msg.author.id)
        if cookies is None:
            await msg.ctx.channel.send('当前没有绑定信息', temp_target_id=msg.author.id)
            return
        else:
            for cookie in cookies:
                await msg.ctx.channel.send(await Sign(cookie, genshin_bot.logger).run(), temp_target_id=msg.author.id)
