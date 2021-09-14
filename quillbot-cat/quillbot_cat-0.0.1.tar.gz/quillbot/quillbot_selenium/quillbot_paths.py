from selenium.webdriver.common.by import By

LOGIN = (By.XPATH, "//span[contains(text(), 'Login')]")
EMAIL_FIELD = (By.XPATH, "//input[contains(@class, 'MuiInputBase-input') and @type='text']")
PASSWORD_FIELD = (By.XPATH, "//input[contains(@class, 'MuiInputBase-input') and @type='password']")
LOG_IN = (By.XPATH, "//span[contains(text(), 'Log In')]")
INPUT_TEXT = (By.XPATH, "//*[contains(@id, 'inputText')]")
PARAPHRASE_BUTTON = (By.XPATH, "//button[contains(@class, 'MuiButtonBase-root')]//div[contains(text(), 'Paraphrase')]")
REPHRASE_BUTTON = (By.XPATH, "//button[contains(@class, 'MuiButtonBase-root')]//div[contains(text(), 'Rephrase')]")
CONFIRMATION_BOX = "//*[@class='MuiDialog-container MuiDialog-scrollPaper']"
CONFIRMATION_CHECKBOX = "//*[@class='MuiGrid-root MuiGrid-container']//input[@type='checkbox']"
CONFIRMATION_BUTTON = "//button[contains(@class,'MuiButtonBase-root MuiButton-root MuiButton-text')]//span[text()='CONTINUE']"
CLEAN_TEXT_BUTTON = (By.XPATH, "//*[@d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM8 9h8v10H8V9zm7.5-5l-1-1h-5l-1 1H5v2h14V4h-3.5z']")
OUTPUT_TEXT = (By.XPATH, "//*[@id='outputText']")
POPAP = (By.XPATH, "//*[contains(@class, 'MuiPaper-root MuiDialog-paper')]")
