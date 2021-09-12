#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

import unittest

class TestLetraBase(unittest.TestCase):
    def _revisar_tipo_y_lineas(self, seccion, tipo, num_lineas):
        """
        Revisa el tipo de una sección.
        """

        self.assertEqual(seccion.tipo, tipo)
        self.assertEqual(len(seccion.lineas), num_lineas)

    def _leer_archivo(self, nombre_archivo):
        """
        Lee un archivo .me37 para usar como prueba.
        """
        letra = open("marke37/test/archivos/" + nombre_archivo + ".me37", "r")
        contenido = letra.read()
        letra.close()

        return contenido