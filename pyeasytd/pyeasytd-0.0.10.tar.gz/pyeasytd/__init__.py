
class BasicCheckUtil:
    '''
    todo 基本数据类型检测工具类
    '''
    @classmethod
    def is_empty(cls, param):
        '''
        todo 判断对象是否为空，添加对基本数据类型的检测
        :param param: 参数
        :return:
        '''
        if cls.is_none(param):
            return True
        if type(param) in (int,float) and param == 0:
            return True
        if type(param) in (str,) and param == '':
            return True
        if type(param) in (tuple, list, dict) and len(param) == 0:
            return True
        if type(param) in (bool,) and param == False:
            return True
        return False

    @classmethod
    def non_empty(cls, param):
        '''
        todo 判断对象是否非空，添加对基本数据类型的检测
        :param param: 参数
        :return:
        '''
        return not cls.is_empty(param)

    @classmethod
    def is_none(cls, param):
        '''
        todo 判断对象是否为空
        :param param: 参数
        :return:
        '''
        if param is None:
            return True
        return False

    @classmethod
    def non_none(cls, param):
        '''
        todo 判断对象是否非空
        :param param: 参数
        :return:
        '''
        return not cls.is_none(param)

    @classmethod
    def equels(cls, a, b):
        if type(a) == type(b):
            if (type(a) in (int, float, str, bool)):
                if a == b:
                    return True
                return False
    @classmethod
    def contains(cls, a, b):
        '''
        a contains b ?
        :param a:
        :param b:
        :return:
        '''
        return b in a



def send_email_old(host: str, port: int, send_email: str, send_user: str, send_pass: str, receive:list,
           title: str, message: str, message_type='plain', encoding='utf-8', is_ssl=True, **kwargs):
    '''
    SMTP 发送邮件服务
    :param host: smtp服务器地址
    :param port: smtp服务器端口
    :param send_email: 发送人邮箱
    :param send_user: 发送人名称
    :param send_pass: 发送人邮箱的发送密码
    :param receive: 接收人邮箱列表
    :param title: 标题
    :param message: 正文
    :param message_type: 消息类型，plain, html
    :param encoding: 内容编码
    :param is_ssl: 是否为SSL连接的服务器
    :param kwargs: 扩展字段
    :return: {"status": "success"} 或 "status": "fail"}
    '''
    if BasicCheckUtil.equels(message_type, 'plain'):
        from smtplib import SMTP_SSL
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.header import Header
        if not is_ssl:
            smtp_obj =smtplib.SMTP(host, port)
        else:
            smtp_obj = SMTP_SSL(host, port)
        smtp_obj.login(send_email, send_pass)
        message_obj = MIMEText(message, message_type, encoding)
        mime_message_obj = MIMEMultipart('related')
        mime_message_obj.attach(message_obj)
        mime_message_obj['Subject'] = title
        mime_message_obj['From'] = Header(send_user, encoding)
        for receive_mail in receive:
            mime_message_obj['To'] = Header(receive_mail, encoding)
        smtp_obj.sendmail(send_email, receive, mime_message_obj.as_string())
        return {'status': 'success'}

def send_mail(host: str, port: int, send_email: str, send_pass: str, receive:list, title: str, message: str, is_ssl=True):
    import zmail
    obj = zmail.server(send_email, send_pass, host, port, is_ssl)
    send_message = {
        'subject': title,
        'content_text': message,
    }
    obj.send_mail(receive, send_message)