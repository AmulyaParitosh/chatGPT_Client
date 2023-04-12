import sys
from typing import NoReturn

import toml
from pynput.keyboard import Key, Listener

from chatGPT.bot import ChatBot
from chatGPT.response import StopedGenerating
from CLI import utils


class CliApplication:

    def __init__(self, debug=False) -> None:
        with open("config.toml") as file:
            config = toml.loads(file.read())

        self._bot = ChatBot(config)
        self.__debug = debug
        self.__answering = False

        listener = Listener(on_press=self.__on_press, on_release=self.__on_release, suppress=False)
        listener.start()

        print(utils.wellcome_str(self._bot.wellcome_message))
        print(utils.hr1())

    def __on_press(self, key) -> None:
        if key == Key.esc:
            self.__answering = False

    def __on_release(self, key) -> None:...

    def __respond(self, response):
        while self.__answering:
            try:
                resp = next(response)
                sys.stdout.write(resp)
                sys.stdout.flush()

            except StopIteration:
                print('\n')
                break

        else:
            raise StopedGenerating()


    def _ask(self) -> None:
        prompt = input(utils.input_format(self._bot.user_name))
        print(utils.bot_format(self._bot.name), end="")

        response = self._bot.ask(prompt).get()
        self.__answering = True
        self.__respond(response)


    def run(self) -> NoReturn:

        while True:
            try:
                self._ask()

            except StopedGenerating:
                print(utils.error_str("Stoped Generating response"))

            except KeyboardInterrupt:
                print("\n\n", utils.exit_str(self._bot.exit_message))
                print(utils.hr1(), end="\n\n")
                exit()

            except Exception as exp:
                if self.__debug:
                    raise
                print(utils.error_str(exp))
                print(utils.hr2())

            finally:
                print(utils.hr2(), end="\n\n")
