import json
import re
from dataclasses import make_dataclass
from functools import lru_cache
from threading import Lock, local
from typing import Union

import requests
import selenium
from .exception import UnknownSiteException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

thread_local = local()

Problem = make_dataclass('Problem', [('code', str), ('level', str), ('link', str), ('title', str)])
Solution = make_dataclass('Solution', [('user_id', str), ('problem_codes', list[str])])


class AlgoSite:
  def __init__(self, headless=True):
    self.driver = getattr(thread_local, "driver", None)
    with Lock():
      if self.driver is None:
        chrome_options = webdriver.ChromeOptions()
        if headless:
          chrome_options.add_argument("--headless")  # Headless doesn't work for hackerrank
          chrome_options.add_argument("--no-sandbox")
          chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        setattr(thread_local, "driver", self.driver)

  def crawl_solutions(self, id_: str) -> Solution:
    raise NotImplementedError

  def crawl_problem(self, code: str) -> Problem:
    raise NotImplementedError

  @property
  def prefix(self):
    raise NotImplementedError

  @staticmethod
  def get_site_by_prefix(prefix):
    if prefix == "BJ":
      return Baekjoon()
    if prefix == "LC":
      return Leetcode()
    if prefix == "KT":
      return Kattis()
    if prefix == "HR":
      return Hackerrank()
    if prefix == "CC":
      return Codechef()
    if prefix == "CF":
      return Codeforce()
    raise UnknownSiteException


class Baekjoon(AlgoSite):
  @property
  def prefix(self):
    return "BJ"

  def crawl_solutions(self, id_: str) -> Solution:
    self.driver.get(f"https://www.acmicpc.net/user/{id_}")
    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "panel-body")))
    return Solution(id_, self.driver.find_element_by_class_name("panel-body").text.split())

  def crawl_problem(self, code: Union[int, str]) -> Problem:
    response = requests.get(f"https://solved.ac/api/v3/problem/show?problemId={code}")
    dic = json.loads(response.text)
    level = str(dic['level'])
    title = dic['titleKo']
    link = f"https://www.acmicpc.net/problem/{code}"
    return Problem(f"{self.prefix}_{code}", level, link, title)


class Leetcode:
  @property
  def prefix(self):
    return "LC"

  # TODO #6 Implement Leetcode crawl_solutions()

  @lru_cache(None)
  def _crawl_problems(self) -> dict[str, Problem]:
    response = requests.get("https://leetcode.com/api/problems/all/")
    dic = json.loads(response.text)
    code2problem = {}
    for prob in dic["stat_status_pairs"]:
      code = str(prob["stat"]["frontend_question_id"])
      level = str(prob["difficulty"]["level"])
      link = f"https://leetcode.com/problems/{prob['stat']['question__title_slug']}"
      title = prob["stat"]["question__title"]
      code2problem[code] = Problem(f"{self.prefix}_{code}", level, link, title)
    return code2problem

  def crawl_problem(self, code: Union[str, int]) -> Problem:
    return self._crawl_problems()[str(code)]


class Kattis(AlgoSite):
  @property
  def prefix(self):
    return "KT"

  # TODO #5 Implement Kattis crawl_solutions()

  def crawl_problem(self, code: str) -> Problem:
    link = f"https://open.kattis.com/problems/{code}"
    self.driver.get(link)
    WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    level = self.driver.find_element_by_css_selector("div.sidebar-info > p:nth-child(4)").text.split()[-1]
    title = self.driver.find_element_by_css_selector("h1").text
    return Problem(f"{self.prefix}_{code}", level, link, title)


class Codechef(AlgoSite):
  @property
  def prefix(self):
    return "CC"

  # TODO #4 Implement Codechef crawl_solutions()

  def crawl_problem(self, code: str) -> Problem:
    link = f"https://www.codechef.com/problems/{code}"
    self.driver.get(link)
    try:
      level = self.driver.find_elements_by_css_selector("aside>a")[1].text
      title = self.driver.find_element_by_css_selector("h1").text.split(" Problem Code")[0]
    except IndexError:
      return {}
    return Problem(f"{self.prefix}_{code}", level, link, title)


class Codeforce(AlgoSite):
  @property
  def prefix(self):
    return "CF"

  # TODO #3 Implement Codeforce crawl_solutions()

  def crawl_problem(self, code: str) -> Problem:
    number = re.findall(r"^\d+", code)[0]
    letter = code[len(number):]
    link = f"https://codeforces.com/contest/{number}/problem/{letter}"

    self.driver.get(link)
    title = self.driver.find_element_by_css_selector("div.title").text.split(".")[1].strip()
    level = self.driver.find_element_by_css_selector('[title="Difficulty"]').text.strip(" *")
    return Problem(f"{self.prefix}_{code}", level, link, title)


class Hackerrank(AlgoSite):
  @property
  def prefix(self):
    return "HR"

  # TODO #7 Implement Hackerrank crawl_solutions()

  def crawl_problem(self, code: str) -> Problem:
    link = f"https://www.hackerrank.com/challenges/{code}/problem"
    self.driver.get(link)
    try:
      WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "difficulty-block")))
      level = self.driver.find_elements_by_class_name("difficulty-block")[1].text.split()[-1]
    except selenium.common.exceptions.NoSuchElementException:
      level = "Medium"
    except selenium.common.exceptions.TimeoutException:
      level = "Medium"

    try:
      title = self.driver.find_element_by_class_name("ui-icon-label").text
    except selenium.common.exceptions.NoSuchElementException:
      title = code

    return Problem(f"{self.prefix}_{code}", level, link, title)


# TODO #8 Implement UVA class
# TODO #9 Implement POJ class
# TODO #10 Implement SPOJ class
