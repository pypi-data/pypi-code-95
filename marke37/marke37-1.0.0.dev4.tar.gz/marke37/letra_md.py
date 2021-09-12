#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

from marke37.linea import Linea
from marke37.seccion import Seccion
from marke37.letra import Letra

class LetraMarkdown(Letra):
    _diccionario = {
        "Titulo": {
            "Apertura": "# ",
            "Clausura": "",
        },
        "Linea": {
                "Apertura": {
                    Linea.GRITOS: "",
                    Linea.SEGUNDA_VOZ: "",
                    Linea.TERCERA_VOZ: "",
                },
                "Clausura": {
                    Linea.GRITOS_C: "",
                    Linea.SEGUNDA_VOZ_C: "",
                    Linea.TERCERA_VOZ_C: "",
                },
                "SaltoDeLinea": ""
            },
        "Seccion": {
            "Apertura": {
                "[VERSO]": "",
                Seccion.INICIO_CORO: "**",
                Seccion.INICIO_PUENTE: "_",
                Seccion.INICIO_INTRO: "_**",
                Seccion.INICIO_OUTRO: "**_",
                Seccion.INICIO_PRECORO: "**",
                Seccion.INICIO_POSTCORO: "**",
            },
            "Clausura": {
                "[/VERSO]": "",
                Seccion.FIN_CORO: "**",
                Seccion.FIN_PUENTE: "_",
                Seccion.FIN_INTRO: "**_",
                Seccion.FIN_OUTRO: "_**",
                Seccion.FIN_PRECORO: "**",
                Seccion.FIN_POSTCORO: "**",
            },
        }
    }