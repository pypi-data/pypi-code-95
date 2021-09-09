import smtplib
from email.mime.text import MIMEText


class Email(object):
    def __init__(self, user_email, password, email_to, region=None, host=None, port=None):
        self._from = user_email
        self.pass_word = password
        self._recipients = email_to
        self.region = region if region else "Default"
        self.host = host if host else "smtp.mxhichina.com"
        self.port = port if port else 465
        self._template = """
        <html>
            <head>
            <meta charset='utf-8'/>
            <style>
                #msg {{
                    height: 100%;
                    width: 100%;
                    white-space: nowrap;
                    overflow-x: auto;
                    font-family: "Courier New", Courier, monospace;
                    line-height:16px;
                    font-size:12px;
                    text-indent:0px;
                }}
            </style>
            </head>

            <body>
            <h2>[{region}] {title}</h2>
            <div id="msg">
                {message}
            </div>
            </body>
        </html>
        """
        super(Email, self).__init__()

    def send(self, title, message, cc=None):
        cc = [] if cc is None else cc
        server = smtplib.SMTP_SSL(host=self.host,
                                  port=self.port,
                                  timeout=20)
        server.login(self._from,
                     self.pass_word)
        content = self._template.format(
            region=self.region,
            title=title,
            message=message.replace("\n", "</br>").replace(" ", "&nbsp;"))
        mail = MIMEText(content, "html", _charset="utf-8")
        mail["Subject"] = "[{region}] {title}" \
            .format(region=self.region.upper(), title=title)
        mail["From"] = "<%s>" % self._from
        mail["To"] = "<%s>" % ">,<".join([self._recipients])
        mail["Cc"] = "<%s>" % ">,<".join(cc)
        ret = server.sendmail(self._from, [self._recipients] + cc, mail.as_string())
        server.close()
