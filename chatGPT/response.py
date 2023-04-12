from abc import ABCMeta, abstractmethod

class StopedGenerating(Exception):...

class Response(metaclass=ABCMeta):
	def __init__(self, bot, prompt, response) -> None:
		self.response = response
		self.answer = None
		self.bot = bot
		self.prompt = prompt

	@abstractmethod
	def get(self) -> None:...


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
		self.bot.store_conversation(self.prompt, self.answer)


class NonStreamedResponse(Response):
	def __init__(self, bot, prompt, response) -> None:
		super().__init__(bot, prompt, response)

	def get(self) -> None:
		self.answer : str = self.response.choices[0].message.content
		self.bot.store_conversation(self.prompt, self.answer)
		yield self.answer
