import os

import toml
from sty import bg, ef, fg, rs


def h2r(value) -> tuple[int, int, int]:
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


with open("config.toml") as file:
	config = toml.loads(file.read())

config : dict = config.pop("cli")
symbols : dict = config.get("symbols") # type: ignore
colors : dict = config.get("colors") # type: ignore

_text_format1 = f"\
{'{symbol}'} \
{ef.bold}\
{ef.underl}\
{'{color}'}\
{'{text}'}\
{fg.rs}\
{rs.underl}\
{rs.dim_bold} \
"

def wellcome_str(text) -> str:
	txt = _text_format1.format(
		text = text,
		symbol = symbols.get("welcome"),
		color = fg(*h2r(colors.get("welcome"))),
	)
	return txt

def exit_str(text) -> str:
	txt = _text_format1.format(
		text = text,
		symbol = symbols.get("exit"),
		color = fg(*h2r(colors.get("exit"))),
	)
	return txt

def error_str(exp) -> str:
	return f"\n\n{fg(*h2r(colors.get('error')))}{symbols.get('error')} there was as error!\n {exp}{ef.rs}"

def stoped_generation() -> str:
	return f"\n\n{fg(*h2r(colors.get('stop_generation')))}{symbols.get('stop_generation')} Response generation stopped!{ef.rs}"

def hr1() -> str:
	return f"{fg(*h2r(colors.get('hr1')))}{symbols.get('hr1','') * os.get_terminal_size().columns}{fg.rs}"

def hr2() -> str:
	return f"{fg(*h2r(colors.get('hr2')))}{symbols.get('hr2', '') * os.get_terminal_size().columns}{fg.rs}"

def input_format(user_name) -> str:
	return f"\n{fg(*h2r(colors.get('user')))}{symbols.get('user')} {user_name}{fg.rs} : "

def bot_format( bot_name) -> str:
	return f"\n{fg(*h2r(colors.get('bot')))}{symbols.get('bot')} {bot_name}{fg.rs} : "



# TODO formating and pretty-printing rules

# TODO function to parse response
# TODO function to parse streamed response

# TODO function to pretty-print response
# TODO function to pretty-print stremed response
