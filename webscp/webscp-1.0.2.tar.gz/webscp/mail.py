import smtplib
from .logger.auto_logger import autolog
from .configuration import *
def send_email(receiver,msg):

    '''
    SEND MAIL TO THE USER WITH ANONFILES LINK
    '''  
    server = smtplib.SMTP(smtp, smtp_port)
    server.starttls()
    autolog("Sending Mail...")
    message = f"""
    URL: {msg}
    """

    try:
        if sender is None or password is None:
            autolog("mail.sender or mail.password is missing", 3)
            exit(2)

        server.login(sender,password)
        server.sendmail(sender,receiver,message)
        autolog("Mail Sent Successfully")       
    except Exception as e:
        autolog(f"Sending Failed. {e}", 3)

