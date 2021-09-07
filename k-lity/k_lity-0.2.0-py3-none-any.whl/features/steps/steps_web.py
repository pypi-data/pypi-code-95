# encoding: utf-8
"""
Web steps
"""

import os
import re
import time

from behave import given, then, when
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from slugify import slugify

from klity.features.steps.utils import *
from klity.klity import TestException


########################################################################################
# Given
########################################################################################
@given(u'que je visite le site "{url}"')
@given(u'que je visite l\'url "{url}"')
def step_impl(context, url):
    url = get_value(context, url)
    context.browser.get(url)


########################################################################################
# When
########################################################################################
@when(u'je clique sur le bouton "{value}"')
@when(u'que je clique sur le bouton "{value}"')
def step_impl(context, value):
    click(context, find_button(context, get_value(context,value)))


@when(u'je clique sur le lien "{value}"')
@when(u'que je clique sur le lien "{value}"')
def step_impl(context, value):
    value = get_value(context, value)
    click(context, find_link(context, value))


@when(u'je clique sur l\'élément contenant "{value}"')
@when(u'que je clique sur l\'élément contenant "{value}"')
def step_impl(context, value):
    value = get_value(context, value)
    click(context, find_element(context, value))


@when(u'je sélectionne la valeur "{value}" du champ "{field}"')
@when(u'que je sélectionne la valeur "{value}" du champ "{field}"')
def step_impl(context, value, field):
    value = get_value(context, value)
    field = get_value(context, field)
    click(context, find_option(context, field, value))


@when(u'je vide le champ "{field}"')
@when(u'que je vide le champ "{field}"')
@when(u'je tape "" dans le champ "{field}"')
@when(u'que je tape "" dans le champ "{field}"')
@when(u'je tape "{value}" dans le champ "{field}"')
@when(u'que je tape "{value}" dans le champ "{field}"')
def step_impl(context, field, value=""):
    element = find_input(context, get_value(context, field))
    if element is not None:
        element.clear()
        element.send_keys("")
        if value != "":
            type_text(context, get_value(context, value))


@when(u'je tape ""')
@when(u'que je tape ""')
@when(u'je tape "{value}"')
@when(u'que je tape "{value}"')
def step_impl(context, value=""):
    value = get_value(context, value)
    if value != "":
        type_text(context, value)


@when(u'je clique sur le bouton radio "{value}"')
@when(u'que je clique sur le bouton radio "{value}"')
def step_impl(context, value):
    value = get_value(context, value)
    element = find_radio_button(context, "", value)
    if not element.is_selected():
        click(context, element)


@when(u'je coche la case à cocher "{value}"')
@when(u'que je coche la case à cocher "{value}"')
def step_impl(context, value):
    value = get_value(context, value)
    element = find_checkbox(context, value)
    if not element.is_selected():
        click(context, element)


@when(u'je décoche la case à cocher "{value}"')
@when(u'que je décoche la case à cocher "{value}"')
def step_impl(context, value):
    value = get_value(context, value)
    element = find_checkbox(context, value)
    if element.is_selected():
        click(context, element)


@when(u'je sélectionne le fichier "{filename}" dans le champ "{field}"')
@when(u'que je sélectionne le fichier "{filename}" dans le champ "{field}"')
def select_file(context, filename, field):
    filename = get_value(context, filename)
    field = get_value(context, field)
    filepath = find_file(filename, os.getcwd())
    if os.path.isfile(filepath):
        element = find_input(context, field)
        element.clear()
        element.send_keys(filepath)


# Testing step
@when(u'je tente le fichier "{filename}"')
@when(u'que je tente le fichier "{filename}"')
def select_file(context, filename):
    filepath = find_file(get_value(context, filename), os.getcwd())
    if os.path.isfile(filepath):
        import pyperclip
        pyperclip.copy(filepath + "\r\n")
        pyperclip.paste()


# Testing step
@when(u'je sélectionne le fichier "{filename}" dans le champ invisible "{field}"')
@when(u'que je sélectionne le fichier "{filename}" dans le champ invisible "{field}"')
def step_impl(context, filename, field):
    filename = get_value(context, filename)
    field = get_value(context, field)
    filepath = find_file(filename, os.getcwd())
    if os.path.isfile(filepath):
        element = find_input(context, field, False)
        element.clear()
        element.send_keys(filepath)


