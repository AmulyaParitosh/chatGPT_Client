import os
import sys
import termios
import tty

import toml
from sty import bg, ef, fg, rs


def h2r(value) -> tuple[int, int, int]:
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


with open("config.toml") as file:
	config = toml.loads(file.read())

config : dict = config.pop("cli")
symbols : dict = config.get("symbols")
colors : dict = config.get("colors")

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

def hr1() -> str:
	return f"{fg(*h2r(colors.get('hr1')))}{symbols.get('hr1') * os.get_terminal_size().columns}{fg.rs}"

def hr2() -> str:
	return f"{fg(*h2r(colors.get('hr2')))}{symbols.get('hr2') * os.get_terminal_size().columns}{fg.rs}"

def input_format(user_name) -> str:
	return f"\n{fg(*h2r(colors.get('user')))}{symbols.get('user')} {user_name}{fg.rs} : "

def bot_format( bot_name) -> str:
	return f"\n{fg(*h2r(colors.get('bot')))}{symbols.get('bot')} {bot_name}{fg.rs} : "


def getkey() -> str:
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3:
                k = ord(b[2])
            else:
                k = ord(b)
            key_mapping = {
                127: 'backspace',
                10: 'return',
                32: 'space',
                9: 'tab',
                27: 'esc',
                65: 'up',
                66: 'down',
                67: 'right',
                68: 'left'
            }
            return key_mapping.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

# TODO formating and pretty-printing rules

# TODO function to parse response
# TODO function to parse streamed response

# TODO function to pretty-print response
# TODO function to pretty-print stremed response
