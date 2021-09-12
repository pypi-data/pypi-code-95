#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

from marke37.linea import Linea
from marke37.seccion import Seccion
from marke37.letra import Letra

class LetraIM(Letra):
    _diccionario = {
        "Letra": {
            "EspacioEntreSecciones": "",
        },
        "Titulo": {
            "Apertura": "```",
            "Clausura": "```",
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
                Seccion.INICIO_CORO: "",
                Seccion.INICIO_PUENTE: "",
                Seccion.INICIO_INTRO: "",
                Seccion.INICIO_OUTRO: "",
                Seccion.INICIO_PRECORO: "",
                Seccion.INICIO_POSTCORO: "",
                "LineaVerso": "",
                "LineaCoro": "*",
                "LineaPrecoro": "*",
                "LineaPostcoro": "*",
                "LineaPuente": "_",
                "LineaIntro": "_*",
                "LineaOutro": "*_",
            },
            "Clausura": {
                "[/VERSO]": None,
                Seccion.FIN_CORO: None,
                Seccion.FIN_PUENTE: None,
                Seccion.FIN_INTRO: None,
                Seccion.FIN_OUTRO: None,
                Seccion.FIN_PRECORO: None,
                Seccion.FIN_POSTCORO: None,
                "LineaVerso": "",
                "LineaCoro": "*",
                "LineaPrecoro": "*",
                "LineaPostcoro": "*",
                "LineaPuente": "_",
                "LineaIntro": "*_",
                "LineaOutro": "_*",
            },
        }
    }