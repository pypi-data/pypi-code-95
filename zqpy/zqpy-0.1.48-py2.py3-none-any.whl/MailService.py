import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

from ToolsService import ToolsServiceClass
tools = ToolsServiceClass()

class MailServiceClass(object):
    def __init__(self):
        self.mail_host='smtp.qq.com'  #设置服务器
        self.mail_user='1620829248@qq.com'    #用户名
        self.mail_pass='vsjgukkyzjjcfacd'#"lkkjyommgyuzfabh"#"askqrqhzcusfcddf"   #口令 
        self.sender = '1620829248@qq.com'
        self.receiversInit = ['877665041@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    def SendMail(self, userName, title, content, receiverMail):
        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = Header(userName, 'utf-8')
        msgRoot['To'] =  Header('用户', 'utf-8')
        subject = title #'Python SMTP 邮件测试'
        msgRoot['Subject'] = Header(subject, 'utf-8')
        
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        
        
        mail_msg = '''
        <p>Python 邮件发送测试...</p>
        <p><a href='http://vip.mayishidai.cn'>菜鸟教程链接</a></p>
        <p>图片演示：</p>
        <p><img src='cid:image1'></p>
        '''
        # msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
        msgAlternative.attach(MIMEText(content, 'html', 'utf-8'))
        
        '''
        fp = open('./image/test.jpg', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        
        # 定义图片 ID，在 HTML 文本中引用
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)
        '''

        receiversTemp = []
        receiversTemp.extend(self.receiversInit)
        receiversTemp.extend(receiverMail)
        reTitle = title
        if len(title + content) < 256 :
        	reTitle = title + content
        try:
            smtpObj = smtplib.SMTP() 
            smtpObj.connect(self.mail_host, 25)    # 25 为 SMTP 端口号
            smtpObj.login(self.mail_user,self.mail_pass)
            smtpObj.sendmail(self.sender, receiverMail, msgRoot.as_string())
            print ('邮件发送成功')
            tools.SendNotify('邮件：%s \n %s'%(reTitle, content))
            return {True, '邮件发送成功'}
        except smtplib.SMTPException as e:
            print ('Error: 无法发送邮件' + str(e))
            tools.SendNotify('邮件：%s \n %s \n %s'%(reTitle, content, str(e)))
            return {False, 'Error: 无法发送邮件'}

if __name__ == '__main__':
    MailService = MailServiceClass()
    content = '''
        <p>Python 邮件发送测试...</p>
        <p><a href='http://vip.mayishidai.cn'>菜鸟教程链接</a></p>
        <p>图片演示：</p>
        <p><img src='cid:image1'></p>
        '''
    MailService.SendMail('用户','嘿嘿嘿',content,'877665041@qq.com')
    MailServiceClass().SendMail('用户','嘿嘿嘿',content,'877665041@qq.com')
