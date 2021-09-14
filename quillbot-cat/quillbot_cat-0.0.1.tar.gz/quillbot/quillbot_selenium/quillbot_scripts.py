from time import sleep

from selenium import webdriver
from attr import attrs, attrib, validators

from quillbot.quillbot_selenium.common import CommonTools
from quillbot.quillbot_selenium.quillbot_paths import LOGIN, EMAIL_FIELD, PASSWORD_FIELD, LOG_IN, INPUT_TEXT, \
    PARAPHRASE_BUTTON, OUTPUT_TEXT, \
    CLEAN_TEXT_BUTTON, CONFIRMATION_BOX, CONFIRMATION_CHECKBOX, CONFIRMATION_BUTTON, POPAP, REPHRASE_BUTTON

from quillbot.settings import BROWSER_OPTIONS, GECKODRIVER_PATH, QUILLBOT_DATA


@attrs
class InputDataValidator:
    text = attrib(validator=[validators.instance_of(str)])


class Quillbot:
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path=GECKODRIVER_PATH, options=BROWSER_OPTIONS)
        self.url = QUILLBOT_DATA["url"]
        self.login = QUILLBOT_DATA["login"]
        self.password = QUILLBOT_DATA["password"]
        self.common = CommonTools(self.driver)

    def authorize_user(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.common.find_element(LOGIN).click()
        self.common.find_element(EMAIL_FIELD).send_keys(self.login)
        self.common.find_element(PASSWORD_FIELD).send_keys(self.password)
        self.common.find_element(LOG_IN).click()

    def paraphrase_content_free(self, content_to_paraphrase: str, driver) -> str:
        output_data = ""
        common = CommonTools(driver)

        paraphrase_button = common.find_element(PARAPHRASE_BUTTON)

        if paraphrase_button.is_displayed():
            common.find_element(INPUT_TEXT).send_keys(content_to_paraphrase)
            sleep(5)
            paraphrase_button.click()
            if common.find_element(REPHRASE_BUTTON, 300).is_displayed():
                paraphrased_el = common.find_element(OUTPUT_TEXT)
                if paraphrased_el.is_displayed():
                    paraphrased = paraphrased_el.text
                    output_data += paraphrased

                    clean_btn = common.find_element(CLEAN_TEXT_BUTTON)
                    common.click_element(clean_btn)
                    sleep(2)
                    try:
                        if driver.find_element_by_xpath(CONFIRMATION_BOX).is_displayed():
                            driver.find_element_by_xpath(CONFIRMATION_CHECKBOX).click()
                            driver.find_element_by_xpath(CONFIRMATION_BUTTON).click()
                    except Exception as e:
                        print("There is no confirmation box anymore")

            return output_data

    def paraphrase_all_content_free(self, input_data: str) -> str:
        data_pieces = input_data.split(".")
        output_data = ""
        content_to_paraphrase = ""
        count_of_paraphrasing = 0
        driver = webdriver.Firefox(executable_path=GECKODRIVER_PATH, options=BROWSER_OPTIONS)
        driver.get(QUILLBOT_DATA["url"])
        driver.maximize_window()

        for piece in data_pieces:
            if piece == '':
                data_pieces.remove(piece)

        for i in range(len(data_pieces)):
            exact_len = len(content_to_paraphrase) + len(data_pieces[i])
            if count_of_paraphrasing == 3:
                driver = webdriver.Firefox(executable_path=GECKODRIVER_PATH, options=BROWSER_OPTIONS)
                driver.get(QUILLBOT_DATA["url"])
                driver.maximize_window()
                count_of_paraphrasing = 0
            if exact_len <= 400:
                content_to_paraphrase += data_pieces[i] + '. '
            if (exact_len > 400) or (i == len(data_pieces) - 1 and exact_len <= 400):
                output_data += self.paraphrase_content_free(content_to_paraphrase, driver)
                count_of_paraphrasing += 1

                if count_of_paraphrasing == 3:
                    driver.quit()
                content_to_paraphrase = ""
        return output_data

    def paraphrase_content(self, content_to_paraphrase: str) -> str:
        output_data = ""
        paraphrase_button = self.common.find_element_presence(PARAPHRASE_BUTTON)

        if paraphrase_button.is_displayed():
            self.common.find_element(INPUT_TEXT).send_keys(content_to_paraphrase)
            sleep(10)
            self.common.click_element(paraphrase_button)

            if self.common.find_element(REPHRASE_BUTTON, 300).is_displayed():
                paraphrased_el = self.common.find_element(OUTPUT_TEXT)
                if paraphrased_el.is_displayed():
                    paraphrased = paraphrased_el.text
                    output_data += paraphrased

                    clean_btn = self.common.find_element(CLEAN_TEXT_BUTTON)
                    self.common.click_element(clean_btn)
                    sleep(2)
                    try:
                        if self.driver.find_element_by_xpath(CONFIRMATION_BOX).is_displayed():
                            self.driver.find_element_by_xpath(CONFIRMATION_CHECKBOX).click()
                            self.driver.find_element_by_xpath(CONFIRMATION_BUTTON).click()
                    except Exception as e:
                        print("There is no confirmation box anymore")

        return output_data

    def paraphrase_all_content(self, input_data: str) -> str:
        data_pieces = input_data.split(".")
        output_data = ""
        content_to_paraphrase = ""

        for piece in data_pieces:
            if piece == '':
                data_pieces.remove(piece)

        for i in range(len(data_pieces)):
            exact_len = len(content_to_paraphrase) + len(data_pieces[i])

            if exact_len <= 8000:
                content_to_paraphrase += data_pieces[i] + '. '
            if (exact_len > 8000) or (i == len(data_pieces) - 1 and exact_len <= 8000):
                print("start paraphrasing")
                output_data += self.paraphrase_content(content_to_paraphrase)
                content_to_paraphrase = ""

        return output_data
