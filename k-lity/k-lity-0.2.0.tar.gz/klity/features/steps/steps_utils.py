# encoding: utf-8
"""
TODO: Translation work to do...
"""

import os
import re
import time
from datetime import datetime

from behave import step, then, when

from klity.features.steps.utils import find_input, get_value
from klity.klity import TestException


########################################################################################
# STEP
########################################################################################
@step(u"j'attends {second} secondes")
@step(u"j'attends {second} seconde")
@step(u"que j'attends {second} secondes")
@step(u"que j'attends {second} seconde")
def step_impl(context, second):
    time.sleep(float(second))


@step(u"je fais un screenshot")
@step(u'je fais un screenshot sous le nom "{name}"')
@step(u"je fais une capture d'écran")
@step(u'je fais une capture d\'écran sous le nom "{name}"')
@step(u"que je fais un screenshot")
@step(u'que je fais un screenshot sous le nom "{name}"')
@step(u"que je fais une capture d'écran")
@step(u'que je fais une capture d\'écran sous le nom "{name}"')
def step_impl(context, name=None):
    if name is None:
        name = "%s" % datetime.utcnow().strftime("%Y%m%d_%H%M%S%f")
    name = get_value(context, name)
    file_path = os.path.join("screenshots", os.path.dirname(name))
    os.makedirs(file_path, exist_ok=True)
    context.browser.save_screenshot(
        os.path.join(file_path, f"{os.path.basename(name)}.png")
    )


@step(u'j\'assigne la valeur "{value}" à la variable "{variable}"')
@step(u'que j\'assigne la valeur "{value}" à la variable "{variable}"')
def step_impl(context, value, variable):
    variable = get_value(context, variable)
    context.klity.variables[variable] = get_value(context, value)
    context.klity.trace(f"Variables: {context.klity.variables}")


@step(u'j\'assigne la valeur du champ "{field}" à la variable "{variable}"')
@step(u'que j\'assigne la valeur du champ "{field}" à la variable "{variable}"')
def step_impl(context, field, variable):
    variable = get_value(context, variable)
    field = get_value(context, field)
    context.klity.variables[variable] = find_input(context,field).get_attribute("value")
    context.klity.trace(f"Variables: {context.klity.variables}")


@step(u'j\'exécute la requête "{request}"')
@step(u'que j\'exécute la requête "{request}"')
@step(u'j\'exécute la requête "{request}" avec le paramètre "{parameters}"')
@step(u'que j\'exécute la requête "{request}" avec le paramètre "{parameters}"')
@step(u'j\'exécute la requête "{request}" avec les paramètres "{parameters}"')
@step(u'que j\'exécute la requête "{request}" avec les paramètres "{parameters}"')
def step_impl(context, request, parameters=None):
    request = get_value(context, request)
    if request not in context.klity.requests:
        context.klity.trace(f"Requête '{request}' non trouvée")
        raise TestException(context)
    if parameters:
        # Parameters are separated by comma
        parameters = re.split(r"(?<!\\),", parameters)
        # Get values of parameters
        for idx, parameter in enumerate(parameters):
            parameters[idx] = get_value(context, parameter)
        context.klity.trace(f"Paramètres: {parameters}")
    try:
        result = context.klity.execute(request, parameters)
        context.klity.trace(result)
    except IndexError:
        context.klity.trace(f"Nombre de paramètres incorrect: {len(parameters)}")
        raise TestException(context)


@step(u'j\'assigne le résultat de la requête "{request}" à la variable "{variable}"')
@step(
    u'que j\'assigne le résultat de la requête "{request}" à la variable "{variable}"'
)
@step(
    u'j\'assigne le résultat de la requête "{request}" avec le paramètre "{parameters}" à la variable "{variable}"'
)
@step(
    u'que j\'assigne le résultat de la requête "{request}" avec le paramètre "{parameters}" à la variable "{variable}"'
)
@step(
    u'j\'assigne le résultat de la requête "{request}" avec les paramètres "{parameters}" à la variable "{variable}"'
)
@step(
    u'que j\'assigne le résultat de la requête "{request}" avec les paramètres "{parameters}" à la variable "{variable}"'
)
def step_impl(context, request, variable, parameters=None):
    request = get_value(context, request)
    if request not in context.klity.requests:
        context.klity.trace(f"Requête '{request}' non trouvée")
        raise TestException(context)
    if parameters:
        # parameters are separated by comma
        parameters = re.split(r"(?<!\\),", parameters)
        # Get values of parameters
        for idx, parameter in enumerate(parameters):
            parameters[idx] = get_value(context, parameter)
        context.klity.trace(f"Paramètres: {parameters}")
    try:
        result = context.klity.execute(request, parameters)
        context.klity.trace(result)
    except IndexError:
        context.klity.trace(f"Nombre de paramètres incorrect: {len(parameters)}")
        raise TestException(context)
    context.klity.variables[variable] = result["results"][0][0]
    context.klity.trace(f"Variables: {context.klity.variables}")


