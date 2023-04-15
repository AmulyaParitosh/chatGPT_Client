from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generator, Literal
from datetime import datetime

class StopedGenerating(Exception):...


class Memory:
	def __init__(self) -> None:
		self.__memory: list[tuple[str, str]] = []
		self.file = open('memory', '+w')

	def __del__(self):
		self.file.close()

	def retrieve_last_response(self) -> tuple[str, str] | Literal['']:
		return self.__memory[-1] if len(self.__memory) > 0 else ''

	def store_conversation(self, question, answer) -> None:
		self.__memory.append((question, answer))
		self.file.write('\n\n\n')
		self.file.write(str(datetime.now()))
		self.file.write('\n')
		self.file.write(f"RESPONSE : {answer}")
		self.file.flush()

	def clear_memory(self):
		self.__memory.clear()


class Response(metaclass=ABCMeta):
	def __init__(self, bot, prompt, response) -> None:
		self.response = response
		self.answer = None
		self._bot = bot
		self.prompt = prompt

	@abstractmethod
	def get(self) -> Generator[str, None, None]:...

	@abstractmethod
	def final_response(self) -> str:...


class StreamedResponse(Response):
	def __init__(self, bot, prompt, response) -> None:
		super().__init__(bot, prompt, response)

	def get(self) -> Generator[str, None, None]:
		self.__collected_chunks: list[str] = []
		for chunk in self.response:
			chunk_message: str = chunk['choices'][0]['delta'].get("content", "")
			self.__collected_chunks.append(chunk_message)
			if chunk_message == None: continue
			yield chunk_message

		self.answer = ''.join(self.__collected_chunks)
		self._bot._memory.store_conversation(self.prompt, self.answer)

	def final_response(self) -> str:
		response: Generator[str, None, None] = self.get()
		while True:
			try:
				next(response)
			except StopIteration:
				break
		return self.answer


class NonStreamedResponse(Response):
	def __init__(self, bot, prompt, response) -> None:
		super().__init__(bot, prompt, response)

	def get(self) -> Generator[str, None, None]:
		self.answer : str = self.response.choices[0].message.content
		self._bot._memory.store_conversation(self.prompt, self.answer)
		yield self.answer

	def final_response(self) -> str:
		response: Generator[str, None, None] = self.get()
		while True:
			try:
				next(response)
			except StopIteration:
				break
		return self.answer

@dataclass
class Prompt:
	value: str

	def __str__(self) -> str:
		return self.value

@dataclass
class Question:
	value: str

	def __str__(self) -> str:
		return self.value

@dataclass
class Suggestion:
	value: str

	def __str__(self) -> str:
		return self.value


class ResponseParser:

	__prompt_pattern = ("Revised Prompt:", "Revised prompt:", "Revised Prompt :", "Revised prompt :")
	__sugg_pattern = ("Suggestion", "suggestion", "Suggestions", "suggestions", "Suggestion:", "suggestion:", "Suggestions :", "suggestions :", "Suggestions:", "suggestions:")
	__ques_pattern = ("Question", "question", "Questions", "questions", "Question:", "question:", "Questions :", "questions :", "Questions:", "questions:")

	def __init__(self, response : Generator[str, None, None]) -> None:
		self.response: Generator[str, None, None] = response
		self.__collected_chunks: list[str] = []

		self.prompt: Prompt = None # type: ignore
		self.suggestions: list[Suggestion] = []
		self.questions: list[Question] = []

		self.__is_prompt = False
		self.__is_sugg = False
		self.__is_que = False


	def __recog_type(self):
		collection: str = ''.join(self.__collected_chunks)
		if any((pat in collection) for pat in self.__prompt_pattern):
			self.__collected_chunks.clear()
			self.__is_prompt = True
			self.__is_sugg = False
			self.__is_que = False

		elif any((pat in collection) for pat in self.__sugg_pattern):
			self.__collected_chunks.clear()
			self.__is_prompt = False
			self.__is_sugg = True
			self.__is_que = False

		elif any((pat in collection) for pat in self.__ques_pattern):
			self.__collected_chunks.clear()
			self.__is_prompt = False
			self.__is_sugg = False
			self.__is_que = True


	def __parsing_logic(self, collection : str):
		if not collection : return

		if self.__is_prompt:
			self.prompt = Prompt(collection)
			return self.prompt

		elif self.__is_sugg:
			self.suggestions.append(Suggestion(collection))
			return self.suggestions[-1]

		elif self.__is_que:
			self.questions.append(Question(collection))
			return self.questions[-1]


	def __parse(self, chunk : str):
		if not chunk: return

		self.__collected_chunks.append(chunk)
		self.__recog_type()

		if '\n' not in chunk: return

		collection: str = ''.join(self.__collected_chunks).strip()
		self.__collected_chunks.clear()
		return self.__parsing_logic(collection)


	def parse(self):
		while True:
			try:
				yield self.__parse(chunk = next(self.response))
			except StopIteration:
				yield self.__parsing_logic(''.join(self.__collected_chunks).strip())
				break
