# 基类——操作层
from selenium.webdriver import ActionChains


class BaseHandle:
    def __init__(self):
        pass

    # 元素输入操作
    def base_input(self, element, text):
        element.clear()
        element.send_keys(text)

    # 元素点击操作
    def base_click(self, element):
        element.click()

    #获取元素文本信息
    def base_getText(self,element):
        return element.text

    # 通过文本判断元组中相同元素，并输出下标
    def base_getIndex_by_elements_text(self, elements, text):
        for i in range(0, len(elements)):
            if elements[i].text == text:
                return i

    # 鼠标移上(condition是否点击)
    def base_move_to_element(self,driver, element, condition):
        if condition is True:
            ActionChains(driver).move_to_element(element).click(element).perform()
        else:
            ActionChains(driver).move_to_element(element).perform()