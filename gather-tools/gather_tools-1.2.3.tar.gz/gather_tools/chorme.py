#coding=UTF-8
#模拟浏览器自动登录yahoo邮箱
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os
import platform
#一下三行为无头模式运行，无头模式不开启浏览器，也就是在程序里面运行的
# #如果不用上面三行，那么就用下面这一行。运行的时候回自动的开启浏览器，并在浏览器中自动运行，你可以看到自动运行的过程


class chorme():
       def init(self,chrome_options):
              if platform.system() == "Linux":
                     chrome_options.add_argument("--headless")
                     self.driver = webdriver.Chrome(executable_path=('/usr/bin/chromedriver'), options=chrome_options)
              else:              
                     self.driver = webdriver.Chrome(executable_path=(os.getcwd()+'/chromedriver.exe'), options=chrome_options)
       def mobile(self):
              mobile_emulation = {'deviceName': 'iPhone 6 Plus'}
              chrome_options = webdriver.ChromeOptions()
              chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
              chrome_options.add_argument('--no-sandbox')
              chrome_options.add_argument('--disable-gpu')
              chrome_options.add_argument('--disable-dev-shm-usage')
              self.init(chrome_options)
              return self.driver
       def pc(self):
              chrome_options = webdriver.ChromeOptions()
              chrome_options.add_argument('--no-sandbox')
              chrome_options.add_argument('--disable-gpu')
              chrome_options.add_argument('--disable-dev-shm-usage')
              self.init(chrome_options)
              return self.driver
       # 打开链接
       def get(self, url):
          try:
       #      self.driver.set_page_load_timeout(10)
       #      self.driver.set_script_timeout(10)
            self.driver.get(url)
          except:
            print("timeout")
       #      self.driver.execute_script("window.stop()")
       # 获取内容      
       def getsrouce(self):
             return self.driver.page_source
       # 截图
       def get_screenshot_as_file(self,filename):
              self.driver.get_screenshot_as_file(filename)
       # 获取COOKIE
       def get_cookies(self):
              return self.driver.get_cookies()
       # 退出
       def quit(self):
              self.driver.quit()  
       # 关闭            
       def close(self):
              self.driver.close()              
       # 鼠标悬停
       def hover(self,by,value):
              element = self.findElement(by,value)
              ActionChains(self.driver).move_to_element(element).perform()
       # 鼠标点击      
       def click(self,by,value):
              element = self.findElement(by,value)
              ActionChains(self.driver).click(element).perform()
       #输入内容
       def send_keys(self,by,value,keys):
              element = self.findElement(by,value)
              ActionChains(self.driver).send_keys(keys).perform()

       # 通过不同的方式查找界面元素
       def findElement(self,by,value):
              if(by == "id"):
                     element = self.driver.find_element_by_id(value)
                     return element
              elif(by == "name"):
                     element = self.driver.find_element_by_name(value)
                     return element
              elif(by == "xpath"):
                     element = self.driver.find_element_by_xpath(value)
                     return element
              elif(by == "classname"):
                     element = self.driver.find_element_by_class_name(value)
                     return element
              elif(by == "css"):
                     element = self.driver.find_element_by_css_selector(value)
                     return element
              elif(by == "link_text"):
                     element = self.driver.find_element_by_link_text(value)
                     return element
              else:
                     print("无对应方法，请检查")
                     return None


# XPATH方式详解
# 表达式	结果
# //*[count(xxx)=2]	统计xxx元素个数=2的节点
# //*[local-name()='xxx']	找到tag为xxx的元素
# //*[starts-with(local-name(),'x')]	找到所有tag以x开头的元素
# //*[contains(local-name(),'x')]	找到所有tag包含x的元素
# //*[string-length(local-name())=3]	找到所有tag长度为3的元素
# //xxx丨//yyy
# ————————————————
# 属性	实例
# id属性	find_element_by_xpath("//input[@id='kw']")
# class属性	element_by_xpath("//input[@class='s_ipt']")
# name属性	find_element_by_xpath("//input[@name='wd']")
# maxlength属性	find_element_by_xpath("//input[@maxlength='255']")
# ————————————————