@when(u'j\'attends un élément contenant "{value}"')
@when(u'que j\'attends un élément contenant "{value}"')
def step_impl(context, value):
    value = get_value(context, value)
    start = time.perf_counter()
    timeout = context.klity.configuration["options"]["timeout"]
    while True:
        if (time.perf_counter() - start) > timeout:
            context.klity.trace(f"=> Timeout after {timeout}s")
            raise TestException(context)
        try:
            # Deleting old traces
            context.klity.traces = []
            if find_element(context, value) is not None:
                return
        except TestException:
            time.sleep(0.1)


@when(u'je clique sur le ReCaptcha')
@when(u'que je clique sur le ReCaptcha')
def step_impl(context):
    # Waiting for ReCaptcha
    start = time.perf_counter()
    timeout = context.klity.configuration["options"]["timeout"]
    while True:
        if (time.perf_counter() - start) > timeout:
            context.klity.trace(f"=> Timeout after {timeout}s.")
            raise TestException(context)
        try:
            element = find_recaptcha(context)
            if find_recaptcha(context) is not None:
                click(context, element)
                return
        except TestException:
            time.sleep(0.1)


@when(u'je soumets le formulaire')
@when(u'que je soumets le formulaire')
def step_impl(context):
    click(context, find_submit(context))


########################################################################################
# Then
########################################################################################
@then(u'le titre de la page contient "{text}"')
def step_impl(context, text):
    text = get_value(context, text)
    context.klity.trace(f"Looking for text in title: '{text}'")
    if text not in context.browser.title:
        context.klity.trace(f"  Title: {context.browser.title}")
        context.klity.trace("=> Text not found")
        raise TestException(context)


@then(u'le titre de la page est "{text}"')
def step_impl(context, text):
    text = get_value(context, text)
    context.klity.trace(f"Looking for text in title: '{text}'")
    if text != context.browser.title:
        context.klity.trace(f"  Title: {context.browser.title}")
        context.klity.trace("=> Text not equal")
        raise TestException(context)


@then(u'page contains "{text}"')
@then(u'la page contient "{text}"')
def step_impl(context, text):
    text = get_value(context, text)
    context.klity.trace(f"Looking for text: '{text}'")
    content = re.sub(
        # espace, espace insécable, tabulation et saut de ligne sont convertis
        "[  \n\t]+", " ", BeautifulSoup(context.browser.page_source, "lxml").text
    )
    if bytes(text, "utf-8") not in content.encode("utf-8"):
        context.klity.trace("  Content: %s" % content.encode("utf-8"))
        context.klity.trace("=> Text not found")
        raise TestException(context)


@then(u'la page ne contient pas "{text}"')
def step_impl(context, text):
    text = get_value(context, text)
    context.klity.trace(f"Looking for text: '{text}'")
    content = re.sub(
        "[ \n\t]+", " ", BeautifulSoup(context.browser.page_source, "lxml").text
    )
    if text in content:
        context.klity.trace(f"  Content: {content}")
        context.klity.trace(f"=> Text found")
        raise TestException(context)


@then(u'le titre de l\'élément "{element}" est "{text}"')
def step_impl(context, element, text):
    element = get_value(context, element)
    text = get_value(context, text)
    element = find_element(context, element, False)
    if element.get_attribute("title") != text:
        assert False, "Texte %s non trouvé pour l'élément %s (%s)" % (
            text,
            element,
            element.get_attribute("title"),
        )


@then(u'le titre de l\'élément "{element}" contient "{text}"')
def step_impl(context, element, text):
    element = get_value(context, element)
    text = get_value(context, text)
    element = find_element(context, element, False)
    if text not in element.get_attribute("title"):
        assert False, "Texte %s non trouvé pour l'élément %s (%s)" % (
            text,
            element,
            element.get_attribute("title"),
        )


@then(u'le titre de l\'élément qui contient "{element}" est "{text}"')
def step_impl(context, element, text):
    element = get_value(context, element)
    text = get_value(context, text)
    element = find_element(context, element, False)
    if element.get_attribute("title") != text:
        assert False, "Texte %s non trouvé pour l'élément %s" % (text, element)


