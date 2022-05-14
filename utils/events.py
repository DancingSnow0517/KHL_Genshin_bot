from typing import TYPE_CHECKING

from khl import EventTypes, Bot, Event

if TYPE_CHECKING:
    from ..bot import GenshinBot


def registry(genshin_bot: 'GenshinBot'):
    @genshin_bot.on_event(EventTypes.ADDED_REACTION)
    async def add_role(_: Bot, event: Event):
        msg_id = event.body['msg_id']
        if genshin_bot.config.role_msg_id == msg_id:
            ...
        # print(event.body)
        ...
    ...
