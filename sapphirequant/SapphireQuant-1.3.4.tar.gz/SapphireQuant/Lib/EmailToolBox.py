import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailToolBox:
    """
    邮件工具箱
    """

    def __init__(self):
        pass

    @staticmethod
    def send_email(subject, msg, from_address, to_address_list, smtp_host, password, attach_path_list=None):
        """
        发送邮件
        :param subject: 邮件主题
        :param msg: 邮件内容
        :param from_address: 收信人的邮箱地址，例如：["382892414@qq.com", 'maxtrics@aliyun.com']
        :param to_address_list: 发信人的邮箱地址
        :param smtp_host: smtp服务地址，可以在邮箱看，比如163邮箱为smtp.163.com
        :param password: 发信人的邮箱密码
        :param attach_path_list: 附件地址
        """
        mail_msg = MIMEMultipart()
        mail_msg['Subject'] = subject
        mail_msg['From'] = from_address
        mail_msg['To'] = ','.join(to_address_list)
        mail_msg.attach(MIMEText(msg, 'html', 'utf-8'))

        if attach_path_list is not None:
            for attach_path in attach_path_list:
                app = MIMEApplication(open(attach_path, 'rb').read(), attach_path.split('.')[-1])
                app.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attach_path))
                mail_msg.attach(app)
        try:
            server = smtplib.SMTP_SSL(smtp_host)
            server.connect(smtp_host, 465)  # 连接smtp服务器
            server.login(from_address, password)  # 登录邮箱
            server.sendmail(from_address, to_address_list, mail_msg.as_string())  # 发送邮件
            server.quit()
        except Exception as e:
            print(str(e))
            print("Error: unable to send email")