@then(u'la page contient un bouton "{value}"')
def step_impl(context, value):
    find_button(context, get_value(context,value))


@then(u'la page contient un lien "{value}"')
@then(u'la page contient un lien "{value}" qui pointe vers "{target}"')
def step_impl(context, value, target=""):
    element = find_link(context, get_value(context,value))
    if target != "":
        href = element.get_attribute("href")
        if target != href:
            context.klity.trace(f"Le lien pointe vers '{target}' au lieu de '{href}'")
            raise TestException(context)


@then(u'la page contient une image "{value}"')
def step_impl(context, value):
    find_image(context, get_value(context,value))


@then(u'la variable "{variable}" vaut "{value}"')
def step_impl(context, variable, value):
    value = get_value(context, value)
    if context.klity.variables[variable] != value:
        context.klity.trace(f"La variable {variable} vaut '{context.klity.variables[variable]}'")
        context.klity.trace(f"La valeur attendue est '{value}'")
        raise TestException(context)


@then(u'la variable "{variable_a}" est égale à la variable "{variable_b}"')
def step_impl(context, variable_a, variable_b):
    if context.klity.variables[variable_a] != context.klity.variables[variable_b]:
        context.klity.trace(f"La variable {variable_a} vaut '{context.klity.variables[variable_a]}'")
        context.klity.trace(f"La variable {variable_b} vaut '{context.klity.variables[variable_b]}'")
        raise TestException(context)


@then(u'la variable "{variable_a}" est différente de la variable "{variable_b}"')
def step_impl(context, variable_a, variable_b):
    if context.klity.variables[variable_a] == context.klity.variables[variable_b]:
        context.klity.trace(f"La variable {variable_a} vaut '{context.klity.variables[variable_a]}'")
        context.klity.trace(f"La variable {variable_b} vaut '{context.klity.variables[variable_b]}'")
        raise TestException(context)


@then(u'la variable "{variable_a}" est inférieure à la variable "{variable_b}"')
def step_impl(context, variable_a, variable_b):
    if context.klity.variables[variable_a] >= context.klity.variables[variable_b]:
        context.klity.trace(f"La variable {variable_a} vaut '{context.klity.variables[variable_a]}'")
        context.klity.trace(f"La variable {variable_b} vaut '{context.klity.variables[variable_b]}'")
        raise TestException(context)


@then(u'la variable "{variable_a}" est supérieure à la variable "{variable_b}"')
def step_impl(context, variable_a, variable_b):
    if context.klity.variables[variable_a] <= context.klity.variables[variable_b]:
        context.klity.trace(f"La variable {variable_a} vaut '{context.klity.variables[variable_a]}'")
        context.klity.trace(f"La variable {variable_b} vaut '{context.klity.variables[variable_b]}'")
        raise TestException(context)


@then(u'le titre du champ "{field}" est "{text}"')
def step_impl(context, field, text):
    text = get_value(context, text)
    field = get_value(context, field)
    element = find_input(context, field, False)
    if element.get_attribute("title") != text:
        context.klity.trace(f"Le titre du champ {field} vaut '{element.get_attribute('title')}'")
        context.klity.trace(f"La valeur attendue est '{text}'")
        raise TestException(context)


@then(u'le champ "{field}" est vide')
@then(u'le champ "{field}" contient "{text}"')
def step_impl(context, field, text=""):
    text = get_value(context, text)
    field = get_value(context, field)
    element = find_input(context, field, False)
    if text != "":
        if text not in element.get_attribute("value"):
            context.klity.trace(f"Le champ {field} contient '{element.get_attribute('value')}'")
            context.klity.trace(f"La valeur attendue est '{text}'")
            raise TestException(context)
    else:
        if element.get_attribute("value") != "":
            context.klity.trace(f"Le champ {field} contient '{element.get_attribute('value')}'")
            context.klity.trace(f"La valeur attendue est vide")
            raise TestException(context)


@then(u'le champ "{field}" ne contient pas "{text}"')
def step_impl(context, field, text=""):
    text = get_value(context, text)
    field = get_value(context, field)
    element = find_input(context, field, False)
    if text in element.get_attribute("value"):
        context.klity.trace(f"Le champ {field} contient '{element.get_attribute('value')}'")
        raise TestException(context)


