#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

# TODO: Transformar a HTML, LaTeX, PDF, Markdown, reST, Messenger, y plano.

from marke37.seccion import Seccion

class Letra:
    _diccionario = None

    def __init__(self):

        self._titulo_provisional = None
        self._titulo = None

        self._seccion_actual = None

        self.secciones = []

        # Arreglar diccionario.
        if self._diccionario and "Linea" in self._diccionario:
            dicc = self._diccionario["Linea"]
            if "Seccion" not in self._diccionario:
                self._diccionario["Seccion"] = {}

            self._diccionario["Seccion"]["Linea"] = dicc

    def leer(self, letra):
        """
        Lee la letra completa, una cadena que proviene de un archivo.
        """

        for linea in letra.split('\n'):
            self.agregar_linea(linea)

        return self

    def agregar_linea(self, linea):
        """
        Agregar la línea, escogiendo la sección.
        """

        # Primero, descartamos las líneas que son comentario.
        if len(linea) > 0 and linea[0] == '%':
            return

        # Sigo buscando título, así que no entro en sección.
        if self._titulo is None:
            self._buscar_titulo(linea)
            return

        # Si es un salto de línea, lo usamos para cerrar sección.
        if len(linea.strip()) == 0:
            if self._hay_seccion_abierta():
                self._seccion_actual.cerrar()

            self._seccion_actual = None

            return

        # En este punto ya tenemos título y hemos eliminado los comentarios,
        # y ya se procesaron los saltos de línea.
        if self._seccion_actual is None:
            self._crear_seccion()

        self._seccion_actual.agregar_linea(linea)

    @property
    def titulo(self):
        """
        Regresa el título de la letra, sin adiciones de contenedor.
        """

        return self._titulo

    @property
    def cantidad_de_lineas(self):
        cantidad = 0

        for s in self.secciones:
            cantidad = cantidad + s.cantidad_de_lineas

        return cantidad

    @property
    def cantidad_de_palabras(self):
        cantidad = 0

        for s in self.secciones:
            cantidad = cantidad + s.cantidad_de_palabras

        return cantidad

    def imprimir(self):

        cadena = self._imprimir_contenedor_inicio()

        cadena += self._imprimir_titulo()

        primera_seccion = True
        for seccion in self.secciones:
            if primera_seccion:
                primera_seccion = False
            else:
                if self._diccionario and "Letra" in self._diccionario and "EspacioEntreSecciones" in self._diccionario["Letra"]:
                    cadena += self._diccionario["Letra"]["EspacioEntreSecciones"]

            if not seccion.esta_cerrada:
                seccion.cerrar()

            cadena += seccion.imprimir()

        cadena += self._imprimir_contenedor_fin()

        return cadena

    def _imprimir_contenedor_inicio(self):
        contenedor = ""

        if not self._diccionario:
            return contenedor

        if "Letra" not in self._diccionario:
            return contenedor

        if "ContenedorInicio" not in self._diccionario["Letra"]:
            return contenedor

        return self._diccionario["Letra"]["ContenedorInicio"] + "\n"

    def _imprimir_contenedor_fin(self):
        contenedor = ""

        if not self._diccionario:
            return contenedor

        if "Letra" not in self._diccionario:
            return contenedor

        if "ContenedorFin" not in self._diccionario["Letra"]:
            return contenedor

        return self._diccionario["Letra"]["ContenedorFin"] + "\n"

    def _imprimir_titulo(self):
        if not self._titulo:
            return ""

        titulo = '<h1 class="titulo">\n'
        titulo += self._titulo + "\n"
        titulo += "</h1>\n"

        if not self._diccionario:
            return titulo

        if "Titulo" not in self._diccionario:
            return titulo

        # Si ya se encontró el nodo de "Titulo", entonces proceder con las
        # sustituciones, sean las que sean.
        titulo = ""
        if "LineaAnterior" in self._diccionario["Titulo"]:
            titulo += self._diccionario["Titulo"]["LineaAnterior"] + "\n"

        if "Apertura" in self._diccionario["Titulo"]:
            titulo += self._diccionario["Titulo"]["Apertura"]

        titulo += self._titulo

        if "Clausura" in self._diccionario["Titulo"]:
            titulo += self._diccionario["Titulo"]["Clausura"]

        titulo += "\n"

        if "LineaPosterior" in self._diccionario["Titulo"]:
            titulo += self._diccionario["Titulo"]["LineaPosterior"] + "\n"

        return titulo

    def _crear_seccion(self):

        diccionario_de_seccion = None

        if self._diccionario and "Seccion" in self._diccionario:
            diccionario_de_seccion = self._diccionario["Seccion"]

        self._seccion_actual = Seccion(diccionario=diccionario_de_seccion)
        self.secciones.append(self._seccion_actual)

    def _hay_seccion_abierta(self):
        if self._seccion_actual is None:
            return False

        return not self._seccion_actual.esta_cerrada


    def _buscar_titulo(self, linea):
        if linea.startswith("==="):
            self._titulo = self._titulo_provisional
            return

        self._titulo_provisional = linea
