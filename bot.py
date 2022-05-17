import logging
import os.path
import sys

from khl import Bot, Message, MessageTypes

from utils import commands, events, github_events
from utils.config import Config
from utils.logger import ColoredLogger


class GenshinBot(Bot):

    def __init__(self, config: Config):
        self.config = config
        self.config.save()

        self.logger = ColoredLogger(level=self.config.log_level)
        if self.config.log_file:
            self.logger.set_file(os.path.join('logs', 'latest.log'))
        self.patch()

        super().__init__(self.config.token)

        commands.registry(self)
        events.registry(self)

        self.task.add_interval(seconds=30, timezone='Asia/Shanghai')(self.push_github_events)

        self.client.register(MessageTypes.KMD, self.agree)

    async def push_github_events(self):
        await github_events.push_events(self)

    async def agree(self, msg: Message):
        if msg.ctx.channel.id == self.config.rule_channel_id:
            await msg.delete()
            agree_role_id = self.config.agree_role_id
            guild = msg.ctx.guild
            user = msg.author
            if agree_role_id not in user.roles:
                await guild.grant_role(user, str(agree_role_id))
                await msg.ctx.channel.send('你已经同意规则，希望能好好遵守！', temp_target_id=user.id)

    def patch(self):
        logging.getLogger = lambda name: self.logger
        import khl.command
        import khl.bot
        khl.receiver.log = self.logger
        khl.client.log = self.logger
        khl.requester.log = self.logger
        khl.command.command.log = self.logger
        khl.command.parser.log = self.logger
        khl.command.manager.log = self.logger
        khl.command.lexer.log = self.logger
        khl.bot.log = self.logger


def main():
    bot = GenshinBot(Config.load())
    bot.run()


if __name__ == '__main__':
    sys.exit(main())
