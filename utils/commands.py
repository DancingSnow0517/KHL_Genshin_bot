from typing import TYPE_CHECKING

from khl import Message
from khl_card.card import Card
from khl_card.types import Theme
from khl_card.modules import *
from khl_card.accessory import *

if TYPE_CHECKING:
    from ..bot import GenshinBot

help_messages = '''[!!help] 显示帮助信息'''


def registry(genshin_bot: 'GenshinBot'):
    @genshin_bot.command(name='help')
    async def reply_help(msg: Message):
        card = Card([
            Section(Kmarkdown(f'```\n{help_messages}\n```'))
        ], theme=Theme.SUCCESS)

    ...
