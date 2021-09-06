from logging import getLogger, StreamHandler
from sys import stdout
from traceback import format_list, extract_tb
from smtplib import SMTP

def initLogger(logLevelStr="CRITICAL"):
    '''returns a logging object set to a loglevel'''
    logLevelMap= {
        "CRITICAL":50,
        "ERROR":50,
        "WARNING":50,
        "INFO":50,
        "DEBUG":50,
        "NOTSET":50,
    }
    log = getLogger(__name__)
    outputHandler = StreamHandler(stdout)
    logLevelValue = logLevelMap[logLevelStr]
    outputHandler.setLevel(logLevelValue)
    log.addHandler(outputHandler)
    log.setLevel(logLevelValue)
    return log
def exceptionStringify(exe):
    '''Returns a string of a pythin error and traceback'''
    traceback_str = "".join(format_list(extract_tb(exe.__traceback__)))
    exception_str= str(exe)
    return f"""
        Exception:\n\n{exception_str}
        Traceback:\n\n{traceback_str}
    """
def sendEmail(smtp_server, smtp_port, mail_content_body, sender_mail, mail_to_array, mail_to_cc_array=[]):
    with SMTP(smtp_server, smtp_port) as smtp:
        smtp.ehlo()
        smtp.sendmail(sender_mail, mail_to_array + mail_to_cc_array, mail_content_body)