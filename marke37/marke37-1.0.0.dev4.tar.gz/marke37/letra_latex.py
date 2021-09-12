#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

# TODO:
# + Reemplazo de comillas dobles.
# + Reemplazo de comillas simples.

from .linea import Linea
from .seccion import Seccion
from .letra import Letra

class LetraLaTeX(Letra):
    _diccionario = {
        "Letra": {
            "ContenedorInicio": "\\begin{letra}\n",
            "ContenedorFin": "\n\\end{letra}",
            "EspacioEntreSecciones": "\\ees\n",
        },
        "Titulo": {
            "Apertura": "\\titulo{",
            "Clausura": "}",
            "LineaPosterior": ""
        },
        "Linea": {
                "Apertura": {
                    Linea.GRITOS: "\\gritos{",
                    Linea.SEGUNDA_VOZ: "\\segundavoz{",
                    Linea.TERCERA_VOZ: "\\terceravoz{",
                },
                "Clausura": {
                    Linea.GRITOS_C: "}",
                    Linea.SEGUNDA_VOZ_C: "}",
                    Linea.TERCERA_VOZ_C: "}",
                },
                "SaltoDeLinea": "\\eel"
            },
        "Seccion": {
            "Apertura": {
                "[VERSO]": "\\begin{verso}",
                Seccion.INICIO_CORO: "\\begin{coro}",
                Seccion.INICIO_PUENTE: "\\begin{puente}",
                Seccion.INICIO_INTRO: "\\begin{intro}",
                Seccion.INICIO_OUTRO: "\\begin{outro}",
                Seccion.INICIO_PRECORO: "\\begin{precoro}",
                Seccion.INICIO_POSTCORO: "\\begin{postcoro}",
            },
            "Clausura": {
                "[/VERSO]": "\\end{verso}",
                Seccion.FIN_CORO: "\\end{coro}",
                Seccion.FIN_PUENTE: "\\end{puente}",
                Seccion.FIN_INTRO: "\\end{intro}",
                Seccion.FIN_OUTRO: "\\end{outro}",
                Seccion.FIN_PRECORO: "\\end{precoro}",
                Seccion.FIN_POSTCORO: "\\end{postcoro}",
            },
        }
    }