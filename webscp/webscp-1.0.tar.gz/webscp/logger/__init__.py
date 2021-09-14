from os.path import isfile
from os import system
import logging

if not isfile("src/logs/scrapper.log"):
    system("touch src/logs/scraper.log")


format_var = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(filename="src/logs/scraper.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

console_log = logging.StreamHandler()
console_log.setLevel(logging.DEBUG)
console_log.setFormatter(format_var)
logging.getLogger("").addHandler(console_log)
