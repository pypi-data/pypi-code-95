#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

from .linea import Linea
from .seccion import Seccion
from .letra import Letra

class LetraIM_HTML(Letra):
    _diccionario = {
        "Letra": {
            "ContenedorInicio": '<div class="letra-im-html">',
            "ContenedorFin": '</div>',
            "EspacioEntreSecciones": "<br>\n",
        },
        "Titulo": {
            "Apertura": '<h1 class="titulo">```',
            "Clausura": '```</h1>',
            "LineaPosterior": "<br>"
        },
        "Linea": {
                "Apertura": {
                    Linea.GRITOS: '<span class="gritos">',
                    Linea.SEGUNDA_VOZ: '<span class="segunda-voz">',
                    Linea.TERCERA_VOZ: '<span class="tercera-voz">',
                },
                "Clausura": {
                    Linea.GRITOS_C: '</span>',
                    Linea.SEGUNDA_VOZ_C: '</span>',
                    Linea.TERCERA_VOZ_C: '</span>',
                },
                "SaltoDeLinea": "<br>"
            },
        "Seccion": {
            "Apertura": {
                "[VERSO]": '<div class="seccion seccion-verso">',
                Seccion.INICIO_CORO: '<div class="seccion seccion-coro">',
                Seccion.INICIO_PUENTE: '<div class="seccion seccion-puente">',
                Seccion.INICIO_INTRO: '<div class="seccion seccion-intro">',
                Seccion.INICIO_OUTRO: '<div class="seccion seccion-outro">',
                Seccion.INICIO_PRECORO: '<div class="seccion seccion-precoro">',
                Seccion.INICIO_POSTCORO: '<div class="seccion seccion-postcoro">',
                "LineaVerso": "",
                "LineaCoro": "*",
                "LineaPrecoro": "*",
                "LineaPostcoro": "*",
                "LineaPuente": "_",
                "LineaIntro": "_*",
                "LineaOutro": "*_",
            },
            "Clausura": {
                "[/VERSO]": '</div>',
                Seccion.FIN_CORO: '</div>',
                Seccion.FIN_PUENTE: '</div>',
                Seccion.FIN_INTRO: '</div>',
                Seccion.FIN_OUTRO: '</div>',
                Seccion.FIN_PRECORO: '</div>',
                Seccion.FIN_POSTCORO: '</div>',
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