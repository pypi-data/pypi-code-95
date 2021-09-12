#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

import unittest
from pprint import pprint
import sys
from ..letra import Letra
from .test_letra_base import TestLetraBase


class TestLetra(TestLetraBase):
    """
    Pruebas a nivel Letra.
    """

    def test_detecta_titulo(self):
        """
        La letra tiene título solamente, nada de contenido.
        """
        letra = self._letra_lee_archivo("titulo")

        self.assertEqual("Ejemplo de título", letra.titulo)
        self.assertEqual(0, len(letra.secciones))

    def test_detecta_titulo_desfasado(self):
        """
        La letra tiene título solamente, nada de contenido.
        """
        letra = self._letra_lee_archivo("titulo_desfasado")

        self.assertEqual("Ejemplo de título", letra.titulo)
        self.assertEqual(0, len(letra.secciones))

    def test_solo_versos(self):
        """
        La letra solo contiene versos, por lo que no se carga contenido.
        """

        letra = self._letra_lee_archivo("solo_versos")
        self.assertEqual(None, letra.titulo)

    def test_agrega_verso(self):
        """
        La letra tiene título y un verso.
        """
        letra = Letra()

        letra = self._letra_lee_archivo("titulo_y_verso")

        self.assertEqual(len(letra.secciones), 1)
        self.assertEqual(letra.secciones[0].tipo, "verso")

    def test_agrega_dos_versos(self):
        """
        La letra tiene título y dos versos.
        """
        letra = Letra()

        letra = self._letra_lee_archivo("titulo_y_dos_versos")

        self.assertEqual(len(letra.secciones), 2)
        self.assertEqual(letra.secciones[0].tipo, "verso")
        self.assertEqual(letra.secciones[1].tipo, "verso")

    def test_agrega_dos_versos_lineas_vacias(self):
        """
        La letra tiene título y dos versos.
        """
        letra = Letra()

        letra = self._letra_lee_archivo("titulo_y_dos_versos_lineas_vacias")

        self.assertEqual(len(letra.secciones), 2)
        self.assertEqual(letra.secciones[0].tipo, "verso")
        self.assertEqual(letra.secciones[1].tipo, "verso")

    def test_agrega_verso_y_coro(self):
        """
        Letra contiene verso y coro.
        """
        letra = Letra()

        letra = self._letra_lee_archivo("titulo_verso_y_coro")

        self.assertEqual(len(letra.secciones), 2)
        self.assertEqual(letra.secciones[0].tipo, "verso")
        self.assertEqual(letra.secciones[1].tipo, "coro")

    def test_agrega_intro_verso(self):
        """
        La letra tiene título, intro y un verso.
        """
        letra = Letra()

        letra = self._letra_lee_archivo("titulo_intro_verso")

        self.assertEqual(len(letra.secciones), 2)
        self._revisar_tipo_y_lineas(letra.secciones[0], "intro", 1)
        self._revisar_tipo_y_lineas(letra.secciones[1], "verso", 2)

    def test_agrega_verso_coro_y_puente(self):
        """
        Letra contiene verso, coro, y puente.
        """
        letra = Letra()

        letra = self._letra_lee_archivo("titulo_verso_coro_y_puente")

        self.assertEqual(len(letra.secciones), 3)
        self.assertEqual(letra.secciones[0].tipo, "verso")
        self.assertEqual(letra.secciones[1].tipo, "coro")
        self.assertEqual(letra.secciones[2].tipo, "puente")

    def test_agrega_coro_precoro_postcoro(self):
        """
        Letra contiene verso, coro, y puente.
        """
        letra = Letra()

        letra = self._letra_lee_archivo("titulo_coro_precoro_postcoro")

        self.assertEqual(len(letra.secciones), 3)
        self._revisar_tipo_y_lineas(letra.secciones[0], "precoro", 3)
        self._revisar_tipo_y_lineas(letra.secciones[1], "coro", 2)
        self._revisar_tipo_y_lineas(letra.secciones[2], "postcoro", 4)

    def test_agrega_intro_verso_outro(self):
        """
        Letra contiene verso, coro, y puente.
        """
        letra = Letra()

        letra = self._letra_lee_archivo("titulo_intro_verso_outro")

        self.assertEqual(len(letra.secciones), 3)
        self._revisar_tipo_y_lineas(letra.secciones[0], "intro", 3)
        self._revisar_tipo_y_lineas(letra.secciones[1], "verso", 4)
        self._revisar_tipo_y_lineas(letra.secciones[2], "outro", 1)

    def test_cuenta_lineas(self):

        letra = Letra()

        letra = self._letra_lee_archivo("titulo_coro_precoro_postcoro")

        self.assertEqual(letra.cantidad_de_lineas, 9)

    def test_cuenta_palabras(self):

        letra = Letra()

        letra = self._letra_lee_archivo("titulo_coro_precoro_postcoro")

        self.assertEqual(letra.cantidad_de_palabras, 18)

    ###########################################################################
    ### Funciones privadas para cargar los archivos de texto de las letras. ###
    ###########################################################################

    def _letra_lee_archivo(self, nombre_archivo):
        """
        Carga el archivo .me37 en un objeto Letra, mismo que es regresado tras
        leer dicho archivo.
        """

        letra = Letra()
        contenido = self._leer_archivo(nombre_archivo)

        return letra.leer(contenido)


if __name__ == '__main__':
    unittest.main()
