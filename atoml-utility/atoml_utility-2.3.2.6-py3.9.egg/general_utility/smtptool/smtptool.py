import smtplib
 
class SMTPHost(object):
    def __init__(self):
        pass

    def connect(self, host,  port = 25, username = None,  password = None):
        self.smtp_obj = smtplib.SMTP() 
        self.smtp_obj.connect(host = host, port = port) 
        self.smtp_obj.login(user = username, password = password) 

    def quit(self):
        self.smtp_obj.quit()

    def send(self,  from_addr = "admin@atoml.com", to_addrs = "caijun@atoml.com", msg = "test"):
        self.smtp_obj.sendmail(from_addr = from_addr, to_addrs = to_addrs, msg = msg) 
        self.quit()

def send2( host = "smtp.163.com", 
                                port = 25, 
                                username = None,  
                                password = None, 
                                subject = "from atoml's notice", 
                                body = "is none", 
                                from_addr = "admin@atoml.com", 
                                to_addrs =  ["caijun@atoml.com", "marmotcai@163.com"]):

    from email.mime.text import MIMEText
    from email.header import Header

    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = Header(from_addr, 'utf-8')   # 发送者

    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]
    
    if  len(to_addrs) > 0:
        message['To'] = ",".join(to_addrs)   # 发送者

    subject = subject
    message['Subject'] = Header(subject, 'utf-8')

    smtp_send = SMTPHost()
    smtp_send.connect(host, port, username, password)
    smtp_send.send(from_addr = from_addr, to_addrs = to_addrs,  msg = message.as_string())
    pass

def send(host = "smtp.163.com", 
                                port = 25, 
                                username = None,  
                                password = None, 
                                subject = "from atoml's notice", 
                                body = "is none", 
                                file_list = None,
                                from_addr = "admin@atoml.com", 
                                to_addrs =  ["caijun@atoml.com", "marmotcai@163.com"]):

    import os
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.header import Header

    messages = MIMEMultipart()
    message = MIMEText(body, 'plain', 'utf-8')
    messages.attach(message)

    if (file_list is not None):
        # 构造附件
        for f in file_list:
            if os.path.isfile(f):
                att = MIMEText(open(f, 'rb').read(), 'base64', 'utf-8')
                att["Content-Type"] = 'application/octet-stream'
                att["Content-Disposition"] = 'attachment;filename=' + os.path.basename(f)
                messages.attach(att)

    if isinstance(from_addr, str):
        from_addr = [from_addr]
    if  len(to_addrs) > 0:
            messages['From'] = ",".join(from_addr)   # 发送者

    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]
    if  len(to_addrs) > 0:
        messages['To'] = ",".join(to_addrs)   # 发送者

    subject = subject
    messages['Subject'] = Header(subject, 'utf-8')

    try:
        smtp_send = SMTPHost()
        smtp_send.connect(host, port, username, password)
        smtp_send.send(from_addr = from_addr, to_addrs = to_addrs,  msg = messages.as_string())
    except smtplib.SMTPException as e:
            return False, ("send mail error: %s" % e)

    return True, "send mail succeed."
