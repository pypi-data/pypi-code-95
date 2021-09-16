import json
import shutil
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from colorama import Back, Fore, Style, init


def get_output_server_file_path():
	return __file__


color_idx = 0
colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
id_to_color = dict()


def _inc_color():
	global color_idx
	color_idx = (color_idx + 1) % len(colors)


def _call_num_exists(call_num):
	global id_to_color
	return call_num in id_to_color.keys()


def _get_color(call_num):
	global color_idx
	global colors
	global id_to_color

	if not _call_num_exists(call_num):
		# enter
		color = colors[color_idx]
		id_to_color[call_num] = color
		_inc_color()
	else:
		# leave
		color = id_to_color[call_num]
		del id_to_color[call_num]

	return color


def get_terminal_width():
	width, _ = shutil.get_terminal_size(fallback=(80, 24))

	# The Windows get_terminal_size may be bogus, let's sanify a bit.
	if width < 40:
		width = 80

	return width


def print_title(title, color):
	print(color + entire_row_str(title))


def print_data(data):
	print(json.dumps(data, indent=4, sort_keys=True))


def entire_row_str(title=None, sepchar='='):
	fullwidth = get_terminal_width()

	# The goal is to have the line be as long as possible
	# under the condition that len(line) <= fullwidth.
	if sys.platform == "win32":
		# If we print in the last column on windows we are on a
		# new line but there is no way to verify/neutralize this
		# (we may not know the exact line width).
		# So let's be defensive to avoid empty lines in the output.
		fullwidth -= 1
	if title is not None:
		# we want 2 + 2*len(fill) + len(title) <= fullwidth
		# i.e.    2 + 2*len(sepchar)*N + len(title) <= fullwidth
		#         2*len(sepchar)*N <= fullwidth - len(title) - 2
		#         N <= (fullwidth - len(title) - 2) // (2*len(sepchar))
		N = max((fullwidth - len(title) - 2) // (2 * len(sepchar)), 1)
		fill = sepchar * N
		line = f"{fill} {title} {fill}"
	else:
		# we want len(sepchar)*N <= fullwidth
		# i.e.    N <= fullwidth // len(sepchar)
		line = sepchar * (fullwidth // len(sepchar))
	# In some situations there is room for an extra sepchar at the right,
	# in particular if we consider that with a sepchar like "_ " the
	# trailing space is not important at the end of the line.
	if len(line) + len(sepchar.rstrip()) <= fullwidth:
		line += sepchar.rstrip()

	return line


def print_hook_details(data):
	call_num = data['callNum']
	method_name = data['methodName']
	class_name = data['className']
	param_types = data['paramTypes']
	params = data['params']

	if not _call_num_exists(call_num):
		enter = True
		data_to_print = {
			'Param Types': param_types,
			'Params': params
		}
	else:
		enter = False
		data_to_print = {
			'Return Value': data['retval']
		}

	color = _get_color(call_num)

	title = ('[ENTER]' if enter else '[LEAVE]') + ' ' + class_name + "::" + method_name

	print_title(title, color)
	print_data(data_to_print)


def pprint(msg):
	if type(msg) == dict:
		msg_type = msg['type']

		if msg_type == 'hook-enter' or msg_type == 'hook-leave':
			data = msg['data']
			print_hook_details(data)

		elif msg_type == "error":
			data = msg['data']
			print(
				Back.RED + Fore.WHITE + Style.BRIGHT + "[ERROR]" + Style.RESET_ALL + '\t' + Fore.RED + Style.BRIGHT + data)
	else:
		print(msg)

	print()


class OutputWindowServer(BaseHTTPRequestHandler):

	def log_message(self, format, *args):
		return

	def do_POST(self):
		self.send_response(200)
		self.end_headers()
		length = int(self.headers['Content-length'])
		content = self.rfile.read(length)
		msg = json.loads(content)['msg']

		if msg == FRIDA_SERVER_KILL_COMMAND:
			exit()

		pprint(msg)


if __name__ == "__main__":
	from consts import FRIDA_SERVER_KILL_COMMAND

	init(autoreset=True)

	if len(sys.argv) != 4:
		exit(-1)

	_, device_id, app_name, port = sys.argv


	def aux_print(name, value):
		pad = 15
		print(Fore.GREEN + Style.BRIGHT + name.ljust(pad) + Style.RESET_ALL + str(value))


	aux_print("Device", device_id)
	aux_print("Package", app_name)
	print()

	server_address = ('', int(port))
	httpd = HTTPServer(server_address, OutputWindowServer)
	httpd.allow_reuse_address = True
	httpd.serve_forever()
