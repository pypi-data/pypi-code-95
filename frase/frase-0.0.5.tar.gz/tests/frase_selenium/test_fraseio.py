from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from time import sleep
import pytest

from frase.frase_selenium.fraseio_paths import SIGN_IN_BUTTON, CREATE_DOC_BUTTON, \
    SHOW_FOLDERS_DROPDOWN, \
    FOLDERS_DROPDOWN, \
    CREATE_NEW_FOLDER, FOLDER_NAME_FIELD, CREATE_NEW_FOLDER_ACCEPT, ADVANCED_SETTINGS, SHOW_COUNTRIES_DROPDOWN, \
    SHOW_LANG_DROPDOWN, DOC_SEARCH_RESULT, ASSETS, \
    TITLES, PARAGRAPHS, PASTE_FULLS, WORD_COUNT, BACK_TO_HOME, DELETE_FOLDER, DELETE_CONFIRMATION
from frase.frase_selenium.common import CommonTools
from frase.settings import BROWSER_OPTIONS, GECKODRIVER_PATH, FRASE_DATA

driver = webdriver.Firefox(executable_path=GECKODRIVER_PATH, options=BROWSER_OPTIONS)
url = FRASE_DATA["url"]
login = FRASE_DATA["login"]
password = FRASE_DATA["password"]
common = CommonTools(driver)


def set_folder(folder_name: str):
    common.find_element(SHOW_FOLDERS_DROPDOWN).click()
    folders = common.find_elements(FOLDERS_DROPDOWN, 20)
    folders_amount = len(folders)

    for num in range(folders_amount):
        folder = folders[num]
        print(folder_name, folder.text)

        if folder_name == folder.text and num != folders_amount - 1:
            folder.click()
            break
        elif num == folders_amount - 1 and folder_name != folder:
            common.find_element(CREATE_NEW_FOLDER).click()
            common.find_element(FOLDER_NAME_FIELD).send_keys(folder_name)
            common.find_element(CREATE_NEW_FOLDER_ACCEPT).click()


def set_country(country_name):
    common.find_element(SHOW_COUNTRIES_DROPDOWN).click()
    country = driver.find_element_by_xpath(
        "//li[@ng-click='selectCountry(code); showCountryDropdown();']//a[contains(text(), '" + country_name + "')]")
    assert country.is_displayed() is True, f"There is no following element(s): {country}"
    country.click()


def set_language(language):
    common.find_element(SHOW_LANG_DROPDOWN).click()
    lang = driver.find_element_by_xpath(
        "//li[@ng-click='selectLanguage(lang)']//a[contains(text(), '" + language + "')]")
    assert lang.is_displayed() is True, f"There is no following element(s): {lang}"
    lang.click()


class TestFraseio:
    def test_authorize_user(self):
        try:
            driver.get(url)
            driver.maximize_window()
            username_field = driver.find_element_by_id("username")
            password_field = driver.find_element_by_id("password")
            assert username_field.is_displayed() and password_field.is_displayed(), f"Following auth elements aren't visible: {username_field},\n{password_field}"

            username_field.send_keys(login)
            password_field.send_keys(password)
            common.find_element(SIGN_IN_BUTTON).click()
            sleep(5)
        except WebDriverException as e:
            pytest.fail(str(e))

    def test_create_document(self):
        try:
            create_doc = common.find_element(CREATE_DOC_BUTTON)
            assert driver.find_element_by_xpath(
                "//*[@id='create-doc-button']//a[@href='/app/dashboard/documents/new-document/']").is_displayed() is True, f"There is no following element(s): {create_doc}"
            create_doc.click()
            sleep(5)

            query_field = driver.find_element_by_xpath(
                "//div[@class='doc-settings-field ng-scope']//input[@ng-model='document_queries[$index]']")
            folder_field = driver.find_element_by_xpath("//*[@ng-click='showChannelsDropdown()']")
            advanced_settings_field = driver.find_element_by_xpath("//a[@ng-click='showAdvancedSettings()']")
            assert all([query_field.is_displayed(), folder_field.is_displayed(),
                        advanced_settings_field.is_displayed()]) is True

            query_field.send_keys("Test query")
            set_folder("TestFolder")
            common.find_element(ADVANCED_SETTINGS).click()
            sleep(2)

            countries_field = driver.find_element_by_xpath("//*[@ng-click='showCountryDropdown()']")
            lang_field = driver.find_element_by_xpath("//*[@ng-click='showLangDropdown()']")
            create_doc_accept_field = driver.find_element_by_xpath("//a[@ng-click='createDocument()']")
            assert all([countries_field.is_displayed(), lang_field.is_displayed(), create_doc_accept_field]) is True
            set_country("Germany")
            set_language("German")
            create_doc_accept_field.click()
            sleep(5)
        except WebDriverException as e:
            pytest.fail(str(e))

    def test_get_data(self):
        try:
            common.find_element(DOC_SEARCH_RESULT)
            headers = driver.find_element_by_xpath("//*[@ng-click=\"setSubview('headers')\"]")
            assert headers.is_displayed() is True, f"There is no following element(s): {headers}"
            common.click_element(headers)
            assets = common.find_elements(ASSETS)
            assets_amount = len(assets)
            texts_len = 0
            numb = 0
            data = ""
            word_count = 0

            for i in range(assets_amount):
                assets[i].click()
                headers = common.find_elements(TITLES)
                paragraphs = common.find_elements(PARAGRAPHS)
                paste_fulls = common.find_elements(PASTE_FULLS)
                data += "<h2>\n" + headers[i + numb].text + '\n'
                numb += 1

                for j in range(texts_len, len(paragraphs)):
                    data += "<p>\n" + paragraphs[j].text + '\n'
                texts_len = len(paragraphs)
                paste_fulls[i].click()
                word_count = int(common.find_element(WORD_COUNT).text)
                if word_count > 1000:
                    break

            assert word_count > 1000, "The length of the generated text is wrong"
        except WebDriverException as e:
            pytest.fail(str(e))

    def test_delete_folder(self):
        try:
            common.find_element(BACK_TO_HOME).click()
            sleep(3)
            assert driver.current_url == "https://app.frase.io/app/dashboard/documents"

            if driver.find_element_by_id("pushActionRefuse").is_displayed():
                driver.find_element_by_id("pushActionRefuse").click()

            folders = driver.find_element_by_xpath("//*[@ng-show='!selectedChannel']")
            assert folders.is_displayed() is True, f"There is no following element(s): {folders}"
            common.click_element(folders)
            folder = driver.find_element_by_xpath("//a[@ng-click='selectChannel(channel)' and text()='TestFolder']")
            assert folder.is_displayed() is True, f"There is no following element(s): {folder}"
            folder.click()
            sleep(5)
            edit_folder = driver.find_element_by_xpath(
                "/html/body/div[1]/div[2]/div/div[1]/div[1]/div[1]/div[6]/div[2]/a")
            assert edit_folder.is_displayed() is True, f"There is no following element(s): {edit_folder}"
            edit_folder.click()
            common.find_element(DELETE_FOLDER).click()
            common.find_element(DELETE_CONFIRMATION).click()
            driver.quit()
        except WebDriverException as e:
            pytest.fail(str(e))
