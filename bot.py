import logging
import sys

from khl import Bot

from utils import commands, events
from utils.config import Config


class GenshinBot(Bot):

    def __init__(self, config: Config):
        self.config = config
        logging.basicConfig(level=self.config.log_level,
                            format='[%(asctime)s] [%(module)s] [%(threadName)s/%(levelname)s]: %(message)s')

        super().__init__(self.config.token)

        commands.registry(self)
        events.registry(self)


def main():
    bot = GenshinBot(Config.load())
    bot.run()


if __name__ == '__main__':
    sys.exit(main())