@step(u'le résultat de la requête "{request}" est vide')
@step(u'que le résultat de la requête "{request}" est vide')
@step(u'le résultat de la requête "{request}" avec le paramètre "{parameters}" est vide')
@step(u'que le résultat de la requête "{request}" avec le paramètre "{parameters}" est vide')
@step(u'le résultat de la requête "{request}" avec les paramètres "{parameters}" est vide')
@step(u'que le résultat de la requête "{request}" avec les paramètres "{parameters}" est vide')
@step(u'le résultat de la requête "{request}" contient "{text}"')
@step(u'que le résultat de la requête "{request}" contient "{text}"')
@step(u'le résultat de la requête "{request}" avec le paramètre "{parameters}" contient "{text}"')
@step(u'que le résultat de la requête "{request}" avec le paramètre "{parameters}" contient "{text}"')
@step(u'le résultat de la requête "{request}" avec les paramètres "{parameters}" contient "{text}"')
@step(u'que le résultat de la requête "{request}" avec les paramètres "{parameters}" contient "{text}"')
def step_impl(context, request, parameters=None, text=""):
    request = get_value(context, request)
    if request not in context.klity.requests:
        context.klity.trace(f"Requête '{request}' non trouvée")
        raise TestException(context)
    if parameters:
        # parameters are separated by comma
        parameters = re.split(r"(?<!\\),", parameters)
        # Get values of parameters
        for idx, parameter in enumerate(parameters):
            parameters[idx] = get_value(context, parameter)
        context.klity.trace(f"Paramètres: {parameters}")
    try:
        result = context.klity.execute(request, parameters)
        context.klity.trace(result)
    except IndexError:
        context.klity.trace(f"Nombre de paramètres incorrect: {len(parameters)}")
        raise TestException(context)
    # TODO : Should be able to manage multiple columns
    column = result["results"][0][0]
    if text == "":
        if column is not None:
            if column != "":
                context.klity.trace(f"La requête n'est pas vide : {column}")
                raise TestException(context)
    else:
        if column is None or text not in str(column):
            context.klity.trace(f"Texte '{text}' non trouvé dans '{column}'")
            raise TestException(context)


@step(u'le résultat de la requête "{request}" n\'est pas vide')
@step(u'que le résultat de la requête "{request}" n\'est pas vide')
@step(u'le résultat de la requête "{request}" avec le paramètre "{parameters}" n\'est pas vide')
@step(u'que le résultat de la requête "{request}" avec le paramètre "{parameters}" n\'est pas vide')
@step(u'le résultat de la requête "{request}" avec les paramètres "{parameters}" n\'est pas vide')
@step(u'que le résultat de la requête "{request}" avec les paramètres "{parameters}" n\'est pas vide')
def step_impl(context, request, parameters=None):
    request = get_value(context, request)
    if request not in context.klity.requests:
        context.klity.trace(f"Requête '{request}' non trouvée")
        raise TestException(context)
    if parameters:
        # parameters are separated by comma
        parameters = re.split(r"(?<!\\),", parameters)
        # Get values of parameters
        for idx, parameter in enumerate(parameters):
            parameters[idx] = get_value(context, parameter)
        context.klity.trace(f"Paramètres: {parameters}")
    try:
        result = context.klity.execute(request, parameters)
        context.klity.trace(result)
    except IndexError:
        context.klity.trace(f"Nombre de paramètres incorrect: {len(parameters)}")
        raise TestException(context)
    result = str(result["results"][0][0])
    if result is None or result == "":
        context.klity.trace("La requête est vide.")
        raise TestException(context)
