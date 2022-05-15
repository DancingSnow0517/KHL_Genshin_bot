from typing import TYPE_CHECKING

from khl import Message
from khl_card.card import Card
from khl_card.types import ThemeTypes
from khl_card.modules import *
from khl_card.accessory import *

if TYPE_CHECKING:
    from ..bot import GenshinBot

help_messages = '''[!!help] 显示帮助信息'''

agree_role_id = 3344336


def registry(genshin_bot: 'GenshinBot'):
    @genshin_bot.command(name='help')
    async def reply_help(msg: Message):
        card = Card([
            Section(Kmarkdown(f'```\n{help_messages}\n```'))
        ], theme=ThemeTypes.SUCCESS)

    @genshin_bot.command(name='agree', aliases=['我同意'], prefixes=[''])
    async def agree(msg: Message):
        if msg.ctx.channel.id == genshin_bot.config.rule_channel_id:
            await msg.delete()
            guild = msg.ctx.guild
            user = msg.author
            if agree_role_id not in user.roles:
                await guild.grant_role(user, str(agree_role_id))
                await msg.ctx.channel.send('你已经同意规则，希望能好好遵守！', temp_target_id=user.id)
