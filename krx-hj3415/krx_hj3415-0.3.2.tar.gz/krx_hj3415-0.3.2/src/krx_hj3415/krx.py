import os
import time
import shutil
from datetime import datetime
import pandas as pd
import selenium.webdriver.chrome.webdriver
from sqlalchemy import create_engine, exc, text
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)


def get_driver(temp_dir: str = '') -> selenium.webdriver.chrome.webdriver.WebDriver:
    """ 크롬 드라이버를 반환

    Args:
        temp_dir : 크롬에서 다운받은 파일을 저장하는 임시디렉토리 경로(주로 krx_hj3415에서 사용)
    """
    # 크롬드라이버 옵션세팅
    options = webdriver.ChromeOptions()
    # reference from https://gmyankee.tistory.com/240
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-gpu')
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--disable-extensions")
    if temp_dir != '':
        logger.info(f'Set temp dir : {temp_dir}')
        options.add_experimental_option('prefs', {'download.default_directory': temp_dir})

    # 크롬드라이버 준비
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    print('Get chrome driver successfully...')

    return driver


# 코스피, 코스닥의 xpath
_MARKETS = [{'name': 'KOSPI', 'xpath': '//*[@id="rWertpapier"]'},
            {'name': 'KOSDAQ', 'xpath': '//*[@id="rKosdaq"]'}]

# 크롬에서 다운받은 파일을 저장할 임시 폴더 경로
_CUR_DIR = os.path.dirname(os.path.realpath(__file__))
_TEMP_DIR = os.path.join(_CUR_DIR, '_down_krx')
_DB_NAME = 'krx.db'
_DB_PATH = os.path.join(_CUR_DIR, _DB_NAME)

# krx 를 refresh 하는 최소 날짜
MIN_REFRESH_DAY = 10


def _get_tablename() -> str:
    """_200124 형식의 당시 날짜로 만들어진 테이블명을 반환한다.

    """
    con = sqlite3.connect(_DB_PATH)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    try:
        return cursor.fetchall()[0][0]
    except IndexError:
        logger.warning(f"Empty tablename.")
        return ''
    finally:
        cursor.close()
        con.close()


def _save_html_from_krx() -> bool:
    # 스크랩시 버튼 클릭간 대기시간
    wait = 1

    # 크롬드라이버 준비
    driver = get_driver(temp_dir=_TEMP_DIR)

    # krx 홈페이지에서 상장법인목록을 받아 html로 변환하여 저장한다.
    print(f'1. Download kosdaq, kospi files and save to temp folder.')
    shutil.rmtree(_TEMP_DIR, ignore_errors=True)
    driver.set_window_size(1280, 768)
    addr = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=loadInitPage'
    driver.get(addr)
    logger.info(f"Opening chrome and get page({addr})..")
    time.sleep(wait * 2)
    for market_dict in _MARKETS:
        # reference from https://stackoverflow.com/questions/2083987/how-to-retry-after-exception(Retry)
        retry = 3
        filename = f"{market_dict['name']}.html"
        for i in range(retry):
            try:
                logger.info('Manipulating buttons...')
                driver.find_element_by_xpath(market_dict['xpath']).click()  # 라디오버튼
                time.sleep(wait)
                # 검색버튼 XPATH - '//*[@id="searchForm"]/section/div/div[3]/a[1]'(2020.1.22)
                driver.find_element_by_xpath('//*[@id="searchForm"]/section/div/div[3]/a[1]').click()  # 검색버튼
                time.sleep(wait)
                # 검색버튼 XPATH - '//*[@id="searchForm"]/section/div/div[3]/a[2]'(2020.1.22)
                driver.find_element_by_xpath('//*[@id="searchForm"]/section/div/div[3]/a[2]').click()  # 엑셀다운버튼
                time.sleep(wait * 2)
                # krx에서 다운받은 파일은 상장법인목록.xls이지만 실제로는 html파일이라 변환해서 저장한다.
                excel_file = os.path.join(_TEMP_DIR, '상장법인목록.xls')
                os.rename(excel_file, os.path.join(_TEMP_DIR, filename))
                logger.info(f"Save file as .\\{_TEMP_DIR}\\{filename}")
                break
            except Exception:
                # 재다운로드를 3회까지 시도해 본다.
                if i < retry - 1:
                    wait = wait * 2
                    logger.error(f'Retrying..{i + 1}')
                    continue
                else:
                    logger.error(f'Downloading error for {retry} times..')
                    driver.quit()
                    return False
    driver.quit()
    return True


