"""
@author  : MG
@Time    : 2021/1/26 16:25
@File    : get_email.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import datetime
import email
import logging
import poplib
import telnetlib
import time
from datetime import datetime, timedelta, date
from email.header import decode_header
from email.parser import Parser
from email.utils import parseaddr
from io import StringIO, BytesIO
from typing import TextIO, Dict

logger = logging.getLogger(__name__)


class DownEmail:

    def __init__(self, user, password, email_server='pop.163.com'):
        # 输入邮件地址, 口令和POP3服务器地址:
        self.user = user
        # 此处密码是授权码,用于登录第三方邮件客户端
        self.password = password
        self.pop3_server = email_server

    # 获得msg的编码
    @staticmethod
    def guess_charset(msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    # 获取邮件内容
    @staticmethod
    def get_content(msg):
        content = ''
        content_type = msg.get_content_type()
        # print('content_type:',content_type)
        if content_type == 'text/plain':  # or content_type == 'text/html'
            content = msg.get_payload(decode=True)
            charset = DownEmail.guess_charset(msg)
            if charset:
                content = content.decode(charset)
        return content

    # 字符编码转换
    @staticmethod
    def decode_str(str_in):
        value, charset = decode_header(str_in)[0]
        if charset:
            value = value.decode(charset)
        return value

    # 解析邮件,获取附件
    def get_attachment_dic(self, msg_in) -> BytesIO:
        for part in msg_in.walk():
            # 获取附件名称类型
            # file_name = part.get_param("name")  # 如果是附件，这里就会取出附件的文件名
            file_name = part.get_filename()  # 获取file_name的第2中方法
            # contType = part.get_content_type()
            if file_name:
                h = email.header.Header(file_name)
                # 对附件名称进行解码
                dh = email.header.decode_header(h)
                filename = dh[0][0]
                if dh[0][1]:
                    # 将附件名称可读化
                    filename = self.decode_str(str(filename, dh[0][1]))
                    # print(filename)
                    # filename = filename.encode("utf-8")
                # 下载附件
                data = part.get_payload(decode=True)
                # 在指定目录下创建文件，注意二进制文件需要用wb模式打开
                # att_file = open('./' + filename, 'wb')
                # att_file.write(data)  # 保存附件
                # att_file.close()
            else:
                pass
                # 不是附件，是文本内容
                # print(DownEmail.get_content(part))
                # # 如果ture的话内容是没用的
                # if not part.is_multipart():
                #     # 解码出文本内容，直接输出来就可以了。
                #     print(part.get_payload(decode=True).decode('utf-8'))

        return BytesIO(data)

    def run_ing(self, email_title, recent_n_days=2) -> Dict[int, BytesIO]:
        # date_n_days_ago = date.today() - timedelta(days=recent_n_days)  # 日期赋值
        # 连接到POP3服务器,有些邮箱服务器需要ssl加密，可以使用poplib.POP3_SSL
        try:
            telnetlib.Telnet(self.pop3_server, 995)
            server = poplib.POP3_SSL(self.pop3_server, 995, timeout=10)
        except:
            time.sleep(5)
            server = poplib.POP3(self.pop3_server, 110, timeout=10)

        try:
            # server.set_debuglevel(1) # 可以打开或关闭调试信息
            # 打印POP3服务器的欢迎文字:
            # print(server.getwelcome().decode('utf-8'))
            # 身份认证:
            server.user(self.user)
            server.pass_(self.password)
            # 返回邮件数量和占用空间:
            # print('Messages: %s. Size: %s' % server.stat())
            # list()返回所有邮件的编号:
            resp, mails, octets = server.list()
            # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
            # print(mails)
            index = len(mails)
            attachment_dic = {}
            if index > 100:
                end = index - 100
            else:
                end = 0
            for i in range(index, end, -1):  # 倒序遍历邮件
                # for i in range(1, index + 1):# 顺序遍历邮件
                resp, lines, octets = server.retr(i)
                # lines存储了邮件的原始文本的每一行,
                # 邮件的原始文本:
                try:
                    msg_content = b'\r\n'.join(lines).decode('utf-8')
                except UnicodeDecodeError:
                    msg_content = b'\r\n'.join(lines).decode('ISO-8859-1')

                # 解析邮件:
                msg = Parser().parsestr(msg_content)
                # 获取邮件的发件人，收件人， 抄送人,主题
                # hdr, addr = parseaddr(msg.get('from_str'))
                # from_str = self.decode_str(hdr)
                # hdr, addr = parseaddr(msg.get('to_str'))
                # to_str = self.decode_str(hdr)
                # 方法2：from or Form均可
                from_str = parseaddr(msg.get('from'))[1]
                to_str = parseaddr(msg.get('to'))[1]
                subject = DownEmail.decode_str(msg.get('subject'))
                n = 0
                if email_title in subject:
                    print('from:%s,to:%s,subject:%s' % (from_str, to_str, subject))
                    # 获取邮件时间,格式化收件时间
                    # date_email = datetime.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S').date()
                    # # 邮件时间格式转换
                    # date2 = time.strftime("%Y-%m-%d", date_email)
                    n = int(subject.split('[')[1][0])
                    attachment_dic[n] = self.get_attachment_dic(msg)
                    if n == 1:
                        break
            # 可以根据邮件索引号直接从服务器删除邮件:
            # self.server.dela(7)
        finally:
            server.quit()

        return attachment_dic


def download_email_attachment(email_title, password, recent_n_days=3) -> Dict[str, TextIO]:
    try:
        # 输入邮件地址, 口令和POP3服务器地址:
        user = '265590706@qq.com'
        email_server = 'pop.qq.com'
        email_class = DownEmail(user=user, password=password, email_server=email_server)
        attachment_dic = email_class.run_ing(email_title=email_title, recent_n_days=recent_n_days)
    except:
        logger.exception("下载邮件异常")
        attachment_dic = {}

    return attachment_dic


if __name__ == '__main__':
    download_email_attachment(email_title='exports strategy and backtest data 2021-02-23', password='***')
