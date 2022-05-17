from typing import TYPE_CHECKING

from khl import Message
from khl_card.card import Card
from khl_card.types import ThemeTypes
from khl_card.modules import *
from khl_card.accessory import *

from .genshin.genshin import Sign

if TYPE_CHECKING:
    from ..bot import GenshinBot

help_messages = '''[!!help] 显示帮助信息'''


def registry(genshin_bot: 'GenshinBot'):
    @genshin_bot.command(name='help')
    async def reply_help(msg: Message):
        card = Card(Section(Kmarkdown(f'```\n{help_messages}\n```')), theme=ThemeTypes.SUCCESS)

    @genshin_bot.command(name='test')
    async def test(msg: Message):
        card_list = await Sign('UM_distinctid=17ddb7c8c10369-0c95c4c6d4ebec-4c607a68-190140-17ddb7c8c11a03; _ga=GA1.2.1841649756.1640064936; _MHYUUID=879aec77-925a-44a8-90d6-d40307f948d9; _gid=GA1.2.1398395830.1641877439; CNZZDATA1275023096=1840295802-1640064312-https%3A%2F%2Fgithub.com%2F|1641943737; ltoken=obXI5Da24dvV16Vz2wUgDgYanOji4cYbPoMGHyDq; ltuid=6527316; cookie_token=dUiITFfmdZuo8YHPH455cXK2Y36SlmyxTXysYgyW; account_id=6527316', '').run()
        await msg.reply(card_list)
