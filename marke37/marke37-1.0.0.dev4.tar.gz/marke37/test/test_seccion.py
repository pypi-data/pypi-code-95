#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

import unittest
from pprint import pprint
import sys
from ..linea import Linea
from ..seccion import Seccion


class TestSeccion(unittest.TestCase):

    def test_seccion_convierte_cadena_a_linea(self):
        """
        Convierte una cadena de texto a un objeto Linea, y la agrega a las
        líneas dentro de la sección.
        """

        seccion = Seccion()
        seccion.agregar_linea("Esta es una línea simple")

        self.assertEqual(len(seccion.lineas), 1)
        self.assertEqual(
            "Esta es una línea simple",
            seccion.lineas[0].texto_original
        )

    def test_seccion_vacia_no_tiene_tipo(self):
        """
        Una sección vacía no tiene tipo todavía.
        """

        seccion = Seccion()

        self.assertEqual(None, seccion.tipo)

    def test_seccion_es_verso(self):
        """
        Una sección con una línea sin indicadores es tipo "verso"
        """

        seccion = Seccion()
        seccion.agregar_linea("Esta es una línea simple")

        self.assertEqual("verso", seccion.tipo)

    def test_seccion_es_coro(self):
        """
        Una sección con dos ** al inicio es un "coro".
        """

        seccion = Seccion()
        seccion.agregar_linea("**Primer línea de coro")

        self.assertEqual("coro", seccion.tipo)

    def test_seccion_es_puente(self):
        """
        Una sección con un _ al inicio es un "puente".
        """

        seccion = Seccion()
        seccion.agregar_linea("_Primer línea de puente")

        self.assertEqual("puente", seccion.tipo)

    def test_seccion_es_precoro(self):
        """
        Una sección con un ## al inicio es un "precoro".
        """

        seccion = Seccion()
        seccion.agregar_linea("##Primer línea de precoro")

        self.assertEqual("precoro", seccion.tipo)

    def test_seccion_es_postcoro(self):
        """
        Una sección con un ## al inicio es un "postcoro".
        """

        seccion = Seccion()
        seccion.agregar_linea("$$Primer línea de postcoro")

        self.assertEqual("postcoro", seccion.tipo)

    def test_seccion_es_intro(self):
        """
        Una sección con un _** al inicio es un "intro".
        """

        seccion = Seccion()
        seccion.agregar_linea("_**Primer línea de intro")

        self.assertEqual("intro", seccion.tipo)

    def test_seccion_es_outro(self):
        """
        Una sección con un ## al inicio es un "outro".
        """

        seccion = Seccion()
        seccion.agregar_linea("**_Primer línea de outro")

        self.assertEqual("outro", seccion.tipo)

    def test_bloque_de_coro_contiene_apertura(self):
        """
        Un bloque contiene la línea de apertura, una línea previa a las líneas.
        """
        seccion = Seccion()
        seccion.agregar_linea("**Primer línea de coro")

        self.assertTrue(len(seccion.bloque) > 1)
        self.assertIsInstance(seccion.bloque[0], str)
        self.assertEqual('<div class="seccion seccion-coro">', seccion.bloque[0])

    def test_primer_linea_de_verso_no_se_recorta(self):
        """
        Como el verso no contiene símbolos a ser recortados, esta prueba tiene
        como objetivo demostrar que el texto se mantiene íntegro.
        """

        seccion = Seccion()
        seccion.agregar_linea("Primera línea de verso")

        primera_linea = seccion.lineas[0].texto_transformado
        self.assertEqual('Primera línea de verso', primera_linea)

    def test_primer_linea_de_coro_no_contiene_simbolos(self):
        """
        La primera línea del coro no muestra los símbolos que indican que
        pertenece al coro.
        """

        seccion = Seccion()
        seccion.agregar_linea("**Primera línea de coro")

        primera_linea = seccion.lineas[0].texto_transformado
        self.assertEqual('Primera línea de coro', primera_linea)

    def test_primer_linea_de_puente_no_contiene_simbolos(self):
        """
        La primera línea del puente no muestra los símbolos que indican que
        pertenece al puente.
        """

        seccion = Seccion()
        seccion.agregar_linea("_Primera línea de puente")

        primera_linea = seccion.lineas[0].texto_transformado
        self.assertEqual('Primera línea de puente', primera_linea)

    def test_primer_linea_de_intro_no_contiene_simbolos(self):
        """
        La primera línea del intro no muestra los símbolos que indican que
        pertenece al intro.
        """

        seccion = Seccion()
        seccion.agregar_linea("_**Primera línea de intro")

        primera_linea = seccion.lineas[0].texto_transformado
        self.assertEqual('Primera línea de intro', primera_linea)

    def test_primer_linea_de_outro_no_contiene_simbolos(self):
        """
        La primera línea del outro no muestra los símbolos que indican que
        pertenece al outro.
        """

        seccion = Seccion()
        seccion.agregar_linea("**_Primera línea de outro")

        primera_linea = seccion.lineas[0].texto_transformado
        self.assertEqual('Primera línea de outro', primera_linea)

    def test_primer_linea_de_precoro_no_contiene_simbolos(self):
        """
        La primera línea del precoro no muestra los símbolos que indican que
        pertenece al precoro.
        """

        seccion = Seccion()
        seccion.agregar_linea("##Primera línea de precoro")

        primera_linea = seccion.lineas[0].texto_transformado
        self.assertEqual('Primera línea de precoro', primera_linea)

    def test_primer_linea_de_postcoro_no_contiene_simbolos(self):
        """
        La primera línea del postcoro no muestra los símbolos que indican que
        pertenece al postcoro.
        """

        seccion = Seccion()
        seccion.agregar_linea("$$Primera línea de postcoro")

        primera_linea = seccion.lineas[0].texto_transformado
        self.assertEqual('Primera línea de postcoro', primera_linea)

    def test_segunda_linea_de_coro_cierra_seccion(self):
        """
        Esta prueba demuestra que la última línea ya no imprime la clausura de
        la sección.
        """

        seccion = Seccion()
        seccion.agregar_linea("**Inicio")
        seccion.agregar_linea("Final**")

        inicio = seccion.lineas[0].texto_transformado
        self.assertEqual('Inicio', inicio)
        final = seccion.lineas[1].texto_transformado
        self.assertEqual('Final', final)

    def test_bloque_de_verso_tiene_etiqueta_html_de_cierre(self):

        seccion = Seccion()
        seccion.agregar_linea("Inicio")
        seccion.agregar_linea("Final")
        seccion.cerrar()

        self.assertEqual(4, len(seccion.bloque))
        self.assertEqual('<div class="seccion seccion-verso">', seccion.bloque[0])
        self.assertEqual("Inicio", seccion.bloque[1].texto_transformado)
        self.assertEqual("Final", seccion.bloque[2].texto_transformado)
        self.assertEqual("</div>", seccion.bloque[3])

    def test_bloque_de_coro_tiene_etiqueta_html_de_cierre(self):

        seccion = Seccion()
        seccion.agregar_linea("**Inicio")
        seccion.agregar_linea("Final**")

        self.assertEqual(4, len(seccion.bloque))
        self.assertEqual("</div>", seccion.bloque[3])

    def test_seccion_maneja_voz_en_dos_lineas(self):
        seccion = Seccion()
        seccion.agregar_linea("Aquí hay {otra")
        seccion.agregar_linea("voz} que acaba")
        seccion.cerrar()

        self.assertEqual(
            'Aquí hay <span class="tercera-voz">otra',
            seccion.lineas[0].texto_transformado
        )
        self.assertEqual(
            'voz</span> que acaba',
            seccion.lineas[1].texto_transformado
        )

    def test_seccion_cierra_gritos_sin_cierre(self):
        seccion = Seccion()
        seccion.agregar_linea("Gritos |abren")
        seccion.agregar_linea("Pero nunca cierran")

        self.assertEqual(
            'Gritos <span class="gritos">abren',
            seccion.bloque[1].texto_transformado
        )

        self.assertEqual(
            'Pero nunca cierran</span>',
            seccion.bloque[2].texto_transformado
        )

    def test_cantidad_de_lineas(self):

        seccion = Seccion()
        seccion.agregar_linea("**_Primera línea de outro")

        self.assertEqual(seccion.cantidad_de_lineas, 1)

    def test_cantidad_de_lineas_con_vacias(self):

        seccion = Seccion()
        seccion.agregar_linea("**_Primera línea de outro")
        seccion.agregar_linea("")
        seccion.agregar_linea("")
        seccion.agregar_linea("")
        seccion.agregar_linea("Una más**")

        self.assertEqual(seccion.cantidad_de_lineas, 2)

    def test_cantidad_de_palabras_una_linea(self):

        seccion = Seccion()
        seccion.agregar_linea("**_Primera línea de outro")

        self.assertEqual(seccion.cantidad_de_palabras, 4)

    def test_cantidad_de_palabras_dos_lineas(self):

        seccion = Seccion()
        seccion.agregar_linea("**_Primera línea de outro")
        seccion.agregar_linea("Segunda línea")

        self.assertEqual(seccion.cantidad_de_palabras, 6)

    def test_cantidad_de_palabras_con_lineas_vacias(self):

        seccion = Seccion()
        seccion.agregar_linea("**_Primera línea de outro")
        seccion.agregar_linea("")
        seccion.agregar_linea("")
        seccion.agregar_linea("Segunda línea")
        seccion.agregar_linea("")
        seccion.agregar_linea("")

        self.assertEqual(seccion.cantidad_de_palabras, 6)

    ###########################################################################
    # PENDIENTES ##############################################################
    ###########################################################################

    def test_seccion_cierra_voces(self):

        pass

    ###########################################################################
    # MECANISMO DE ADVERTENCIAS ###############################################
    ###########################################################################

    def test_se_crea_una_advertencia_por_agregar_linea_a_seccion_cerrada(self):

        pass


if __name__ == '__main__':
    unittest.main()
