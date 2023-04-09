import toml
from typing import NoReturn

from chatGPT.bot import ChatBot
from CLI import utils

class CliApplication:

    def __init__(self, debug=False) -> None:
        with open("config.toml") as file:
            config = toml.loads(file.read())

        self.bot = ChatBot(config)
        self._debug = debug

        print(utils.wellcome_str(self.bot.wellcome_message))
        print(utils.hr1())

    def run(self) -> NoReturn:
        while True:
            try:
                prompt = input(utils.input_format(self.bot.user_name))
                print(utils.bot_format(self.bot.name), end="")
                response = self.bot.ask(prompt) # TODO handle stream responses here rather than in bot module.

                if not self.bot.stream:
                    print(response)

                print('\n')
                print(utils.hr2(), end="\n\n")

            except KeyboardInterrupt:
                print("\n\n", utils.exit_str(self.bot.exit_message))
                print(utils.hr1(), end="\n\n")
                exit()

            except Exception as exp:
                if self._debug:
                    raise
                print(utils.error_str(exp.with_traceback()))
                print(utils.hr2())
                continue
