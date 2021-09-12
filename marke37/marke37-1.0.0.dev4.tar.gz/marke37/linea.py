#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

# TODO: Contar palabras

class Linea:
    """
    Sirve para procesar una línea de una letra de canción en formato Marke37,
    para su transformación en diversos formatos, como HTML, reStructuredText,
    LaTeX, y PDF.
    """
    SIMBOLO_COMENTARIO = "%"

    # Símbolos para denotar la apertura de un cambio de voz.
    GRITOS = "|"
    SEGUNDA_VOZ = "["
    TERCERA_VOZ = "{"
    # Símbolos para denotar la clausura del cambio de voz.
    GRITOS_C = "|"
    SEGUNDA_VOZ_C = "]"
    TERCERA_VOZ_C = "}"

    # Relación de los símbolos de apertura con su cierre.
    VOCES = {
        GRITOS:      GRITOS_C,
        SEGUNDA_VOZ: SEGUNDA_VOZ_C,
        TERCERA_VOZ: TERCERA_VOZ_C,
    }

    # Relación de sustitución del marcado de apertura.
    APERTURA_DE_VOZ = {
        GRITOS:      '<span class="gritos">',
        SEGUNDA_VOZ: '<span class="segunda-voz">',
        TERCERA_VOZ: '<span class="tercera-voz">',
    }

    # Relación de sustitución del marcado de clausura.
    CLAUSURA_DE_VOZ = {
        GRITOS_C: '</span>',
        SEGUNDA_VOZ_C: '</span>',
        TERCERA_VOZ_C: '</span>',
    }

    def __init__(self, texto, efectos_abiertos=None, diccionario=None, cerrar_voces=False):
        self.texto_original = texto
        self.texto_plano = ""

        if efectos_abiertos is None:
            self.efectos_abiertos = []
        else:
            self.efectos_abiertos = efectos_abiertos

        self._cerrar_voces = cerrar_voces

        self._diccionario = diccionario

    def imprimir(self, cerrar_voces=False):
        """
        Imprime la cadena transformada.

        :returns: Texto procesado en el formato requerido.
        :rtype: string
        """

        linea = self._imprimir_antes_de()
        linea += self.texto_transformado
        linea += self._imprimir_despues_de()
        linea += self._imprimir_salto_de_linea()

        return linea

    @property
    def texto_transformado(self):
        texto = self._texto_sin_comentario()

        # Si se recibe la instrucción de cerrar voces, se forzan las voces
        # abiertas como símbolos al final del texto.
        if self._cerrar_voces:
            if len(self.efectos_abiertos) > 0:
                for efecto in self.efectos_abiertos:
                    texto += self.VOCES[efecto]

        texto = self._reemplazar_voces(texto, self.efectos_abiertos)

        self._texto_transformado = texto

        return self._texto_transformado

    @property
    def cantidad_de_palabras(self):
        texto = self._texto_sin_comentario()

        self._cantidad_de_palabras = len(texto.split())

        return self._cantidad_de_palabras

    def _texto_sin_comentario(self):
        """
        Elimina los comentarios de la línea recibida.
        """

        texto = self.texto_original.strip()

        # Si no hay signo de '%', entonces regresar todo el texto.
        if not self.SIMBOLO_COMENTARIO in texto:
            return texto

        # Si la línea es enteramente comentario, regresamos una cadena vacía.
        if texto[0] == self.SIMBOLO_COMENTARIO:
            return ''

        # Si no es completamente comentario, hay que analizar si el porciento debe ser texto.
        indices = [i for i, letra in enumerate(self.texto_original) if letra == self.SIMBOLO_COMENTARIO]

        indices_a_eliminar = []
        for i in indices:
            # Si tenemos una diagonal invertida, entonces es texto legítimo,
            # y lo dejamos en paz.
            if texto[i-1] == '\\':
                indices_a_eliminar.append(i - 1)
                continue

            # En este punto, ya sabemos que no es comentario. Regresamos el texto hasta esta posición.
            texto_l = list(texto)
            diagonalesCnt = len(indices_a_eliminar)
            print(indices_a_eliminar)
            if diagonalesCnt > 0:
                indices_a_eliminar.reverse() # Invertir para no tener que recorrer.
                for j in indices_a_eliminar:
                    texto_l.pop(j)

            return ''.join(texto_l[0:i - diagonalesCnt])

        return texto

    def _reemplazar_voces(self, texto, voces):
        """
        En esta función es donde se procesa la cadena de datos
        que proviene de la sección.
        """

        texto_procesado = ""
        for c in texto:
            # Primero buscamos si tenemos efectos abiertos...
            if len(voces) > 0:
                # Para buscar cerrar el último en la lista.
                texto_procesado += self._cerrar_voz(c, voces)
            else:
                texto_procesado += self._abrir_voz(c, voces)

        # Se corre con strip para eliminar espacios dejados por un comentario
        # que se eliminó en el preocesamiento.
        return texto_procesado.strip()

    def _cerrar_voz(self, caracter, voces):
        """
        Busca los símbolos de clausura, para ver si coinciden con el carácter
        actual.
        """

        reemplazo = caracter

        ultimo_efecto = voces[-1]
        simbolo_clausura = self.VOCES[ultimo_efecto]
        if caracter == simbolo_clausura:
            voces.pop()
            reemplazo = self.CLAUSURA_DE_VOZ[simbolo_clausura]

            # Para obtener el reemplazo ahora se busca en el diccionario.
            if not self._diccionario:
                return reemplazo

            if "Clausura" not in self._diccionario:
                return reemplazo

            if simbolo_clausura not in self._diccionario["Clausura"]:
                return reemplazo

            return self._diccionario["Clausura"][simbolo_clausura]

        return reemplazo

    def _abrir_voz(self, caracter, voces):
        """
        Busca dentro de los caracteres que definen las voces para ver si se
        va a abrir una nueva en base al caracter actual.
        """

        reemplazo = caracter

        for simbolo in self.VOCES.keys():
            if caracter == simbolo:
                voces.append(simbolo)
                # El reemplazo predeterminado...
                reemplazo = self.APERTURA_DE_VOZ[simbolo]

                # Para obtener el reemplazo ahora se busca en el diccionario.
                if not self._diccionario:
                    return reemplazo

                if "Apertura" not in self._diccionario:
                    return reemplazo

                if simbolo not in self._diccionario["Apertura"]:
                    return reemplazo

                return self._diccionario["Apertura"][simbolo]

        return reemplazo

    ###########################################################################
    # Funciones de impresión ##################################################
    ###########################################################################

    def _imprimir_antes_de(self):
        """
        Regresa una cadena que se imprime antes del texto de la letra. Está
        diseñada para ser reescrita por implementaciones de diversos formatos,
        para agregar el HTML, reST, o LaTeX necesario, según sea el caso.
        """

        if self._diccionario is None:
            return ''

        if "Inicio" not in self._diccionario:
            return ''

        return self._diccionario['Inicio']

    def _imprimir_despues_de(self):
        """
        Regresa una cadena con el contenido que se imprime después de la línea,
        que sirve para cerrar etiquetas que aún no se cierran (que se deben
        volver a abrir en el próximo renglón).
        """

        if self._diccionario is None:
            return ''

        if "Final" not in self._diccionario:
            return ''

        return self._diccionario['Final']

    def _imprimir_salto_de_linea(self):
        """
        Regresa una candena que representa un salto de línea, y se imprime
        después del contenido que va después del texto de la línea, y cualquier
        marcado que se necesite para acabar.
        """

        salto = '<br>'

        if self._diccionario is None:
            return salto

        if "SaltoDeLinea" not in self._diccionario:
            return salto

        return self._diccionario["SaltoDeLinea"]
