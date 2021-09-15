from colorama import Back, Fore, Style


class Log:
	DEBUG = 'DEBUG'
	INFO = 'INFO'
	WARN = 'WARN'
	ERROR = 'ERROR'

	levels_mapping = {
		DEBUG: 0,
		INFO: 1,
		WARN: 2,
		ERROR: 3,
	}

	min_level = levels_mapping[INFO]

	@staticmethod
	def check_level(level):
		return Log.levels_mapping[level] >= Log.min_level

	@staticmethod
	def set_log_level(level):
		Log.min_level = Log.levels_mapping[level]

	@staticmethod
	def debug(s):
		if Log.check_level(Log.DEBUG):
			print(Back.BLUE + Fore.WHITE + Style.BRIGHT + "[DEBUG]" +
			      Style.RESET_ALL + '\t' + Fore.BLUE + Style.BRIGHT + s +
			      Style.RESET_ALL)

	@staticmethod
	def info(s):
		if Log.check_level(Log.INFO):
			print(Back.BLACK + Fore.WHITE + "[INFO]" + Style.RESET_ALL + '\t' +
			      Fore.WHITE + Style.BRIGHT + s + Style.RESET_ALL)

	@staticmethod
	def warn(s):
		if Log.check_level(Log.WARN):
			print(Back.YELLOW + Fore.WHITE + Style.BRIGHT + "[WARNING]" +
			      Style.RESET_ALL + '\t' + Fore.YELLOW + Style.BRIGHT + s +
			      Style.RESET_ALL)

	@staticmethod
	def error(s):
		if Log.check_level(Log.ERROR):
			print(Back.RED + Fore.WHITE + Style.BRIGHT + "[ERROR]" + Style.RESET_ALL +
			      '\t' + Fore.RED + Style.BRIGHT + s + Style.RESET_ALL)


def debug(s):
	log(s, Log.DEBUG)


def info(s):
	log(s, Log.INFO)


def warn(s):
	log(s, Log.WARN)


def error(s):
	log(s, Log.ERROR)


def log(s, level=Log.INFO, do_style=True):
	if not do_style:
		print(s)
		return

	getattr(Log, level.lower())(s)
