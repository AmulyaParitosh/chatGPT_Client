import toml

from chatGPT.bot import ChatBot
from CLI import utils

class CliApplication:

    def __init__(self):
        with open("config.toml") as file:
            config = toml.loads(file.read())

        self.bot = ChatBot(config)

        print(utils.wellcome_str(self.bot.wellcome_message))
        print(utils.hr1())

        while True:
            try:
                prompt = input(utils.input_format(self.bot.user_name))
                print(utils.bot_format(self.bot.name), end="")
                response = self.bot.ask(prompt)

                if not self.bot.stream:
                    print(response)

                print('\n')
                print(utils.hr2(), end="\n\n")

            except KeyboardInterrupt:
                print("\n\n", utils.exit_str(self.bot.exit_message))
                print(utils.hr1(), end="\n\n")
                exit()

            except Exception as exp:
                raise
                print(utils.error_str(exp.with_traceback()))
                print(utils.hr2())
                continue