@then(u'le champ "{field}" n\'est pas vide')
def step_impl(context, field):
    field = get_value(context, field)
    element = find_input(context, field, False)
    if element.get_attribute("value") == "":
        context.klity.trace(f"Le champ {field} est vide")
        raise TestException(context)


@then(u'le champ "{field}" contient "{nombre}" caractères')
def step_impl(context, field, nombre):
    field = get_value(context, field)
    nombre = get_value(context, nombre)
    element = find_input(context, field, False)
    if element.tag_name == "textarea":
        if len(element.text) != int(nombre):
            context.klity.trace(f"Le champ {field} possède {len(element.text)} caractères au lieu de {nombre}")
            raise TestException(context)
    else:
        if len(element.get_attribute("value")) != int(nombre):
            context.klity.trace(f"Le champ {field} possède {element.get_attribute('value')} caractères au lieu de {nombre}")
            raise TestException(context)


@then(u'le champ "{field}" contient moins de "{nombre}" caractères')
def step_impl(context, field, nombre):
    field = get_value(context, field)
    nombre = get_value(context, nombre)
    element = find_input(context, field, False)
    if element.tag_name == "textarea":
        if len(element.text) >= int(nombre):
            context.klity.trace(f"Le champ {field} possède {len(element.text)} caractères, soit plus ou autant que {nombre}")
            raise TestException(context)
    else:
        if len(element.get_attribute("value")) >= int(nombre):
            context.klity.trace(f"Le champ {field} possède {len(element.get_attribute('value'))} caractères, soit plus ou autant que {nombre}")
            raise TestException(context)


@then(u'le champ "{field}" contient plus de "{nombre}" caractères')
def step_impl(context, field, nombre):
    field = get_value(context, field)
    nombre = get_value(context, nombre)
    element = find_input(context, field, False)
    if element.tag_name == "textarea":
        if len(element.text) <= int(nombre):
            context.klity.trace(f"Le champ {field} possède {len(element.text)} caractères, soit moins ou autant que {nombre}")
            raise TestException(context)
    else:
        if len(element.get_attribute("value")) <= int(nombre):
            context.klity.trace(f"Le champ {field} possède {len(element.get_attribute('value'))} caractères, soit moins ou autant que {nombre}")
            raise TestException(context)


@then(u'le champ "{field}" contient entre "{nombre_min}" et "{nombre_max}" caractères')
def step_impl(context, field, nombre_min, nombre_max):
    field = get_value(context, field)
    nombre_min = get_value(context, nombre_min)
    nombre_max = get_value(context, nombre_max)
    # TODO: This part is to be tested
    if element.tag_name == "textarea":
        if not (int(nombre_min) <= len(element.text) <= int(nombre_max)):
            context.klity.trace(f"Le champ {field} possède {len(element.text)} caractères, donc pas entre {nombre_min} et {nombre_max}")
            raise TestException(context)
    else:
        if not (int(nombre_min) <= len(element.get_attribute("value")) <= int(nombre_max)):
            context.klity.trace(f"Le champ {field} possède {len(element.get_attribute('value'))} caractères, donc pas entre {nombre_min} et {nombre_max}")
            raise TestException(context)


@then(u'le champ "{field}" contient l\'option "{value}"')
@then(u'le champ "{field}" contient l\'option ""')
def step_impl(context, field, value=""):
    field = get_value(context, field)
    value = get_value(context, value)
    element = find_option(context, field, value)
    if element is None:
        context.klity.trace(f"Le champ {field} ne contient pas l'option {value}")
        raise TestException(context)


@then(u'le champ "{field}" ne contient pas l\'option "{value}"')
@then(u'le champ "{field}" ne contient pas l\'option ""')
def step_impl(context, field, value=""):
    field = get_value(context, field)
    value = get_value(context, value)
    # For select tag
    try:
        element = find_option(context, field, value)
        if element is not None:
            context.klity.trace(f"Le champ {field} contient l'option {value}")
            raise TestException(context)
    except:
        assert True


@then(u'le champ "{field}" contient "{value}" options')
def step_impl(context, field, value):
    field = get_value(context, field)
    value = get_value(context, value)
    field_size = len(find_select(context, field).find_elements_by_tag_name("option"))
    try:
        value = int(value)
    except:
        context.klity.trace(f"Il semble que {value} ne soit pas un entier.")
        raise TestException(context)
    if value != field_size:
        context.klity.trace(
            f"Le champ {field} contient {field_size} options au lieu de {value}"
        )
        raise TestException(context)