def _save_db_from_html() -> bool:
    # 테이블명은 숫자로 시작하면 안된다.
    NEW_TABLE_NAME = '_' + datetime.today().strftime('%y%m%d')

    print(f'2. Get data from temp files and save to .\\{_DB_NAME} (table:{NEW_TABLE_NAME})')
    engine = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
    # Drop table
    # reference from https://stackoverflow.com/questions/33229140/how-do-i-drop-a-table-in-sqlalchemy-when-i-dont-have-a-table-object/34834205
    OLD_TABLE_NAME = _get_tablename()
    if OLD_TABLE_NAME != '':
        logger.info(f"Drop previous '{OLD_TABLE_NAME}' table ...")
        with engine.connect() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS {OLD_TABLE_NAME}'))
            conn.execute(text('VACUUM'))
    # html 파일을 pandas로 읽어 데이터베이스에 저장한다.
    for market_dict in _MARKETS:
        filename = f"{market_dict['name']}.html"
        try:
            with open(os.path.join(_TEMP_DIR, filename), encoding='euc-kr') as f:
                logger.info(f"Open .\\{_TEMP_DIR}\\{filename} and convert to {market_dict['name']} dataframe.")
                df = pd.read_html(f.read(), header=0, converters={'종목코드': str}, encoding='utf-8')[0]
                # 테이블을 저장한다.append로 저장해야 kosdaq과 kospi같이 저장됨
                logger.info(f"Append {market_dict['name']} dataframe to .\\{_DB_NAME} (table:{NEW_TABLE_NAME})")
                df.to_sql(NEW_TABLE_NAME, con=engine, index=False, if_exists='append')
        except FileNotFoundError:
            logger.critical('There is not temp files for saving db. please download file first.')
            return False
    engine.dispose()
    shutil.rmtree(_TEMP_DIR, ignore_errors=True)
    return True


def make_db():
    _save_html_from_krx()
    _save_db_from_html()


def is_old_krx() -> bool:
    # 빈테이블명의 경우는 2000년 1월1 일로 임의로 날짜를 할당한다.
    underbar_create_date = '_000101' if _get_tablename() == '' else _get_tablename()
    # krx.db가 MIN_REFRESH_DAY일 이상 오래된 것이면 재 다운로드를 권고함.
    if os.path.exists(_DB_PATH):
        db_created_date = datetime.strptime(underbar_create_date, '_%y%m%d')
        if (datetime.today() - db_created_date).days > MIN_REFRESH_DAY:
            return True
        else:
            return False
    else:
        raise FileNotFoundError


def _get_df():
    """실제로 데이터프레임을 만들어서 반환하는 함수

    """
    while is_old_krx():
        print(f"It's too old to use 'krx.db({_get_tablename()[1:]})', refreshing database...")
        make_db()

    try:
        engine = create_engine(f"sqlite:///{_DB_PATH}")
    except exc.OperationalError:
        logger.critical(f"There is not {_DB_PATH}, please run make_db() first.")
        return None
    else:
        table_name = _get_tablename()
        df = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)
        return df


def get_codes() -> list:
    """전체 krx 코드를 담은 리스트를 반환한다.

    """
    while True:
        df = _get_df()
        if df is not None:
            break
    return list(df.loc[:, '종목코드'])


def get_name_codes() -> dict:
    """
    key - 코드, value - 종목명을 가지는 전체 krx 딕셔너리를 반환한다.
    """
    while True:
        df = _get_df()
        if df is not None:
            break
    return df.set_index('종목코드').loc[:, ['회사명']].to_dict()['회사명']


def get_name(code: str) -> str:
    """
    코드를 인자로 받으면 종목명을 반환한다.
    """
    return get_name_codes().get(code)


def get_parts() -> list:
    """
    전체 2200여개의 전체 코드리스트를 10등분하여 오늘 날짜의 끝자리에 해당하는 리스트를 튜플로 반환한다.
    """
    def split_list(alist, wanted_parts=1):
        # 멀티프로세싱할 갯수로 리스트를 나눈다.
        # reference from https://www.it-swarm.dev/ko/python/%EB%8D%94-%EC%9E%91%EC%9D%80-%EB%AA%A9%EB%A1%9D%EC%9C%BC%EB%A1%9C-%EB%B6%84%ED%95%A0-%EB%B0%98%EC%9C%BC%EB%A1%9C-%EB%B6%84%ED%95%A0/957910776/
        length = len(alist)
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                for i in range(wanted_parts)]
    while True:
        df = _get_df()
        if df is not None:
            break
    codes = list(df.loc[:, '종목코드'])
    return split_list(codes, wanted_parts=10)[int(datetime.today().strftime('%d')[-1])]


if __name__ == '__main__':
    # make_db()
    print(len(get_parts()))
