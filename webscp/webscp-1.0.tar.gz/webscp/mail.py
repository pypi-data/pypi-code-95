import smtplib
from .logger.auto_logger import autolog
import configparser

def send_email(receiver,msg):

    '''
    SEND MAIL TO THE USER WITH ANONFILES LINK
    '''

    settings = configparser.ConfigParser()
    settings.read("config.ini")
    sender = settings["MAIL"]["EMAIL"]       
    password = settings["MAIL"]["PASSWORD"]  
 
    server = smtplib.SMTP(settings.get("MAIL","SMTP", fallback='smtp.gmail.com'), settings.get("MAIL","SMTP_PORT", fallback=587))
    server.starttls()
    autolog("Sending Mail...")
    message = f"""
    URL: {msg}
    """

    try:
        server.login(sender,password)
        server.sendmail(sender,receiver,message)
        autolog("Mail Sent Successfully")       
    except Exception as e:
        autolog(f"Sending Failed. {e}", 3)