@then(u'l\'option "{value}" du champ "{field}" est sélectionnée')
@then(u'l\'option "" du champ "{field}" est sélectionnée')
def step_impl(context, field, value=""):
    field = get_value(context, field)
    value = get_value(context, value)
    # For select tag
    try:
        element = find_option(context, field, value)
    except:
        # For radio button
        element = find_radio_button(context, field, value, False)
    if not element.is_selected():
        context.klity.trace(f"L'option {value} du champ {field} n'est pas sélectionnée")
        raise TestException(context)


@then(u'la case à cocher "{field}" est cochée')
def step_impl(context, field):
    field = get_value(context, field)
    element = find_checkbox(context, field, False)
    if element is None:
        context.klity.trace(f"La case à cocher {field} n'a pas été trouvée")
        raise TestException(context)
    if not element.is_selected():
        context.klity.trace(f"La case à cocher {field} n'est pas cochée")
        raise TestException(context)


@then(u'la case à cocher "{field}" n\'est pas cochée')
@then(u'la case à cocher "{field}" est décochée')
def step_impl(context, field):
    field = get_value(context, field)
    element = find_checkbox(context, field, False)
    if element is None:
        context.klity.trace(f"La case à cocher {field} n'a pas été trouvée")
        raise TestException(context)
    if element.is_selected():
        context.klity.trace(f"La case à cocher {field} est cochée")
        raise TestException(context)


@then(u'je clique sur le bouton "{value}"')
def step_impl(context, value):
    value = get_value(context, value)
    click(context, find_button(context, value, False))


@then(u'je clique sur le lien "{value}"')
def step_impl(context, value):
    value = get_value(context, value)
    click(context, find_link(context, value, False))


@then(u'un élément contenant "{value}" existe')
def step_impl(context, value):
    element = find_element(context, get_value(context, value))
    if element is None:
        context.klity.trace(f"L'élément {value} n'existe pas ou n'est pas visible.")
        raise TestException(context)


@then(u'un élément contenant "{value}" n\'existe pas')
def step_impl(context, value):
    try:
        element = find_element(context, get_value(context, value))
    except:
        pass
    else:
        if element is not None:
            context.klity.trace(f"L'élément {value} existe et est visible.")
            raise TestException(context)


@then(u'le champ "{field}" existe')
def step_impl(context, field):
    field = get_value(context, field)
    try:
        element = find_input(context, field, False)
    except:
        context.klity.trace(f"Le champ {field} n'existe pas.")
        raise TestException(context)
    if element is None:
        context.klity.trace(f"Le champ {field} n'existe pas.")
        raise TestException(context)


@then(u'le champ "{field}" n\'existe pas')
def step_impl(context, field):
    field = get_value(context, field)
    try:
        element = find_input(context, field, False)
    except:
        pass
    else:
        if element is not None:
            context.klity.trace(f"Le champ {field} existe et est visible.")
            raise TestException(context)


@then(u'le tableau contient "{nombre}" colonnes')
def step_impl(context, nombre):
    tableau = get_table(context)
    if tableau is None:
        assert False, "Tableau non trouvé"

    nombre = get_value(context, nombre)
    if len(tableau["colonnes"]) == int(nombre):
        assert True
    else:
        assert False, "Le tableau contient %d colonnes au lieu de %d" % (
            len(tableau["colonnes"]),
            int(nombre),
        )


@then(u'le tableau contient "{nombre}" lignes')
def step_impl(context, nombre):
    tableau = get_table(context)
    if tableau is None:
        assert False, "Tableau non trouvé"

    nombre = get_value(context, nombre)
    if len(tableau["lignes"]) == int(nombre):
        assert True
    else:
        assert False, "Le tableau contient %d lignes au lieu de %d" % (
            len(tableau["lignes"]),
            int(nombre),
        )


@then(u'le tableau contient moins de "{nombre}" lignes')
def step_impl(context, nombre):
    tableau = get_table(context)
    if tableau is None:
        assert False, "Tableau non trouvé"

    nombre = get_value(context, nombre)
    if len(tableau["lignes"]) <= int(nombre):
        assert True
    else:
        assert False, "Le tableau contient %d lignes au lieu de moins de %d" % (
            len(tableau["lignes"]),
            int(nombre),
        )


