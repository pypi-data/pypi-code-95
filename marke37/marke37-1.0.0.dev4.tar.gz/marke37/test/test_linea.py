#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

import unittest
from pprint import pprint
import sys
sys.path.insert(0, '../')
from linea import Linea


class TestLinea(unittest.TestCase):

    def test_imprime_linea_simple(self):
        """
        Imprime una línea sin modificadores. Es decir, texto que recibe, texto
        que se imprime.
        """

        linea = Linea("Esta es una línea simple")

        self.assertEqual("Esta es una línea simple", linea.texto_transformado)

    def test_reemplaza_inicio_de_gritos(self):
        """
        La línea contiene un símbolo para iniciar gritos, que se reemplaza por
        el HTML correspondiente.
        """

        linea = Linea("Esta línea abre |gritos")

        self.assertEqual(
            'Esta línea abre <span class="gritos">gritos',
            linea.texto_transformado
        )

    def test_reemplaza_inicio_y_final_de_gritos(self):
        """
        Dentro de una misma línea se abre y se cierra la modificación de voz a
        gritos.
        """

        linea = Linea("Aquí abre |gritos| y los cierra.")

        self.assertEqual(
            'Aquí abre <span class="gritos">gritos</span> y los cierra.',
            linea.texto_transformado
        )

    def test_reemplaza_final_de_gritos(self):
        """
        La línea contiene un símbolo para finalizar gritos, que se reemplaza
        por la etiqueta de cierra debido a que se inicializa el arreglo de
        pendientes con una barra vertical.
        """

        linea = Linea("fin de gritos| aquí", ["|"])

        self.assertEqual('fin de gritos</span> aquí', linea.texto_transformado)

    def test_elimina_espacios_en_blanco_de_final(self):
        """
        Imprime la línea eliminando los espacios del final.
        """

        linea = Linea("Espacios al final    ")

        self.assertEqual('Espacios al final', linea.texto_transformado)

    def test_elimina_espacios_en_blanco_de_inicio(self):
        """
        Imprime la línea eliminando los espacios del inicio.
        """

        linea = Linea("    Espacios al inicio")

        self.assertEqual('Espacios al inicio', linea.texto_transformado)

    def test_imprime_linea_con_comentario(self):
        """
        Imprime la parte del texto que no contiene comentario.
        """

        linea = Linea("Línea con % comentario")

        self.assertEqual("Línea con", linea.texto_transformado)

    def test_reemplaza_inicio_de_segunda_voz(self):
        """
        La línea contiene un símbolo de inicio de segunda voz, y se reemplaza
        por su HTML correspondiente.
        """

        linea = Linea("Inicia [segunda voz")

        self.assertEqual(
            'Inicia <span class="segunda-voz">segunda voz',
            linea.texto_transformado
        )

    def test_reemplaza_final_de_segunda_voz(self):
        """
        Reemplaza el final de la segunda voz, cuando un inicio de segunda voz
        le es enviado como voz activa.
        """

        linea = Linea("fin] segunda", ["["])

        self.assertEqual('fin</span> segunda', linea.texto_transformado)

    def test_reemplaza_inicio_y_final_de_segunda_voz(self):
        """
        Dentro de una misma línea se abre y se cierra la modificación a segunda
        voz.
        """

        linea = Linea("Segunda [voz] aquí.")

        self.assertEqual(
            'Segunda <span class="segunda-voz">voz</span> aquí.',
            linea.texto_transformado
        )

    def test_reemplaza_inicio_de_tercera_voz(self):
        """
        La línea contiene un símbolo de inicio de tercera voz, y se reemplaza
        por su HTML correspondiente.
        """

        linea = Linea("Inicia {tercera voz")

        self.assertEqual(
            'Inicia <span class="tercera-voz">tercera voz',
            linea.texto_transformado
        )

    def test_reemplaza_final_de_tercera_voz(self):
        """
        Reemplaza el final de la tercera voz, cuando un inicio de tercera voz
        le es enviado como voz activa.
        """

        linea = Linea("fin} tercera", ["{"])

        self.assertEqual('fin</span> tercera', linea.texto_transformado)

    def test_reemplaza_inicio_y_final_de_tercera_voz(self):
        """
        Dentro de una misma línea se abre y se cierra la modificación a tercera
        voz.
        """

        linea = Linea("Tercera {voz} aquí.")

        self.assertEqual(
            'Tercera <span class="tercera-voz">voz</span> aquí.',
            linea.texto_transformado
        )

    def test_las_estrellas_solas_se_imprimen(self):
        """
        Demuestra que el carácter de estrella no es necesario que se escape.
        """

        linea = Linea("La estrella * se imprime sin problemas.")

        self.assertEqual(
            "La estrella * se imprime sin problemas.",
            linea.texto_transformado
        )

    def test_cuenta_palabras(self):
        linea = Linea("Estas son cuatro palabras")

        self.assertEqual(linea.cantidad_de_palabras, 4)

    def test_cuenta_palabras_en_linea_con_comentario(self):
        linea = Linea("Estas son % cuatro palabras")

        self.assertEqual(linea.cantidad_de_palabras, 2)

    def test_cuenta_palabras_en_linea_con_porcentaje(self):
        linea = Linea("Esto es 10,000\% correcto")

        self.assertEqual(linea.cantidad_de_palabras, 4)

    def test_cuenta_palabras_en_linea_con_comentario_y_porcentaje(self):
        linea = Linea("Esto es 10,000\% correcto, pero % esto no")

        self.assertEqual(linea.cantidad_de_palabras, 5)

    ###########################################################################
    # FALTAN POR HACER ########################################################
    ###########################################################################

    def test_se_cierra_segunda_voz_sin_inicio(self):

        pass

    def test_se_cierra_tercera_voz_sin_inicio(self):

        pass


if __name__ == '__main__':
    unittest.main()
