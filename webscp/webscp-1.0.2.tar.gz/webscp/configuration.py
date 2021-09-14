import configparser
from os.path import isfile

settings  = configparser.ConfigParser()
if isfile("config.ini"):
    settings.read("config.ini")

    sender    = settings["MAIL"]["EMAIL"]       
    password  = settings["MAIL"]["PASSWORD"]
    smtp      = settings.get("MAIL","SMTP", fallback='smtp.gmail.com')
    smtp_port = settings.get("MAIL","SMTP_PORT", fallback=587)
    keep_logs = settings.get("LOGS", "KEEP_LOG_FILE", fallback=False)
    path      = settings.get("LOGS", "PATH", fallback='src/logs/scraper.log')

else:
    sender = ""
    password = ""
    smtp = "smtp.gmail.com"
    smtp_port = 587
    keep_logs = False
    log_path  = "src/logs/scraper.log"