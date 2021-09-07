from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

import time


def find_elements_by_text(driver, text):
    elements = []
    text_elements = driver.find_elements_by_xpath("//*[text()='{0}']|//*[@value='{0}']|//*[@placeholder='{0}']".format(text))
    if text_elements and len(text_elements) > 0:
        elements.extend(text_elements)

    return elements


class WaitVisibilityLambda:
    def __init__(self, text):
        self._text = text

    def __call__(self, driver):
        elements = find_elements_by_text(driver, self._text)
        if not elements or len(elements) == 0:
            return False
        else:
            return elements[0]


def find_element(driver, text, anchor_type=''):
    print('find_element start: ' + time.asctime(time.localtime(time.time())))
    wait = WebDriverWait(driver, 20, 0.2)
    result = wait.until(WaitVisibilityLambda(text))
    print('find_element after awit element: ' + time.asctime(time.localtime(time.time())))

    elements = find_elements_by_text(driver, text)
    print('find_element elements: '  + time.asctime(time.localtime(time.time())))
    print(elements)
    if not elements or len(elements) == 0:
        return None

    max_probability_element = elements[0]
    if not anchor_type:
        return max_probability_element
    for element in elements:
        location = element.location
        print('element {0} location {1}'.format(element.text, location))
        if '左' in anchor_type:
            max_probabilty_location = max_probability_element.location
            if max_probabilty_location['x'] > location['x']:
                max_probability_element = element
        if '右' in anchor_type:
            max_probabilty_location = max_probability_element.location
            if max_probabilty_location['x'] < location['x']:
                max_probability_element = element
        if '上' in anchor_type:
            max_probabilty_location = max_probability_element.location
            if max_probabilty_location['y'] < location['y']:
                max_probability_element = element
        if '下' in anchor_type:
            max_probabilty_location = max_probability_element.location
            if max_probabilty_location['y'] > location['y']:
                max_probability_element = element

    return max_probability_element


# 查找最合适的element
# 算法：在mc_select之下 最接近的
# mc_select_input[1].send_keys(Keys.RETURN)
def find_max_probability_element(elements, anchor_element, anchor_type=''):
    max_probability_element = None
    anchor_element_location = anchor_element.location
    for element in elements:
        location = element.location
        if '下' in anchor_type:  # 查找的元素位于锚点元素的下方
            if location['y'] > anchor_element_location['y']:
                if max_probability_element:
                    max_probabilty_location = max_probability_element.location
                    if ((max_probabilty_location['y'] - anchor_element_location['y']) > (
                            location['y'] - anchor_element_location['y']) \
                            or (max_probabilty_location['x'] - anchor_element_location['x']) > (
                                    location['x'] - anchor_element_location['x'])):
                        max_probability_element = element
                else:
                    max_probability_element = element
        else:  # 默认情况查找离锚点元素最进的元素
            if max_probability_element:
                max_probabilty_location = max_probability_element.location
                if ((max_probabilty_location['y'] - anchor_element_location['y']) > (
                        location['y'] - anchor_element_location['y']) \
                        or (max_probabilty_location['x'] - anchor_element_location['x']) > (
                                location['x'] - anchor_element_location['x'])):
                    max_probability_element = element
            else:
                max_probability_element = element

    return max_probability_element


def click_element(web_driver, text, anchor_type=''):
    element = find_element(web_driver, text, anchor_type)
    if element:
        element.click()
    else:
        pass  # 抛出异常


def login(web_driver, username, password, env='test'):
    if env == 'test':
        web_driver.get('https://test.salesforce.com/login.jsp?pw={1}&un={0}'.format(username, password))
        click_element(web_driver, 'Continue')
    else:  # 其他环境的okta登录处理
        pass


def open_url(driver, url):
    driver.implicitly_wait(2)
    driver.get(url)


def set_value(web_driver, label_text, value, anchor_type=''):
    label_element = find_element(web_driver, label_text, anchor_type)
    print('set_value label element:')
    print(label_element)
    if label_element:
        if 'select' in anchor_type:  # 下拉选项
            select_input_elements = find_elements_by_text(web_driver, 'Search...')
            print('input elements:')
            print(select_input_elements)
            select_input_element = find_max_probability_element(select_input_elements, label_element, '下')
            # select_input_element.send_keys(value)
            select_input_element.send_keys(Keys.RETURN)
            click_element(web_driver, value, '')
        else:  # 默认找input或 textarea元素 进行录入
            parent = label_element.find_element_by_xpath("..")
            input_elements = parent.find_elements_by_xpath("//input|//textarea")
            input_element = find_max_probability_element(input_elements, label_element, '下')
            input_element.send_keys(value)