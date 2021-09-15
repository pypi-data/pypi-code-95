import re
import os
import time
import datetime

import sys
sys.path.insert(1,"/ssd2/zhanghonghai/codes/pyocs/pyocs")
sys.path.insert(2,"/ssd2/zhanghonghai/codes/pyocs/pyocs/pyocs")

from pyocs_software import PyocsSoftware
from pyocs import pyocs_demand
from pyocs import pyocs_software
from pyocs import pyocs_login

import poplib
import smtplib
import telnetlib
import email
import email.policy
from email.parser import Parser
from email.header import Header
from email.header import decode_header
from email.utils import parseaddr
from email.mime.text import MIMEText

from lxml import etree





confirm_task = pyocs_software.PyocsSoftware()
pop3_server = 'pop.cvte.com'
poplib._MAXLINE=20480

#发件人
sender = 'zhanghonghai@cvte.com'
#收件人
receivers = 'zhanghonghai@cvte.com'
#抄送人
Cc = 'zhanghonghai@cvte.com'+','+'zhanghonghai@cvte.com'

LogfileDailypath="/ssd2/zhanghonghai/codes/pyocs/pyocs/pyocs/NeedUploadOCSOrder.txt"

email_user = pyocs_login.PyocsLogin().get_account_from_json_file()['Username'] + "@cvte.com"
password   = pyocs_login.PyocsLogin().get_account_from_json_file()['Password']



'''
# 解析有必要的一些字符转换
'''
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


'''
# 从最新的100封邮件中检索客户邮件
'''
def get_customer_mail(customer_mail_info):
    # 连接到POP3服务器,有些邮箱服务器需要ssl加密，可以使用poplib.POP3_SSL
    try:
        telnetlib.Telnet('pop.cvte.com', 995)
        server = poplib.POP3_SSL(pop3_server, 995, timeout=10)
    except:
        time.sleep(5)
        server = poplib.POP3(pop3_server, 110, timeout=10)

    # 身份认证:
    server.user(email_user)
    server.pass_(password)
    # 返回邮件数量和占用空间
    # print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    new_email_num = len(mails)
    # print("当前邮件个数 ="+str(new_email_num))

    customer_mail_info_dict = {
    'mail_summary': '',
    'mail_sender' : ''
    }
    
    customer_mail_list = list()

    for index in range(new_email_num,new_email_num-50,-1):
        resp, lines, octets = server.retr(index)
        # lines存储了邮件的原始文本的每一行
        # 邮件的原始文本:
        msg_content = b'\r\n'.join(lines).decode('utf-8','ignore')
        msg = Parser().parsestr(msg_content)
        
        #邮件发送人
        mail_sender_pattern = re.compile('\w+[\.\w]*@\w+[\.\w]+')#匹配邮箱
        try:
            mail_sender_str = mail_sender_pattern.findall(msg.get('From',''))[0]
        except IndexError:
            continue

        if customer_mail_info in mail_sender_str:
            customer_mail_info_dict['mail_sender']  = mail_sender_str
            customer_mail_info_dict['mail_summary'] = decode_str(msg.get('Subject','')) 
            customer_mail_list.append(customer_mail_info_dict.copy())
    #关闭连接
    server.quit()
    return customer_mail_list

def send_email():

    if os.access(LogfileDailypath, os.F_OK):
        fp=open(LogfileDailypath,"r")
        htmljira_texts=fp.read()
        fp.close()
    else:
        return

    message = MIMEText(htmljira_texts, 'text')
    #发件人
    message['From'] = Header(sender)
    #收件人
    message['To'] =  Header(receivers)
    #抄送人
    message['Cc'] =  Header(Cc)
    #主题
    Subject = '《可上传软件OCS订单》'+time.strftime("%Y%m%d", time.localtime())
    message['Subject'] = Header(Subject, 'utf-8')


    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.cvte.com')
        smtpObj.login(sender, password) #邮箱账号
        smtpObj.sendmail(sender, receivers.split(',')+Cc.split(','), message.as_string())
        smtpObj.quit();
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

'''
# 删除当天的日志文件
'''
def DeleteDailylog():
    if os.access(LogfileDailypath, os.F_OK):
        os.remove(LogfileDailypath)
    else:
        pass


'''
获取OCS上 "待录入需求" 状态的订单
'''
def get_untreated_order():
    my_ocs_list = PyocsSoftware().get_my_ocs_order()
    ocs_untreated_list = list()
    order_info = {
            'ocs_id':'',
            'customer_order_id':''
    }
 
    for ocs_id in my_ocs_list:
        ocs_request = pyocs_demand.PyocsDemand(ocs_id)
        current_ocs_status_type = ocs_request.get_order_status_type()

        if '待录入需求' == current_ocs_status_type:
            current_ocs_summary = ocs_request.get_summary()
            customer_order_id_pattern = re.compile('\w+\/\w+')#匹配摘要中的启悦订单号
            customer_order_id_list = customer_order_id_pattern.findall(current_ocs_summary)
            order_info['ocs_id'] = ocs_id
            try:
                order_info['customer_order_id'] = customer_order_id_list[0]
            except IndexError:
                continue
            ocs_untreated_list.append(order_info.copy())
        else:
            break
    return ocs_untreated_list


if __name__ == "__main__":

    DeleteDailylog()
    customer_mail_list = get_customer_mail("@qiyue.cn")
    ocs_untreated_list = get_untreated_order()

    need_to_upload_sw_order_list = list()

    for ocs_order in ocs_untreated_list:
        for customer_mail in customer_mail_list:
            if ocs_order['customer_order_id'] in customer_mail['mail_summary']:
                need_to_upload_sw_order_list.append(ocs_order.copy())

    if len(need_to_upload_sw_order_list) > 0:
        fd = open(LogfileDailypath, 'a+',encoding='utf-8',errors='ignore')
        for i in need_to_upload_sw_order_list:
            msg_text = "订单号：" + i['customer_order_id'] + " http://ocs.gz.cvte.cn/tv/Tasks/view/range:my/" + str(i['ocs_id']) + " 客户已发需求"
            fd.write(msg_text)
        fd.close()

    send_email()
    




    