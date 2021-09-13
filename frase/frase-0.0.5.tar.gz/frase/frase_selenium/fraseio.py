from selenium import webdriver
from attr import attrs, attrib, validators
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep

from frase.frase_selenium.fraseio_paths import SIGN_IN_BUTTON, CREATE_DOC_BUTTON, QUERY_FIELD, \
    SHOW_FOLDERS_DROPDOWN, \
    FOLDERS_DROPDOWN, \
    CREATE_NEW_FOLDER, FOLDER_NAME_FIELD, CREATE_NEW_FOLDER_ACCEPT, ADVANCED_SETTINGS, SHOW_COUNTRIES_DROPDOWN, \
    COUNTRIES_DROPDOWN, SHOW_LANG_DROPDOWN, LANG_DROPDOWN, CREATE_DOC_ACCEPT, DOC_SEARCH_RESULT, HEADERS_TAB, ASSETS, \
    TITLES, PARAGRAPHS, PASTE_FULLS, WORD_COUNT, BACK_TO_HOME, FOLDERS, EDIT_FOLDER, DELETE_FOLDER, DELETE_CONFIRMATION, REFUSE_NOTIFICATIONS
from frase.frase_selenium.common import CommonTools
from frase.settings import BROWSER_OPTIONS, GECKODRIVER_PATH, FRASE_DATA


@attrs
class InputDataValidator:
    query = attrib(validator=[validators.instance_of(str)])
    lang = attrib(validator=[validators.instance_of(str)])
    country = attrib(validator=[validators.instance_of(str)])
    text_length = attrib(validator=[validators.instance_of(int)])


class Fraseio:
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path=GECKODRIVER_PATH, options=BROWSER_OPTIONS)
        self.url = FRASE_DATA["url"]
        self.login = FRASE_DATA["login"]
        self.password = FRASE_DATA["password"]
        self.common = CommonTools(self.driver)

    def authorize_user(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.find_element_by_id("username").send_keys(self.login)
        self.driver.find_element_by_id("password").send_keys(self.password)
        self.common.find_element(SIGN_IN_BUTTON).click()

    def create_document(self, query: str, folder_name: str, language: str, country_name: str):
        self.common.find_element(CREATE_DOC_BUTTON).click()
        self.common.find_element(QUERY_FIELD).send_keys(query)
        self.set_folder(folder_name)
        self.common.find_element(ADVANCED_SETTINGS).click()
        self.set_country(country_name)
        self.set_language(language)
        self.common.find_element(CREATE_DOC_ACCEPT).click()

    def set_folder(self, folder_name: str):
        self.common.find_element(SHOW_FOLDERS_DROPDOWN).click()
        folders = self.common.find_elements(FOLDERS_DROPDOWN, 20)
        folders_amount = len(folders)

        for num in range(folders_amount):
            folder = folders[num]
            print(folder_name, folder.text)

            if folder_name == folder.text and num != folders_amount - 1:
                folder.click()
                break
            elif num == folders_amount - 1 and folder_name != folder:
                self.common.find_element(CREATE_NEW_FOLDER).click()
                self.common.find_element(FOLDER_NAME_FIELD).send_keys(folder_name)
                self.common.find_element(CREATE_NEW_FOLDER_ACCEPT).click()

    def set_country(self, country_name):
        self.common.find_element(SHOW_COUNTRIES_DROPDOWN).click()
        country_xpath = "//li[@ng-click='selectCountry(code); showCountryDropdown();']//a[contains(text(), '" + country_name + "')]"
        try:
            if self.driver.find_element_by_xpath(country_xpath).is_displayed():
                self.driver.find_element_by_xpath(country_xpath).click()
        except NoSuchElementException:
            print("There was no such country")
            pass

    def set_language(self, language):
        self.common.find_element(SHOW_LANG_DROPDOWN).click()
        lang_xpath = "//li[@ng-click='selectLanguage(lang)']//a[contains(text(), '" + language + "')]"
        try:
            if self.driver.find_element_by_xpath(lang_xpath).is_displayed():
                self.driver.find_element_by_xpath(lang_xpath).click()
        except NoSuchElementException:
            print("There was no such language")
            pass

    def delete_folder(self, folder_name):
        self.common.find_element(BACK_TO_HOME).click()
        if self.driver.find_element_by_id("pushActionRefuse").is_displayed():
            self.driver.find_element_by_id("pushActionRefuse").click()

        if self.driver.find_element_by_xpath("//*[@ng-show='!selectedChannel']").is_displayed():
            folders = self.common.find_element(FOLDERS)
            self.common.click_element(folders)
            folder_locator = (By.XPATH, "//a[@ng-click='selectChannel(channel)' and text()='" + folder_name + "']")
            self.common.find_element(folder_locator).click()
            edit_folder = self.common.find_element(EDIT_FOLDER)
            sleep(3)
            edit_folder.click()
            self.common.find_element(DELETE_FOLDER).click()
            self.common.find_element(DELETE_CONFIRMATION).click()

    def get_data(self, text_length: int) -> str:
        self.common.find_element(DOC_SEARCH_RESULT)
        headers = self.common.find_element(HEADERS_TAB)
        self.common.click_element(headers)

        assets = self.common.find_elements(ASSETS)
        assets_amount = len(assets)
        texts_len = 0
        numb = 0
        data = ""

        for i in range(assets_amount):
            assets[i].click()
            headers = self.common.find_elements(TITLES)
            paragraphs = self.common.find_elements(PARAGRAPHS)
            paste_fulls = self.common.find_elements(PASTE_FULLS)
            data += "<h2>\n" + headers[i + numb].text + '\n'
            numb += 1

            for j in range(texts_len, len(paragraphs)):
                data += "<p>\n" + paragraphs[j].text + '\n'
            texts_len = len(paragraphs)
            paste_fulls[i].click()

            if int(self.common.find_element(WORD_COUNT).text) > text_length:
                break
        return data

    def get_countries_and_languages(self) -> dict:
        try:
            self.common.find_element(CREATE_DOC_BUTTON).click()
            self.common.find_element(ADVANCED_SETTINGS).click()

            self.common.find_element(SHOW_COUNTRIES_DROPDOWN).click()

            countries = self.common.find_elements(COUNTRIES_DROPDOWN)
            countries_amount = len(countries)

            res_countries = []
            res_languages = []

            for num in range(countries_amount):
                res_countries.append(countries[num].text)

            self.common.find_element(SHOW_LANG_DROPDOWN).click()

            langs = self.common.find_elements(LANG_DROPDOWN)
            langs_amount = len(langs)

            for num in range(langs_amount):
                res_languages.append(langs[num].text)

            res = {
                "countries": res_countries,
                "languages": res_languages
            }
            return res
        except WebDriverException as e:
            print(str(e))

    def run(self, input_data: InputDataValidator):
        folder_name = "TempFolder"
        try:
            self.authorize_user()
            self.create_document(input_data.query, folder_name, input_data.lang, input_data.country)
            output_data = self.get_data(input_data.text_length)
            self.delete_folder(folder_name)
            self.driver.quit()
            return output_data
        except Exception as e:
            self.driver.quit()
            print(str(e))


if __name__ == "__main__":
    from frase.utils import check_dict_attr

    data = {
        "query": "Hello world query",
        "lang": "German",
        "country": "Germany",
        "text_length": 1000
    }

    data = check_dict_attr(InputDataValidator, data, "Invalid input data")
    frase_io = Fraseio()
    res = frase_io.run(data)
    print(res)
