#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

import unittest
from pprint import pprint
from ..letra_latex import LetraLaTeX
from .test_letra_base import TestLetraBase


class TestLetraLaTeX(TestLetraBase):
    def test_letra_latex_se_puede_instanciar(self):
        letra = LetraLaTeX()

        self.assertTrue(1)

    def test_con_verso(self):
        letra = LetraLaTeX()

        letra.agregar_linea("Título")
        letra.agregar_linea("======")

        letra.agregar_linea("Verso")

        self.assertTrue(1)

    def test_con_gritos(self):
        letra = LetraLaTeX()

        letra.agregar_linea("Título")
        letra.agregar_linea("======")

        letra.agregar_linea("Verso |gritando| mucho.")

    def test_con_verso(self):
        letra = LetraLaTeX()

        letra.agregar_linea("Título")
        letra.agregar_linea("======")

        letra.agregar_linea("Verso")
        letra.agregar_linea("")
        letra.agregar_linea("**Coro")

        self.assertTrue(1)


if __name__ == '__main__':
    unittest.main()
