import sys
from abc import ABCMeta, abstractmethod
from typing import Any, NoReturn

import toml
from pynput.keyboard import Key, Listener

from chatGPT.bot import ChatBot, ChatWizard
from chatGPT.utils import Question, StopedGenerating
from CLI import utils


class CliApp(metaclass=ABCMeta):
    def __init__(self, debug : bool=False) -> None:
        self._debug: bool = debug
        self._answering = False

        listener = Listener(on_press=self.__on_press, on_release=self.__on_release, suppress=False)
        listener.start()

    def __on_press(self, key) -> None:
        if key == Key.esc:
            self._answering = False

    def __on_release(self, key) -> None:...

    @abstractmethod
    def run(self) -> NoReturn:...

    @abstractmethod
    def _chat(self) -> NoReturn:...


class CliBot(CliApp):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        with open("config.toml", 'r') as file:
            config: dict[str, Any] = toml.loads(file.read())

        self._bot = ChatBot(config)
        print(utils.wellcome_str(self._bot.wellcome_message))
        print(utils.hr1())


    def __respond(self, response) -> None:
        while self._answering:
            try:
                resp = next(response)
                sys.stdout.write(resp)
                sys.stdout.flush()

            except StopIteration:
                print('\n')
                break

        else:
            raise StopedGenerating()


    def _chat(self) -> None:
        prompt: str = input(utils.input_format(self._bot.user_name))
        print(utils.bot_format(self._bot.name), end="")

        response = self._bot.ask(prompt).get()
        self._answering = True
        self.__respond(response)


    def run(self) -> NoReturn:

        while True:
            try:
                self._chat()

            except StopedGenerating:
                print(utils.stoped_generation())

            except KeyboardInterrupt:
                print("\n\n", utils.exit_str(self._bot.exit_message))
                print(utils.hr1(), end="\n\n")
                exit()

            except Exception as exp:
                if self._debug:
                    raise
                print(utils.error_str(exp))
                print(utils.hr2())

            finally:
                print(utils.hr2(), end="\n\n")


class CliWizard(CliApp):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        with open("config.toml", 'r') as file:
            config: dict[str, Any] = toml.loads(file.read())

        self.wiz = ChatWizard(config)


    def _chat(self) -> NoReturn:...


    def __respond(self) -> None:
        print("hello")


    def run(self):
        res = self.wiz.wake()
        for r in res:
            print(r)

        while True:
            user_resp = input("input : ")
            res = self.wiz.converse(user_resp)
            for r in res:
                if r is None: continue
                if not isinstance(r, Question): continue
                print("Q:",r)
