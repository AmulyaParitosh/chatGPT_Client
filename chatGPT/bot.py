import os
import sys
from typing import Literal, Optional

import openai


class ChatBot(openai.ChatCompletion):
	def __init__(self, config, engine: Optional[str] = None, **kwargs) -> None:
		self._openai_api_key = config.get("openai").get("api_key", os.getenv("OPENAI_API_KEY"))
		self._openai_api_key = os.getenv("OPENAI_API_KEY") if self._openai_api_key == "default" else self._openai_api_key
		openai.api_key = self._openai_api_key

		openai.ChatCompletion.__init__(self, engine, **kwargs)

		self._init_user(config.get("user"))
		self._init_bot(config.get("bot"))

		self.memory : list[tuple[str, str]] = []


	def _init_bot(self, config : Optional[dict]) -> None:
		self.name = config.get("name", "chatGPT")
		self.name = "chatGPT" if self.name == "default" else self.name
		self.stream = bool(config.get("stream", False))
		self.max_tokens = config.get("max_tokens", 500)
		self.model = config.get("model", "gpt-3.5-turbo")
		self.temperature = config.get("temperature", 0.7)
		self.top_p = config.get("top_p", 1)
		self.n = config.get("n", 1)
		self.stop = config.get("stop", None)
		self.stop = None if self.stop == "None" else self.stop

		messages = config.get("messages")

		self.wellcome_message = messages.get("welcome", "Bot Initialised")
		self.exit_message = messages.get("exit", "Bye Bye!")


	def _init_user(self, config : Optional[dict]) -> None:
		self.user_name = config.get("name", os.getenv("USER"))
		self.user_name = os.getenv("USER") if self.user_name == "default" else self.user_name


	def retrieve_last_response(self) -> tuple[str, str] | Literal['']:
		return self.memory[-1] if len(self.memory) > 0 else ''


	def store_conversation(self, question, answer) -> None:
		self.memory.append((question, answer))


	def ask(self, prompt) -> str:
		last_response = self.retrieve_last_response()
		if last_response:
			prompt = f"{last_response} {prompt}"

		response = self.create(
			model = self.model,
			max_tokens = self.max_tokens,
			temperature = self.temperature,
			top_p = self.top_p,
			n = self.n,
			stream = self.stream,
			stop = self.stop,
			messages = [{
				"role" : "user",
				"content" : prompt,
     		}]
		)

		# TODO Figure out a way to return the stream response rather than directly printing it
		print(response)

		if self.stream:
			return StreamResponse(response)

		else:
			answer : str = response.choices[0].message.content

		self.store_conversation(prompt, answer)

		return answer


class StreamResponse:
	def __init__(self, response) -> None:
		self.response = response
		self.answer = None

	def get_stream(self):
		collected_messages = []
		for chunk in self.response:
			chunk_message = chunk['choices'][0]['delta'].get("content", "")
			collected_messages.append(chunk_message)
			yield chunk_message


class Response:
	def __init__(self, response) -> None:
		self.response = response
		self.answer = None

# TODO make GptWizard class
