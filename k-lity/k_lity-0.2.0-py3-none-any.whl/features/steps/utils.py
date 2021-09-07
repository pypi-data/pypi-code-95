# encoding: utf-8
"""
Utilities for web steps.

TODO:
* Add lowering in XPath with translate function
    translate(%s, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸŽŠŒ', 'abcdefghijklmnopqrstuvwxyzàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿžšœ')
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import re
from types import FunctionType

from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, InvalidSelectorException

from klity.klity import TestException


def normalize_for_xpath(value):
    """
    Normalize values for Xpath search.
    """
    if "'" in value:
        values = value.split("'")
        result = "concat("
        for val in values:
            result += "'%s', " % val
            result += '"\'", '
        new_value = result[:-7] + ")"
    else:
        new_value = "'%s'" % value
    return new_value


def normalize_for_css(value):
    """
    Normalize values for CSS search.
    """
    if "'" in value:
        return "'%s'" % value.replace("'", "\\'")
    return "'%s'" % value


def get_first_visible_element(context, elements):
    for element in elements:
        context.klity.trace(f" ID: {element.get_attribute('id')}")
        context.klity.trace(f" displayed: {element.is_displayed()}")
        context.klity.trace(f" class: {element.get_attribute('class').lower()}")
        if element.is_displayed() and not any(
            [
                class_name in element.get_attribute("class").lower()
                for class_name in context.klity.configuration["options"][
                    "hidden_classes"
                ]
            ]
        ):
            return element
    context.klity.trace(f"=> No visible element")


def get_value(context, value):
    """
    Replace possible variables and/or constants in string with their value.
    """
    # Replacing variables
    variables = list(set(re.findall(r"(?<!\\)\$([^$]+)\$", value)))
    context.klity.trace(f"variables: {variables}")
    context.klity.trace(f"known variables: {context.klity.variables}")
    context.klity.trace(f"before => value: {value}")
    for variable in variables:
        value = value.replace(f"${variable}$", context.klity.variables[variable])
    context.klity.trace(f"after => value: {value}")

    # Replacing constants
    constants = list(set(re.findall(r"(?<!\\)#([^#]+)#", value)))
    context.klity.trace(f"constants: {constants}")
    for constant in constants:
        new_value = ""
        what = constant.split("_")[0]
        how = ""
        if "_" in constant:
            how = "_".join(constant.split("_")[1:])
        if what[:4] == "DATE":
            date = datetime.today()
            if len(what) > 4 and what[4] in ("-", "+"):
                date += timedelta(days=int(what[4:]))
            if len(how) > 0:
                new_value = how
                # Replacing year
                for data in ("YEAR", "ANNEE"):
                    new_value = new_value.replace(data, date.strftime("%Y"))
                # Replacing month
                for data in ("MONTH", "MOIS"):
                    new_value = new_value.replace(data, date.strftime("%m"))
                # Replacing day
                for data in ("DAY", "JOUR"):
                    new_value = new_value.replace(data, date.strftime("%d"))
                # Replacing hour
                for data in ("HOUR", "HEURE"):
                    new_value = new_value.replace(data, date.strftime("%H"))
                # Replacing minute
                for data in ("MINUTE",):
                    new_value = new_value.replace(data, date.strftime("%M"))
                # Replacing second
                for data in ("SECOND", "SECONDE"):
                    new_value = new_value.replace(data, date.strftime("%S"))
            else:
                new_value = str(date)
        value = value.replace(f"#{constant}#", str(new_value))
    context.klity.trace(f"=> value: {value}")

    # Replacing escaped characters
    value = value.replace("\$", "$")
    value = value.replace("\#", "#")
    value = value.replace("\\n", "\n")
    context.klity.trace(f"=> final value: {value}")
    return value


@dataclass
class Finder:
    """
    A finder is an object containing a description and a method to find a specific
    element.
    """
    description: str
    find: FunctionType


def find(context, name, finders, visible, value=None, field=None):
    elements = []
    for finder in finders:
        context.klity.trace(f"  {finder.description}")
        try:
            if field is not None:
                elements = finder.find(field, value)
            else:
                elements = finder.find(value)
        except InvalidSelectorException:
            elements = []
        if len(elements) > 0:
            context.klity.trace(f"=> {len(elements)} elements found.")
            if visible:
                # Looking for a visible element only
                context.klity.trace("  Looking for a visible element.")
                element = get_first_visible_element(context, elements)
                if element is not None:
                    return element
            else:
                return elements[0]
    if len(elements) == 0:
        context.klity.trace(f"=> {name} '{value}' not found.")
        raise TestException(context)


def find_button(context, value, visible=True):
    context.klity.trace(f"Looking for button: '{value}'")
    finders = [
        Finder(
            f"Elements with id='{value}'",
            lambda x: context.browser.find_elements_by_id(x),
        ),
        Finder(
            f"Elements with name='{value}'",
            lambda x: context.browser.find_elements_by_name(x),
        ),
        Finder(
            "//*[(self::button or self::input or self::img) "
            f"and normalize-space(.)={normalize_for_xpath(value)}]",
            lambda x: context.browser.find_elements_by_xpath(
                "//*[(self::button or self::input or self::img) "
                f"and normalize-space(.)={normalize_for_xpath(x)}]"
            ),
        ),
        Finder(
            "//*[(self::button or self::input or self::img) "
            f"and contains(.,{normalize_for_xpath(value)})]",
            lambda x: context.browser.find_elements_by_xpath(
                "//*[(self::button or self::input or self::img) "
                f"and contains(.,{normalize_for_xpath(x)})]"
            ),
        ),
        Finder(
            "//*[(self::button or self::input or self::img) "
            f"and normalize-space(@value)={normalize_for_xpath(value)}]",
            lambda x: context.browser.find_elements_by_xpath(
                "//*[(self::button or self::input or self::img) "
                f"and normalize-space(@value)={normalize_for_xpath(x)}]"
            ),
        ),
        Finder(
            "//*[(self::button or self::input or self::img) "
            f"and normalize-space(@title)={normalize_for_xpath(value)}]",
            lambda x: context.browser.find_elements_by_xpath(
                "//*[(self::button or self::input or self::img) "
                f"and normalize-space(@title)={normalize_for_xpath(x)}]"
            ),
        ),
        Finder(
            "//*[self::a "
            f"and normalize-space(@value)={normalize_for_xpath(value)}]",
            lambda x: context.browser.find_elements_by_xpath(
                "//*[self::a "
                f"and normalize-space(@value)={normalize_for_xpath(x)}]"
            ),
        ),
        Finder(
            f"//*[self::a and normalize-space(@title)={normalize_for_xpath(value)}]",
            lambda x: context.browser.find_elements_by_xpath(
                f"//*[self::a and normalize-space(@title)={normalize_for_xpath(x)}]"
            ),
        ),
        Finder(
            f"//*[self::a and normalize-space(.)={normalize_for_xpath(value)}]",
            lambda x: context.browser.find_elements_by_xpath(
                f"//*[self::a and normalize-space(.)={normalize_for_xpath(x)}]"
            ),
        ),
        Finder(
            f"//*[self::a and contains(.,{normalize_for_xpath(value)})]",
            lambda x: context.browser.find_elements_by_xpath(
                f"//*[self::a and contains(.,{normalize_for_xpath(x)})]"
            ),
        ),
        Finder(
            f"//img[@alt={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@alt={normalize_for_xpath(v)}]"
            )
        ),
    ]
    return find(context, "Button", finders, visible, value)


def find_option(context, field, value, visible=True):
    context.klity.trace(f"Looking for selection list option: '{value}'")
    finders = [
        Finder(
            f"//select[@id={normalize_for_xpath(field)}]"
            f"/option[contains(normalize-space(.),{normalize_for_xpath(value)})]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//select[@id={normalize_for_xpath(f)}]"
                f"/option[contains(normalize-space(.),{normalize_for_xpath(v)})]",
            ),
        ),
        Finder(
            f"select[id={normalize_for_css(field)}]"
            f">option[value={normalize_for_css(value)}]",
            lambda f,v: context.browser.find_elements_by_css_selector(
                f"select[id={normalize_for_css(f)}]"
                f">option[value={normalize_for_css(v)}]",
            )
        ),
        Finder(
            f"select[id={normalize_for_css(field)}]"
            f">option[title={normalize_for_css(value)}]",
            lambda f,v: context.browser.find_elements_by_css_selector(
                f"select[id={normalize_for_css(f)}]"
                f">option[title={normalize_for_css(v)}]",
            )
        ),
        Finder(
            f"//select[@name={normalize_for_xpath(field)}]"
            f"/option[contains(normalize-space(.),{normalize_for_xpath(value)})]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//select[@name={normalize_for_xpath(f)}]"
                f"/option[contains(normalize-space(.),{normalize_for_xpath(v)})]",
            ),
        ),
        Finder(
            f"select[name={normalize_for_css(field)}]"
            f">option[value={normalize_for_css(value)}]",
            lambda f,v: context.browser.find_elements_by_css_selector(
                f"select[name={normalize_for_css(f)}]"
                f">option[value={normalize_for_css(v)}]",
            )
        ),
        Finder(
            f"select[name={normalize_for_css(field)}]"
            f">option[title={normalize_for_css(value)}]",
            lambda f,v: context.browser.find_elements_by_css_selector(
                f"select[name={normalize_for_css(f)}]"
                f">option[title={normalize_for_css(v)}]",
            )
        ),
        Finder(
            f"//select/option[@value={normalize_for_xpath(value)}]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//select/option[@value={normalize_for_xpath(v)}]",
            )
        ),
        Finder(
            "//select/option[contains(normalize-space(.),"
            f"{normalize_for_xpath(value)})]",
            lambda f,v: context.browser.find_elements_by_xpath(
                "//select/option[contains(normalize-space(.),"
                f"{normalize_for_xpath(v)})]",
            )
        ),
    ]
    # Trying to find select based on its label without blocking other tests
    try:
        label_for = find_label(context, field, visible).get_attribute("for")
        if label_for is not None:
            finders.insert(0, Finder(
                f"select[id={normalize_for_css(label_for)}]"
                f">option[title={normalize_for_css(value)}]",
                lambda f,v: context.browser.find_elements_by_xpath(
                    f"select[id={normalize_for_css(label_for)}]"
                    f">option[title={normalize_for_css(value)}]",
                ),
            ))
            finders.insert(0, Finder(
                f"select[id={normalize_for_css(label_for)}]"
                f">option[value={normalize_for_css(value)}]",
                lambda f,v: context.browser.find_elements_by_xpath(
                    f"select[id={normalize_for_css(label_for)}]"
                    f">option[value={normalize_for_css(value)}]",
                ),
            ))
            finders.insert(0, Finder(
                f"//select[@id={normalize_for_xpath(label_for)}]"
                f"/option[contains(normalize-space(.),{normalize_for_xpath(value)})]",
                lambda f,v: context.browser.find_elements_by_xpath(
                    f"//select[@id={normalize_for_xpath(label_for)}]"
                    f"/option[contains(normalize-space(.),{normalize_for_xpath(v)})]",
                ),
            ))
    except TestException:
        # No label found
        pass
    return find(context, "Selection list option", finders, visible, value, field)


def find_select(context, field, visible=True):
    context.klity.trace(f"Looking for selection list: '{field}'")
    finders = [
        Finder(
            f"//select[@id={normalize_for_xpath(field)}]",
            lambda f: context.browser.find_elements_by_xpath(
                f"//select[@id={normalize_for_xpath(f)}]",
            ),
        ),
        Finder(
            f"select[id={normalize_for_css(field)}]",
            lambda f: context.browser.find_elements_by_css_selector(
                f"select[id={normalize_for_css(f)}]",
            )
        ),
        Finder(
            f"//select[@name={normalize_for_xpath(field)}]",
            lambda f: context.browser.find_elements_by_xpath(
                f"//select[@name={normalize_for_xpath(f)}]",
            ),
        ),
        Finder(
            f"select[name={normalize_for_css(field)}]",
            lambda f: context.browser.find_elements_by_css_selector(
                f"select[name={normalize_for_css(f)}]",
            )
        ),
    ]
    # Trying to find select based on its label without blocking other tests
    try:
        label_for = find_label(context, field, visible).get_attribute("for")
        if label_for is not None:
            finders.insert(0, Finder(
                f"select[id={normalize_for_css(label_for)}]",
                lambda f: context.browser.find_elements_by_xpath(
                    f"select[id={normalize_for_css(label_for)}]",
                ),
            ))
            finders.insert(0, Finder(
                f"//select[@id={normalize_for_xpath(label_for)}]",
                lambda f: context.browser.find_elements_by_xpath(
                    f"//select[@id={normalize_for_xpath(label_for)}]",
                ),
            ))
    except TestException:
        # No label found
        pass
    return find(context, "Selection list", finders, visible, field)


def find_radio_button(context, field, value, visible=True):
    context.klity.trace(f"Looking for radio button: '{value}'")
    finders = [
        Finder(
            f"//input[@type='radio' and @id={normalize_for_xpath(value)}]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//input[@type='radio' and @id={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            f"//input[@type='radio' and @name={normalize_for_xpath(field)}"
            f" and contains(normalize-space(.),{normalize_for_xpath(value)})]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//input[@type='radio' and @name={normalize_for_xpath(f)}"
                f" and contains(normalize-space(.),{normalize_for_xpath(v)})]",
            ),
        ),
        Finder(
            f"//input[@type='radio' and @name={normalize_for_xpath(field)}"
            f" and @id={normalize_for_xpath(value)}]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//input[@type='radio' and @name={normalize_for_xpath(f)}"
                f" and @id={normalize_for_xpath(v)}]",
            ),
        ),
        Finder(
            f"//input[@type='radio' and @name={normalize_for_xpath(field)}"
            f" and @value={normalize_for_xpath(value)}]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//input[@type='radio' and @name={normalize_for_xpath(f)}"
                f" and @value={normalize_for_xpath(v)}]",
            ),
        ),
        Finder(
            f"//input[@type='radio' and @name={normalize_for_xpath(field)}"
            f" and @value={normalize_for_xpath(value)}]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//input[@type='radio' and @name={normalize_for_xpath(f)}"
                f" and @value={normalize_for_xpath(v)}]",
            ),
        ),
        Finder(
            f"//input[@type='radio' and @name={normalize_for_xpath(value)}]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//input[@type='radio' and @name={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            f"//input[@type='radio' and @value={normalize_for_xpath(value)}]",
            lambda f,v: context.browser.find_elements_by_xpath(
                f"//input[@type='radio' and @value={normalize_for_xpath(v)}]"
            ),
        ),
    ]
    # Trying to find radio button based on its label without blocking other tests
    try:
        label_for = find_label(context, value, visible).get_attribute("for")
        if label_for is not None:
            finders.insert(0, Finder(
                f"Elements with id corresponding to label '{value}'",
                lambda f,v: context.browser.find_elements_by_xpath(
                    f"//*[@id={normalize_for_xpath(label_for)}]"
                ),
            ))
    except TestException:
        # No label found
        pass
    return find(context, "Radio button", finders, visible, value, field)


def find_link(context, value, visible=True):
    context.klity.trace(f"Looking for link: '{value}'")
    finders = [
        Finder(
            f"//a[@id={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//a[@id={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//a[@name={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//a[@name={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//a[@title={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//a[@title={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//a[@alt={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//a[@alt={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//a[contains(normalize-space(.),{normalize_for_xpath(value)})]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//a[contains(normalize-space(.),{normalize_for_xpath(v)})]"
            ),
        ),
        Finder(
            f"//img[@id={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@id={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//img[@name={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@name={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//img[@title={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@title={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//img[@alt={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@alt={normalize_for_xpath(v)}]"
            )
        ),
    ]
    return find(context, "Link", finders, visible, value)


def find_label(context, value, visible=True):
    context.klity.trace(f"Looking for label: '{value}'")
    finders = [
        Finder(
            f"//label[normalize-space(.)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//label[normalize-space(.)={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            f"//label[contains(normalize-space(.),{normalize_for_xpath(value)})]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//label[contains(normalize-space(.),{normalize_for_xpath(v)})]"
            ),
        ),
    ]
    return find(context, "Label", finders, visible, value)


def find_element(context, value, visible=True):
    context.klity.trace(f"Looking for element: '{value}'")
    finders = [
        Finder(
            "//*[not(self::p) and not(self::div) and not(self::li) and"
                f" contains(normalize-space(text()), {normalize_for_xpath(value)})]",
            lambda v: context.browser.find_elements_by_xpath(
                "//*[not(self::p) and not(self::div) and not(self::li) and"
                f" contains(normalize-space(text()), {normalize_for_xpath(v)})]",
            ),
        ),
        Finder(
            f"[id={normalize_for_css(value)}]",
            lambda v: context.browser.find_elements_by_css_selector(
                f"[id={normalize_for_css(v)}]"
            )
        ),
        Finder(
            f"[name={normalize_for_css(value)}]",
            lambda v: context.browser.find_elements_by_css_selector(
                f"[name={normalize_for_css(v)}]"
            )
        ),
        Finder(
            f"[value={normalize_for_css(value)}]",
            lambda v: context.browser.find_elements_by_css_selector(
                f"[value={normalize_for_css(v)}]"
            )
        ),
        Finder(
            f"[title={normalize_for_css(value)}]",
            lambda v: context.browser.find_elements_by_css_selector(
                f"[title={normalize_for_css(v)}]"
            )
        ),
        Finder(
            f"//*[contains(normalize-space(text()), {normalize_for_xpath(value)})]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//*[contains(normalize-space(text()), {normalize_for_xpath(v)})]",
            ),
        ),
    ]
    return find(context, "Field", finders, visible, value)


def find_input(context, value, visible=True):
    context.klity.trace(f"Looking for field: '{value}'")
    finders = [
        Finder(
            f"Elements with id='{value}'",
            lambda v: context.browser.find_elements_by_id(v),
        ),
        Finder(
            f"Elements with name='{value}'",
            lambda v: context.browser.find_elements_by_name(v),
        ),
        Finder(
            "//*[(self::input or self::textarea) and "
            f"normalize-space(.)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//*[(self::input or self::textarea) and "
                f"normalize-space(.)={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            "//*[(self::input or self::textarea) and "
            f"contains(.,{normalize_for_xpath(value)})]",
            lambda v: context.browser.find_elements_by_xpath(
                "//*[(self::input or self::textarea) and "
                f"contains(.,{normalize_for_xpath(v)})]"
            ),
        ),
        Finder(
            "//*[(self::input or self::textarea) and "
            f"normalize-space(@value)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//*[(self::input or self::textarea) and "
                f"normalize-space(@value)={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            "//*[(self::input or self::textarea) and "
            f"normalize-space(@title)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//*[(self::input or self::textarea) and "
                f"normalize-space(@title)={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            "//*[(self::input or self::textarea) and "
            f"normalize-space(@placeholder)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//*[(self::input or self::textarea) and "
                f"normalize-space(@placeholder)={normalize_for_xpath(v)}]"
            ),
        ),
    ]
    # Trying to find input based on its label without blocking other tests
    try:
        label_for = find_label(context, value, visible).get_attribute("for")
        if label_for is not None:
            finders.insert(0, Finder(
                f"Elements with id corresponding to label '{value}'",
                lambda v: context.browser.find_elements_by_xpath(
                    f"//*[@id={normalize_for_xpath(label_for)}]"
                ),
            ))
    except TestException:
        # No label found
        pass
    return find(context, "Field", finders, visible, value)


def find_checkbox(context, value, visible=True):
    context.klity.trace(f"Looking for field: '{value}'")
    finders = [
        Finder(
            "//input[@type='checkbox']"
            f"[normalize-space(@value)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//input[@type='checkbox']"
                f"[normalize-space(@value)={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            "//input[@type='checkbox']"
            f"[normalize-space(@id)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//input[@type='checkbox']"
                f"[normalize-space(@id)={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            "//input[@type='checkbox']"
            f"[normalize-space(@name)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//input[@type='checkbox']"
                f"[normalize-space(@name)={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            "//input[@type='checkbox']"
            f"[normalize-space(@title)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//input[@type='checkbox']"
                f"[normalize-space(@title)={normalize_for_xpath(v)}]"
            ),
        ),
        Finder(
            "//input[@type='checkbox']/parent::*"
            f"[normalize-space(.)={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                "//input[@type='checkbox']/parent::*"
                f"[normalize-space(.)={normalize_for_xpath(v)}]"
            ),
        ),
    ]
    # Trying to find input based on its label without blocking other tests
    try:
        label_for = find_label(context, value, visible).get_attribute("for")
        if label_for is not None:
            finders.insert(0, Finder(
                f"Elements with id corresponding to label '{value}'",
                lambda v: context.browser.find_elements_by_xpath(
                    f"//input[@type='checkbox'][@id={normalize_for_xpath(label_for)}]"
                ),
            ))
    except TestException:
        # No label found
        pass
    return find(context, "Checkbox", finders, visible, value)


def find_submit(context, value=None):
    context.klity.trace(f"Looking for submit input")
    finders = [
        Finder(
            "//input[@type='submit']",
            lambda v: context.browser.find_elements_by_xpath(
                "//input[@type='submit']"
            ),
        ),
    ]
    return find(context, "Submit", finders, True)


def find_recaptcha(context, value=None):
    context.klity.trace(f"Looking for ReCaptcha")
    finders = [
        Finder(
            "//iframe[//label]",
            lambda v: context.browser.find_elements_by_xpath(
                "//iframe[//label]"
            ),
        ),
    ]
    return find(context, "ReCaptcha", finders, True, value)


def find_image(context, value, visible=True):
    context.klity.trace(f"Looking for image: '{value}'")
    finders = [
        Finder(
            f"//img[@id={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@id={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//img[@name={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@name={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//img[@title={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@title={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//img[@alt={normalize_for_xpath(value)}]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[@alt={normalize_for_xpath(v)}]"
            )
        ),
        Finder(
            f"//img[contains(@src,{normalize_for_xpath(value)})]",
            lambda v: context.browser.find_elements_by_xpath(
                f"//img[contains(@src,{normalize_for_xpath(v)})]"
            ),
        ),
    ]
    return find(context, "Image", finders, visible, value)


def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    context.klity.trace(f"=> File {name} not found in {path}.")
    raise TestException(context)


def click(context, element):
    """
    If selenium can't click, let's try with javascript
    """
    if element is not None:
        try:
            element.click()
        except ElementClickInterceptedException:
            try:
                context.browser.execute_script("arguments[0].click();", element)
            except:
                context.klity.trace(f"=> Can't click on {element}.")
                raise TestException(context)


# TODO: This method should be improved
def get_table(context):
    array = {
        "columns": [],
        "lines": [],
    }
    soup = BeautifulSoup(context.browser.page_source, "lxml")
    table = soup.find("table")
    ths = table.find("thead").find_all("th")
    if len(ths) == 0:
        ths = table.find("tr").find_all("th")
    if len(ths) == 0:
        ths = table.find("tr").find_all("td")
    for th in ths:
        array["columns"].append(re.sub("[ \n\t]+", " ", th.text).strip())
    trs = table.find("tbody").find_all("tr")
    if len(trs) == 0:
        trs = table.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        ligne = []
        for td in tds:
            text = re.sub(
                "[ \n\t]+", " ", "".join(["%s" % content for content in td.contents])
            ).strip()
            ligne.append(text)
        array["lines"].append(ligne)

    return array


def type_text(context, text):
    actions = ActionChains(context.browser)
    for character in text:
        context.klity.trace(f"Character {character}")
        if character == "\n":
            actions.send_keys(Keys.RETURN)
        else:
            actions.send_keys(character)
    actions.perform()


# TODO: This function is not used for now...
def paste_from_clipboard(context):
    actions = ActionChains(context.browser)
    actions.send_keys(Keys.SHIFT, Keys.INSERT)
    actions.perform()
