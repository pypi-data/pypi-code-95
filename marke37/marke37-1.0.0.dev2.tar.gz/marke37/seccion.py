#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

# TODO: Contar líneas

from .linea import Linea


class Seccion:
    INICIO_CORO = "**"
    INICIO_PUENTE = "_"
    INICIO_INTRO = "_**"
    INICIO_OUTRO = "**_"
    INICIO_PRECORO = "##"
    INICIO_POSTCORO = "$$"

    FIN_CORO = "**"
    FIN_PUENTE = "_"
    FIN_INTRO = "**_"
    FIN_OUTRO = "_**"
    FIN_PRECORO = "##"
    FIN_POSTCORO = "$$"

    SECCIONES = {
        INICIO_OUTRO: FIN_OUTRO,
        INICIO_INTRO: FIN_INTRO,
        INICIO_CORO: FIN_CORO,
        INICIO_PRECORO: FIN_PRECORO,
        INICIO_POSTCORO: FIN_POSTCORO,
        INICIO_PUENTE: FIN_PUENTE
    }

    CLASES = {
        "[VERSO]": "verso",
        INICIO_CORO: "coro",
        INICIO_PUENTE: "puente",
        INICIO_INTRO: "intro",
        INICIO_OUTRO: "outro",
        INICIO_PRECORO: "precoro",
        INICIO_POSTCORO: "postcoro"
    }

    APERTURA_DE_SECCION = {
        "[VERSO]": '<div class="seccion seccion-verso">',
        INICIO_CORO: '<div class="seccion seccion-coro">',
        INICIO_PUENTE: '<div class="seccion seccion-puente">',
        INICIO_INTRO: '<div class="seccion seccion-intro">',
        INICIO_OUTRO: '<div class="seccion seccion-outro">',
        INICIO_PRECORO: '<div class="seccion seccion-precoro">',
        INICIO_POSTCORO: '<div class="seccion seccion-postcoro">'
    }

    CLAUSURA_DE_SECCION = {
        "[/VERSO]": '</div>',
        FIN_CORO: '</div>',
        FIN_PUENTE: '</div>',
        FIN_INTRO: '</div>',
        FIN_OUTRO: '</div>',
        FIN_PRECORO: '</div>',
        FIN_POSTCORO: '</div>'
    }

    def __init__(self, apertura=None, diccionario=None):
        """
        Inicializa la lista de voces que contiene la sección.
        """

        # Inicializa la lista de líneas.
        self.lineas = []
        # Inicializa la lista de voces en la letra.
        self.voces = []
        # Recibo la apertura aquí, posiblemente desde la letra. Si no es así,
        # lo establecemos a "None" para evitar cargar el tipo u otros datos.
        self._apertura = apertura
        # Determina si ya se recibió o no el elemento que indica que se cerró
        # la sección.
        self._esta_cerrada = False
        # Contiene el diccionario que la sección le pasa a cada una de las
        # líneas que pertenecen a ella.
        self._diccionario_de_linea = None

        # Cadenas de sustitución
        self._diccionario = diccionario

    def agregar_linea(self, linea):
        """
        Agrega una línea a la sección.

        :param linea: Línea de la letra a ser agregada a la sección.
        """

        # Revisar la línea por apertura.
        if len(self.lineas) <= 0:
            apertura = self._buscar_apertura(linea)
            if apertura:
                self._apertura = apertura
                linea = self._recortar_apertura_de_linea(linea)

        # Revisar la línea por clausura.
        clausura = self._buscar_clausura(linea)
        if clausura:
            linea = self._recortar_clausura_de_linea(linea)
            self.cerrar()

        # Crea un objeto línea en base a la cadena, pasando el diccionario de
        # línea en base a lo que recibe la sección.
        objLinea = Linea(linea, self.voces, self.diccionario_de_linea)
        self.lineas.append(objLinea)

    def cerrar(self):
        """
        Cierra la sección, estableciendo la bandera de cierre.
        """

        self._esta_cerrada = True

    @property
    def cantidad_de_lineas(self):
        cantidad = 0

        for l in self.lineas:
            if len(l.texto_transformado) > 0:
                cantidad = cantidad + 1

        return cantidad

    @property
    def cantidad_de_palabras(self):
        cantidad = 0

        for l in self.lineas:
            cantidad = cantidad + l.cantidad_de_palabras

        return cantidad

    @property
    def tipo(self):
        """
        Regresa el tipo de sección en base a los primeros tres caracteres de la
        primera línea.
        """

        # Si no estableción el tipo, ni tenemos líneas todavía, no podemos
        # decir qué tipo de sección es.
        if self._apertura is None:
            return None

        return self.CLASES[self._apertura]

    @property
    def bloque(self):
        """
        Regresa el conjunto de líneas de la sección, más los indicadores de
        sección, como un arreglo de líneas.
        """

        self._bloque = []

        # Revisamos si la sección se abre con una línea previa.
        if self._apertura in self.APERTURA_DE_SECCION:
            # En el caso de que sí se deba imprimir algo en la línea previa,
            # se agrega al bloque. En caso contrario, se omite.
            if self._linea_previa() is not None:
                self._bloque.append(self._linea_previa())

        # Se agrega para que la última línea cierre las voces que no se
        # cerraron con marcado adecuado.
        if len(self.lineas) > 0:
            self.lineas[-1]._cerrar_voces = True

        # Agregamos cada línea de la sección.
        for linea in self.lineas:
            self._bloque.append(linea)

        # Si la sección ya está cerrada, entonces podemos agregar el cierre.
        if self._esta_cerrada:
            if self._linea_posterior() is not None:
                # En caso de que no se requieran etiquetas de clausura de
                # sección, no se agregan al bloque.
                self._bloque.append(self._linea_posterior())

        return self._bloque

    @property
    def es_verso(self):
        """
        Bandera para saber si la sección actual es verso o no.
        """

        self._es_verso = False

        if self._apertura == "[VERSO]":
            self._es_verso = True

        return self._es_verso

    @property
    def esta_cerrada(self):
        return self._esta_cerrada

    def _buscar_apertura(self, linea):
        """
        Busca el indicador de apertura en la línea provista.

        :param linea: Cadena en la que se va a buscar el indicador de apertura.
        """

        if isinstance(linea, str):
            texto_de_linea = linea
        else:
            texto_de_linea = linea.texto_original

        for apertura in self.SECCIONES.keys():
            if apertura == texto_de_linea[0:len(apertura)]:
                return apertura

        return "[VERSO]"

    def _texto_de_inicio_de_linea(self):
        """
        Obtiene el texto a agregar al inicio de cada línea de la sección.
        """

        if not self._diccionario:
            return ""

        if "Apertura" not in self._diccionario:
            return ""

        inicio_linea = "Linea" + self.tipo.title()
        if inicio_linea not in self._diccionario["Apertura"]:
            return ""

        return self._diccionario["Apertura"][inicio_linea]

    def _texto_de_final_de_linea(self):
        """
        Obtiene el texto a agregar al final de cada línea de la sección.
        """

        if not self._diccionario:
            return ""

        if "Clausura" not in self._diccionario:
            return ""

        fin_linea = "Linea" + self.tipo.title()
        if fin_linea not in self._diccionario["Clausura"]:
            return ""

        return self._diccionario["Clausura"][fin_linea]

    def _buscar_clausura(self, linea):
        """
        Busca el indicador de clausura en la línea provista.

        :param linea: Cadena en la que se va a buscar el indicador de clausura.
        """

        if self._apertura == "[VERSO]":
            return None

        if isinstance(linea, str):
            texto_de_linea = linea
        else:
            texto_de_linea = linea.texto_original

        clausura = self.SECCIONES[self._apertura]
        if clausura == texto_de_linea[-len(clausura):]:
            return clausura

        return None

    def _recortar_apertura_de_linea(self, linea):
        """
        Recorta el indicador de apertura de sección de la línea que recibe como
        argumento.
        En sí, evita el corte en caso de no tener sección definida, o si la
        sección en cuestión es un verso.
        """

        if self._apertura is None or self._apertura == "[VERSO]":
            return linea

        return linea[len(self._apertura):]

    def _recortar_clausura_de_linea(self, linea):
        """
        Recorta el indicador de clausura de sección de la línea que recibe como
        argumento.
        Este corte solamente aplica para el tipo de sección ya abierta. Es
        decir, un puente busca el símbolo de cierre de puente, y un coro busca
        cerrar un coro.
        De momento, no se plantea hacer nada si la sección es una pero el
        cierre corresponde a otra.
        """

        # Si no hay indicador, no se hace nada.
        if self._apertura is None or self._apertura == "[VERSO]":
            return linea

        # Si lo único que hay en la línea es potencialmente el indicador,
        # tampoco se hace nada.
        clausura = self.SECCIONES[self._apertura]
        if len(linea) <= len(self._apertura):
            return linea

        if linea[-len(self._apertura):] == clausura:
            return linea[0:-len(clausura)]

        return linea[len(self._apertura):]

    def imprimir(self):
        """
        Regresa el bloque convertido en cadena.
        """

        cadena = ""

        for linea in self.bloque:
            if isinstance(linea, str):
                cadena += linea
            else:
                cadena += linea.imprimir()
            cadena += "\n"

        return cadena

    def _linea_previa(self):
        """
        Regresa el texto que va una línea previo a la primera línea de la
        sección.
        """
        texto = self.APERTURA_DE_SECCION[self._apertura]

        if self._diccionario is None:
            return texto

        if "Apertura" not in self._diccionario:
            return texto

        if self._apertura not in self._diccionario["Apertura"]:
            return texto

        return self._diccionario["Apertura"][self._apertura]

    def _linea_posterior(self):
        """
        Regresa el texto que va en la línea siguiente a la última línea de la
        sección.
        """

        if self.es_verso:
            clausura = "[/VERSO]"
        else:
            clausura = self.SECCIONES[self._apertura]

        texto = self.CLAUSURA_DE_SECCION[clausura]

        if self._diccionario is None:
            return texto

        if "Clausura" not in self._diccionario:
            return texto

        if clausura not in self._diccionario["Clausura"]:
            return texto

        return self._diccionario["Clausura"][clausura]

    @property
    def diccionario_de_linea(self):
        """
        Crea y almacena el diccionario a ser enviado a cada línea.
        """

        if self._diccionario_de_linea is not None:
            return self._diccionario_de_linea

        if self._diccionario and "Linea" in self._diccionario:
            # Hacer una copia es necesaria, de lo contrario cada sección se
            # imprimirá con los símbolos de la última sección agregada.
            diccionario_de_linea = self._diccionario["Linea"].copy()
        else:
            diccionario_de_linea = {}

        diccionario_de_linea["Inicio"] = self._texto_de_inicio_de_linea()
        diccionario_de_linea["Final"] = self._texto_de_final_de_linea()

        self._diccionario_de_linea = diccionario_de_linea

        return self._diccionario_de_linea