# 模拟键盘输入和按键
# from selenium.webdriver.common.keys import Keys
# click(on_element=None)                 #鼠标左键单击
# click_and_hold(on_element=None)        #单击鼠标左键，不松开
# context_click(on_element=None)         #单击鼠标右键
# double_click(on_element=None)          #双击鼠标左键
# drag_and_drop(source,target)           #拖拽到某个元素然后松开
# drag_and_drop_by_offset(source,xoffset,yoffset) #拖拽到某个坐标然后松开
# key_down(value,element=None)     #按下键盘上的某个键
# key_up(value, element=None)      #松开键盘上的某个键
# move_by_offset(xoffset, yoffset)  #鼠标从当前位置移动到某个坐标
# move_to_element(to_element)        #鼠标移动到某个元素
# move_to_element_with_offset(to_element, xoffset, yoffset) #移动到距某个元素（左上角坐标）多少距离的位置
# pause(seconds)                  #暂停所有输入(指定持续时间以秒为单位)
# perform()                       #执行所有操作
# reset_actions()                 #结束已经存在的操作并重置
# release(on_element=None)       #在某个元素位置松开鼠标左键
# send_keys(*keys_to_send)        #发送某个键或者输入文本到当前焦点的元素
# send_keys_to_element(element, *keys_to_send) #发送某个键到指定元素

# 元素操作
# kw1.clear()        #清除元素的值
# kw1.click()        #点击元素
# kw1.id             #Selenium所使用的内部ID
# kw1.get_property('background') #获取元素的属性的值
# kw1.get_attribute('id') #获取元素的属性的值
# kw1.location       #不滚动获取元素的坐标
# kw1.location_once_scrolled_into_view  #不滚动且底部对齐并获取元素的坐标
# kw1.parent         #父元素
# kw1.send_keys('')  #向元素内输入值
# kw1.size           #大小
# kw1.submit         #提交
# kw1.screenshot('2.png') #截取元素形状并保存为图片
# kw1.tag_name       #标签名
# kw1.text           #内容，如果是表单元素则无法获取
# kw1.is_selected()  #判断元素是否被选中
# kw1.is_enabled()   #判断元素是否可编辑
# kw1.is_displayed   #判断元素是否显示
# kw1.value_of_css_property('color') #获取元素属性的值
# kw1._upload('2.png') #上传文件

# 浏览器参数
# o.add_argument('--window-size=600,600') #设置窗口大小
# o.add_argument('--incognito') #无痕模式
# o.add_argument('--disable-infobars') #去掉chrome正受到自动测试软件的控制的提示
# o.add_argument('user-agent="XXXX"') #添加请求头
# o.add_argument("--proxy-server=http://200.130.123.43:3456")#代理服务器访问
# o.add_experimental_option('excludeSwitches', ['enable-automation'])#开发者模式
# o.add_experimental_option("prefs",{"profile.managed_default_content_settings.images": 2})#禁止加载图片
# o.add_experimental_option('prefs',
# {'profile.default_content_setting_values':{'notifications':2}}) #禁用浏览器弹窗
# o.add_argument('blink-settings=imagesEnabled=false')  #禁止加载图片
# o.add_argument('lang=zh_CN.UTF-8') #设置默认编码为utf-8
# o.add_extension(create_proxyauth_extension(
#            proxy_host='host',
#            proxy_port='port',
#            proxy_username="username",
#            proxy_password="password"
#        ))# 设置有账号密码的代理
# o.add_argument('--disable-gpu')  # 这个属性可以规避谷歌的部分bug
# o.add_argument('--disable-javascript')  # 禁用javascript
# o.add_argument('--hide-scrollbars')  # 隐藏滚动条
# o.binary_location=r"C:\Users\Administrator\AppData\Local\Google\Chrome\Application" #指定浏览器位置
# o.add_argument('--no-sandbox')  #解决DevToolsActivePort文件不存在的报错

# https://blog.csdn.net/qq_44326412/article/details/107825851
