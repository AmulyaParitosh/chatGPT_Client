from abc import ABCMeta, abstractmethod
from typing import Literal

class StopedGenerating(Exception):...


class Memory:
	def __init__(self) -> None:
		self.__memory: list[tuple[str, str]] = []

	def retrieve_last_response(self) -> tuple[str, str] | Literal['']:
		return self.__memory[-1] if len(self.__memory) > 0 else ''

	def store_conversation(self, question, answer) -> None:
		self.__memory.append((question, answer))

	def clear_memory(self):
		self.__memory.clear()


class Response(metaclass=ABCMeta):
	def __init__(self, bot, prompt, response) -> None:
		self.response = response
		self.answer = None
		self._bot = bot
		self.prompt = prompt

	@abstractmethod
	def get(self) -> None:...

	@abstractmethod
	def final_response(self) -> str:...


class StreamedResponse(Response):
	def __init__(self, bot, prompt, response) -> None:
		super().__init__(bot, prompt, response)

	def get(self):
		collected_messages = []
		for chunk in self.response:
			chunk_message = chunk['choices'][0]['delta'].get("content", "")
			collected_messages.append(chunk_message)
			yield chunk_message

		self.answer = ''.join(collected_messages)
		self._bot._memory.store_conversation(self.prompt, self.answer)

	def final_response(self) -> str:
		response = self.get()
		while True:
			try:
				next(response)
			except StopIteration:
				break
		return self.answer


class NonStreamedResponse(Response):
	def __init__(self, bot, prompt, response) -> None:
		super().__init__(bot, prompt, response)

	def get(self):
		self.answer : str = self.response.choices[0].message.content
		self._bot._memory.store_conversation(self.prompt, self.answer)
		yield self.answer

	def final_response(self) -> str:
		response = self.get()
		while True:
			try:
				next(response)
			except StopIteration:
				break
		return self.answer
