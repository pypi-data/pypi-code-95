# 基类——对象库层
from selenium.webdriver.support.wait import WebDriverWait


class BasePage:
    def __init__(self):
        pass

    # 单个元素定位
    def base_find_elt(self,driver, location, timeout=30, poll=0.5):
        return WebDriverWait(driver, timeout, poll).until(lambda el: el.find_element(*location))

    # 多个元素定位
    def base_find_elts(self,driver, location, timeout=30, poll=0.5):
        return WebDriverWait(driver, timeout, poll).until(lambda el: el.find_elements(*location))

    # 查找页面是否存在指定元素
    def base_is_exsit_elt(self,driver, location, timeout=30, poll=0.5):
        try:
            WebDriverWait(driver, timeout, poll).until(lambda el: el.find_element(*location))
            return True
        except:
            # print("未找到{}元素！".format(location))
            return False

    # 通过父类元素查找单个元素
    def base_find_el_by_fatherEL(self,driver, fatherEL, location, timeout=30, poll=0.5):
        return WebDriverWait(driver, timeout, poll).until(lambda el: fatherEL.find_element(*location))

    # 通过父类元素查找多个元素
    def base_find_els_by_fatherEL(self,driver, fatherEL, location, timeout=30, poll=0.5):
        return WebDriverWait(driver, timeout, poll).until(lambda el: fatherEL.find_elements(*location))

    # 切换窗口(句柄)
    def base_swith_window(self,driver, num):
        # 找到当前所有句柄
        list = driver.window_handles
        # 切换句柄
        driver.switch_to.window(list[num])
