import os
from typing import Generator, Optional, Union

import openai

from chatGPT.utils import (Memory, NonStreamedResponse, Response,
                           StreamedResponse, Prompt, Question, Suggestion)


class Bot:
	def __init__(self, config : dict[str, Union[dict, str]], engine: Optional[str] = None, **kwargs) -> None:
		self._openai_api_key = config.get("openai").get("api_key", os.getenv("OPENAI_API_KEY")) # type: ignore
		self._openai_api_key = os.getenv("OPENAI_API_KEY") if self._openai_api_key == "default" else self._openai_api_key
		openai.api_key = self._openai_api_key

		self.chatGPT = openai.ChatCompletion(engine, **kwargs)
		self._memory = Memory()


class DaemonBot(Bot):
	def __init__(self, config : dict[str, Union[dict, str]], engine: Optional[str] = None, **kwargs) -> None:
		super().__init__(config, engine, **kwargs)

		self.__base_prompt = "Answer in only one word, either True or False"
		self.__closing_prompt_format = f"{'{prompt}'}. Am I asking you to close or go away? {self.__base_prompt}"
		self.__generate_prompt_format = f"{'{prompt}'}. Am I asking you to finilise or I am happy or done? {self.__base_prompt}"


	def __process_response(self, response : str) -> bool:
		if "true" in response.lower() : return True
		return False


	def to_close(self, prompt : str) -> bool:
		prompt = self.__closing_prompt_format.format(prompt)
		return self.__ask(prompt)


	def to_gene_ans(self, prompt : str) -> bool:
		prompt = self.__generate_prompt_format.format(prompt)
		return self.__ask(prompt)


	def __ask(self, prompt) -> bool:

		response = self.chatGPT.create(
			name = "Servant",
			stream = False,
			max_tokens = 1024,
			model = "gpt-3.5-turbo",
			temperature = 0.7,
			top_p = 1,
			n = 1,
			stop = "None",
			messages = [{
				"role" : "user",
				"content" : prompt,
     		}]
		)

		return self.__process_response(response.choices[0].message.content) # type: ignore


class ChatBot(Bot):
	def __init__(self, config : dict[str, Union[dict, str]], engine: Optional[str] = None, **kwargs) -> None:
		super().__init__(config, engine, **kwargs)

		self._init_user(config.get("user")) # type: ignore
		self._init_bot(config.get("bot")) # type: ignore


	def _init_bot(self, config : dict[str, Union[dict, str]]) -> None:
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

		messages: dict = config.get("messages") # type: ignore

		self.wellcome_message = messages.get("welcome", "Bot Initialised")
		self.exit_message = messages.get("exit", "Bye Bye!")


	def _init_user(self, config : dict[str, Union[dict, str]]) -> None:
		self.user_name = config.get("name", os.getenv("USER"))
		self.user_name = os.getenv("USER") if self.user_name == "default" else self.user_name


	def ask(self, prompt) -> Response:
		last_response = self._memory.retrieve_last_response()
		if last_response:
			prompt = f"{last_response} {prompt}"

		response = self.chatGPT.create(
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
     		}],
		)

		return self.responde(prompt, response)

	def responde(self, prompt, response):
		if isinstance(response, openai.openai_object.OpenAIObject): # type: ignore
			return NonStreamedResponse(self, prompt, response)
		else:
			return StreamedResponse(self, prompt, response)



# TODO make GptWizard class

class ChatWizard:

	__uses_info_msg: str = "I am a Chatter Wizard. I create the best possible responses for you. Just keep answering my questions to get my maggical response."
	__wizard_prompt: str = "I want you to become my Prompt Creator. Your goal is to help me craft the best possible prompt for my needs. The prompt will be used by you, ChatGPT. You will follow the following process: 1. Your first response will be to ask me what the prompt should be about. I will provide my answer, but we will need to improve it through continual iterations by going through the next steps. 2. Based on my input, you will generate 3 sections. a) Revised prompt (provide your rewritten prompt. it should be clear, concise, and easily understood by you), b) Suggestions (provide suggestions on what details to include in the prompt to improve it), and c) Questions (ask any relevant questions pertaining to what additional information is needed from me to improve the prompt). 3. We will continue this iterative process with me providing additional information to you and you updating the prompt in the Revised prompt section until it's complete."
	__wizard_greeting: str = "Greetings, my adventurous seeker of knowledge! As a wise wizard, I am here to guide you towards finding the answers to your questions. What topic intrigues you? Shall we explore ancient civilizations, the wonders of nature, or delve into the realm of magic and fantasy? Simply ask your question, and together we shall embark on a journey of learning and exploration. May the magic of knowledge guide us on our way!"

	def __init__(self, config, engine: Optional[str] = None, **kwargs) -> None:
		self.__bot = ChatBot(config, engine, **kwargs)
		self.__dbot = DaemonBot(config, engine, **kwargs)
		self.latest_prompt: Prompt | None = None
		self.latest_suggestions: list[Suggestion] = []
		self.latest_questions: list[Question] = []


	def __usages_info(self) -> Generator:
		yield self.__uses_info_msg


	def __finilize(self):
		self.__bot._memory.clear_memory()
		return self.__bot.ask(self.latest_prompt)

	def __prepare_prompt(self, chunk):
		sen = " ".join(chunk).replace('"', '')
		return Prompt(sen)

	def __prepare_sugg(self, chunk):
		sen = " ".join(chunk).strip()
		chunk.clear()
		if sen == '' : return
		sen = Suggestion(sen)
		self.latest_suggestions.append(sen)
		return sen

	def __prepare_que(self, chunk):
		sen = " ".join(chunk).strip()
		chunk.clear()
		if sen == '' : return
		sen = Question(sen)
		self.latest_questions.append(sen)
		return sen

	def __parse_prompt(self, response, chunk):
		while True:

			word = next(response)

			if word == "Suggestions:":
				self.latest_prompt = self.__prepare_prompt(chunk)
				chunk.clear()
				break

			else:
				chunk.append(word)

		return self.latest_prompt

	def __parse_sugg(self, response, chunk):
		while True:
			word = next(response)

			if word == "-":
				yield self.__prepare_sugg(chunk)

			elif word == "Questions:":
				yield self.__prepare_sugg(chunk)
				break

			else:
				chunk.append(word)

	def __parse_que(self, response, chunk):
		while True:
			try:
				word = next(response)
			except StopIteration:
				yield self.__prepare_que(chunk)
				break

			if word == "-":
				yield self.__prepare_que(chunk)

			else:
				chunk.append(word)


	def __parse_response(self, response : Generator):
		chunk: list[str] = []

		next(response)
		next(response)

		yield self.__parse_prompt(response, chunk)
		yield self.__parse_sugg(response, chunk)
		yield self.__parse_que(response, chunk)


	def wake(self) -> Generator:
		yield self.__usages_info()
		self.__bot.ask(self.__wizard_prompt)
		yield self.__wizard_greeting


	def converse(self, user_response) -> Generator:
		response = self.__bot.ask(user_response).get()

		if self.__dbot.to_gene_ans(user_response):
			return self.__finilize()

		for item in self.__parse_response(response):
			if isinstance(item, Question):
				yield item.value
