#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

import os
from .letra import Letra
from .letra_latex import LetraLaTeX

class Marke37:
    """
    Esta clase transforma un archivo de Marke37 a diversos formatos.
    En caso de no especificar, el formato predeterminado es "html".

    Los formatos disponibles son:
        html   genera el html de la letra, solo contendedores y clases.
        pagina genera toda la página de html lista para ser mostrada en
               el navegador, utilizando una plantilla con HTML y CSS.
        latex  genera el código LaTeX con entornos e instrucciones que
               pueden ser definidas por el usuario, para su posterior
               compilación a PDF.
        pdf    esta opción genera el pdf de la letra, utilizando latex
               como intermedio.
    """

    def __init__(self):

        pass

    def convertir(self, archivo, formato="html"):
        letra = None

        if formato == "latex":
            letra = LetraLaTeX()

        if letra is None or formato == "html":
            letra = Letra()

        archivo = open(archivo, "r")
        texto_letra = archivo.read()

        for linea in texto_letra.split("\n"):
            letra.agregar_linea(linea)

        if formato == "pagina":
            return self._convertir_a_pagina(letra)

        return letra.imprimir()

    def _convertir_a_pagina(self, letra):
        """
        Esta conversión tiene implícita una conversión a HTML, que luego se
        reemplaza dentro de una página completa de HTML5, con hoja de estilo.
        """

        texto = ""

        nombre_plantilla = os.path.abspath(os.path.dirname(__file__)) + "/plantillas/html/bulma.html"

        archivo_plantilla = open(nombre_plantilla, "r")
        texto_plantilla = archivo_plantilla.read()

        texto = texto_plantilla.replace("{% titulo %}", letra.titulo)
        texto = texto.replace("{% bloque %}", letra.imprimir())

        return texto

    def _convertir_a_pdf(self, letra):
        """
        Esta conversión agrega el código suficiente para generar un
        documento autocontenido en PDF de la letra, tomando el código
        LaTeX como base.
        """

        pass