@then(u'la ligne "{index}" de la colonne "{colonne}" du tableau contient "{value}"')
@then(u'la ligne "{index}" de la colonne "{colonne}" du tableau contient ""')
@then(u'la ligne "{index}" de la colonne "{colonne}" du tableau est vide')
def step_impl(context, index, colonne, value=""):
    tableau = get_table(context)
    if tableau is None:
        assert False, "Tableau non trouvé"

    index = int(get_value(context, index)) - 1
    colonne = get_value(context, colonne)
    value = get_value(context, value)
    try:
        col_index = tableau["colonnes"].index(colonne)
    except:
        assert False, "La colonne %s n'existe pas dans le tableau" % colonne

    if len(tableau["lignes"]) <= index:
        assert False, (
            "Le numéro de ligne est trop grand pour le tableau. Celui-ci ne contient que %d lignes"
            % len(tableau["lignes"])
        )

    if tableau["lignes"][index][col_index] != value:
        assert False, "La cellule (%d,%d) du tableau contient %s au lieu de %s" % (
            index + 1,
            col_index,
            tableau["lignes"][index][col_index],
            value,
        )


@then(u'la ligne "{index}" de la colonne "{colonne}" du tableau n\'est pas vide')
def step_impl(context, index, colonne):
    tableau = get_table(context)
    if tableau is None:
        assert False, "Tableau non trouvé"

    index = int(get_value(context, index)) - 1
    colonne = get_value(context, colonne)
    try:
        col_index = tableau["colonnes"].index(colonne)
    except:
        assert False, "La colonne %s n'existe pas dans le tableau" % colonne

    if len(tableau["lignes"]) <= index:
        assert False, (
            "Le numéro de ligne est trop grand pour le tableau. Celui-ci ne contient que %d lignes"
            % len(tableau["lignes"])
        )

    if tableau["lignes"][index][col_index] == "":
        assert False, "La cellule (%d,%d) du tableau n'est pas vide et contient %s" % (
            index + 1,
            col_index,
            tableau["lignes"][index][col_index],
        )


@then(u'la colonne "{colonne}" du tableau est triée dans l\'ordre {order}')
def step_impl(context, colonne, order):
    tableau = get_table(context)
    if tableau is None:
        assert False, "Tableau non trouvé"

    colonne = get_value(context, colonne)
    order = get_value(context, order)
    if order not in (
        "croissant",
        "décroissant",
        "decroissant",
        "alphabétique",
        "alphabétique inverse",
        "alphabetique",
        "alphabetique inverse",
    ):
        raise NotImplementedError
    try:
        col_index = tableau["colonnes"].index(colonne)
    except:
        assert False, "La colonne %s n'existe pas dans le tableau" % colonne
    # Getting values of specified column
    ligne = []
    for i in range(len(tableau["lignes"])):
        ligne.append(slugify(tableau["lignes"][i][col_index]).replace("-", ""))
    if order in ("croissant", "alphabétique", "alphabetique"):
        if not all(ligne[i] <= ligne[i + 1] for i in range(len(ligne) - 1)):
            old_item = ligne[0]
            for item in ligne:
                if old_item > item:
                    print("%s > %s" % (old_item, item))
                old_item = item
            assert False, "Le contenu de la colonne %s n'est pas dans l'ordre %s" % (
                colonne,
                order,
            )
    else:
        if not all(ligne[i] >= ligne[i + 1] for i in range(len(ligne) - 1)):
            old_item = ligne[0]
            for item in ligne:
                if old_item < item:
                    print("%s < %s" % (old_item, item))
                old_item = item
            assert False, "Le contenu de la colonne %s n'est pas dans l'ordre %s" % (
                colonne,
                order,
            )


@then(u'le bouton "{value}" existe')
def step_impl(context, value):
    value = get_value(context, value)
    element = find_button(context, value)
    assert element is not None


@then(u'le bouton "{value}" n\'existe pas')
def step_impl(context, value):
    value = get_value(context, value)
    try:
        find_button(context, value)
    except AssertionError:
        assert True
