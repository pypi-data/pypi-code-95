#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# SATURAPI, API de conexión a la base de datos de saturar
# Copyright © 2020 Valentin Basel <valentinbasel@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import sqlite3


class SATURAPI(object):

    """Docstring for SATURAPI. """

    def __init__(self):
        """TODO: to be defined. """
        self.__con = None

    def conectar(self, arch):
        """Levanta una instacia de la base de datos de saturar y la prepara 
           para poder trabajar con la API
        :returns: con

        """
        try:
            self.__con = sqlite3.connect(arch)
            print("la conexión a: ", arch, " fue exitosa")
            return True
        except Exception as e:
            print("hubo un error en la conexión")
            return False
            raise e

    def recuperar_paginas(self, id_cuaderno=None):
        """
        Recupero todas las paginas activas de un cuaderno.}
        entradas: Id del cuaderno
        retorna: lista con las paginas activas y sus datos en el formato:

        id_pagina
        id_cuaderno
        titulo
        contenido
        fecha_alt
        status

        """
        if self.__con is None:
            print("no ha iniciado una conexión con la base de datos")
            return False
        if id_cuaderno is None:
            cod = 'SELECT * FROM pagina'
        else:
            cod = 'SELECT * FROM pagina WHERE id_cuaderno = '+str(id_cuaderno)
        cursorObj = self.__con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[5] == 1:
                tag = {'id_pagina': str(r[0]),
                       'id_cuaderno': str(r[1]),
                       'titulo': r[2],
                       'contenido': r[3],
                       'fecha_alt': r[4],
                       'status': str(r[5]),
                       'tipo': str(r[6])}
                cod_data.append(tag)
        return cod_data

    def recuperar_codigos(self):
        """
        """
        if self.__con is None:
            print("no ha iniciado una conexión con la base de datos")
            return False
        cod = 'SELECT * FROM codigo WHERE id_prop = 1'
        cursorObj = self.__con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[6] == 1:
                tag = {'id_cod': str(r[0]),
                       'nombre_cod': r[1],
                       'color': r[2],
                       'memo': r[3],
                       'fecha_alt': r[5],
                       'status': str(r[6])}
                cod_data.append(tag)
        return cod_data

    def recuperar_todo_codificado(self):
        """TODO: Docstring for recuperar_codificado.
        :returns: TODO

        """
        cod = 'SELECT * FROM codificacion'
        cursorObj = self.__con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[8] == 1:
                tag = {'id_codificacion': str(r[0]),
                       'id_cod': r[1],
                       'id_prop': r[2],
                       'id_pagina': r[3],
                       'text_cod': r[4],
                       'fecha_creac': r[7],
                       'status': str(r[8])}
                cod_data.append(tag)
        return cod_data

    def recuperar_codificado(self, id_cod):
        """TODO: Docstring for recuperar_codificado.
        :returns: TODO

        """
        cod = 'SELECT * FROM codificacion WHERE id_cod = ' + id_cod
        cursorObj = self.__con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[8] == 1:
                tag = {'id_codificacion': str(r[0]),
                       'id_cod': r[1],
                       'id_prop': r[2],
                       'id_pagina': r[3],
                       'text_cod': r[4],
                       'c_ini': r[5],
                       'c_fin': r[6],
                       'fecha_creac': r[7],
                       'status': str(r[8]),
                       'memo': str(r[9])}
                cod_data.append(tag)
        return cod_data

    def recuperar_pagina_especifica(self, pagina):
        """TODO: Docstring for recuperar_pagina_especifica.

        :pagina: TODO
        :returns: TODO

        """
        if self.__con is None:
            print("no ha iniciado una conexión con la base de datos")
            return False
        cod = 'SELECT * FROM pagina WHERE id_pagina = '+str(pagina)
        cursorObj = self.__con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[5] == 1:
                tag = {'id_pagina': str(r[0]),
                       'id_cuaderno': str(r[1]),
                       'titulo': r[2],
                       'contenido': r[3],
                       'fecha_alt': r[4],
                       'status': str(r[5]),
                       'tipo': str(r[6])
                       }
                cod_data.append(tag)
        return cod_data

    def recuperar_cuaderno_especifico(self, cuad):
        """TODO: Docstring for recuperar_pagina_especifica.

        :pagina: TODO
        :returns: TODO

        """
        if self.__con is None:
            print("no ha iniciado una conexión con la base de datos")
            return False
        cod = 'SELECT * FROM cuaderno WHERE id_cuaderno = '+str(cuad)
        cursorObj = self.__con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[5] == 1:
                tag = {'id_cuaderno': str(r[0]),
                       'id_proy': str(r[1]),
                       'nombre_cuad': r[2],
                       'memo': r[3],
                       'fecha_alt': r[4],
                       'status': str(r[5])}
                cod_data.append(tag)
        return cod_data

    def recuperar_categorias(self):
        """
        """
        if self.__con is None:
            print("no ha iniciado una conexión con la base de datos")
            return False
        cod = 'SELECT * FROM categoria WHERE id_prop = 1'
        cursorObj = self.__con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[6] == 1:
                tag = {'id_cat': str(r[0]),
                       'nombre_cat': r[1],
                       'color': r[2],
                       'memo': r[3],
                       'fecha_alt': r[5],
                       'status': str(r[6])}
                cod_data.append(tag)
        return cod_data

    def recuperar_categorizado(self, id_cat):
        """TODO: Docstring for recuperar_codificado.
        :returns: TODO

        """
        cod = 'SELECT * FROM cod_axial WHERE id_cat = '+str(id_cat) 
        cursorObj = self.__con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[4] == 1:
                tag = {'id_cod': str(r[1]),
                       'fecha_creac': r[3],
                       'status': str(r[4])}
                cod_data.append(tag)
        categor = []
        for c in cod_data:
            cod2 = 'SELECT nombre_cod, color FROM codigo WHERE id_cod = '+ str(c['id_cod'])
            cursorObj2 = self.__con.cursor()
            cursorObj2.execute(cod2)
            res2 = cursorObj2.fetchall()
            categor.append(res2[0])
        return categor



    def contar_elementos(self, lista):

        """

        Recibe una lista, y devuelve un diccionario con todas las repeticiones de

        cada valor

        """

        return {i:lista.count(i) for i in lista}
