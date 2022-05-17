from typing import TYPE_CHECKING

from khl import EventTypes, Bot, Event

if TYPE_CHECKING:
    from ..bot import GenshinBot


def registry(genshin_bot: 'GenshinBot'):
    @genshin_bot.on_event(EventTypes.ADDED_REACTION)
    async def add_role(_: Bot, event: Event):
        msg_id = event.body['msg_id']
        user_id = event.body['user_id']
        emoji_map = genshin_bot.config.emoji_to_role_id_map
        if msg_id == genshin_bot.config.role_msg_id:
            guild = await genshin_bot.fetch_guild(genshin_bot.config.guild_id)
            user = await guild.fetch_user(user_id)
            roles = user.roles
            for role_id in emoji_map.values():
                if role_id in roles:
                    await guild.revoke_role(user, str(role_id))
            await guild.grant_role(user, str(emoji_map[event.body['emoji']['id']]))
