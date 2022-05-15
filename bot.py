import logging
import sys

from khl import Bot

from utils import commands, events, github_events
from utils.config import Config


class GenshinBot(Bot):

    def __init__(self, config: Config):
        self.config = config
        self.config.save()
        logging.basicConfig(level=self.config.log_level,
                            format='[%(asctime)s] [%(module)s] [%(threadName)s/%(levelname)s]: %(message)s')

        super().__init__(self.config.token)

        commands.registry(self)
        events.registry(self)

        self.task.add_interval(seconds=30, timezone='Asia/Shanghai')(self.push_github_events)

    async def push_github_events(self):
        await github_events.push_events(self)


def main():
    bot = GenshinBot(Config.load())
    bot.run()


if __name__ == '__main__':
    sys.exit(main())
