#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# Ventana para creación de nuevos codigos.
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

import gi
import time
import sqlite3
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class NUEVO_COD(object):

    """Docstring for NUEVO_COD. """

    def __init__(self, con, id_prop, padre, editar=False):
        """TODO: to be defined. """
        self.editar = editar
        self.padre = padre
        self.id_prop = id_prop 
        self.con = con
        self._id_cod = 0
        self.ventana = Gtk.Window()
        self.ventana.set_modal(True)
        hbox = Gtk.HBox()
        hbox_L = Gtk.VBox()
        hbox_C = Gtk.VBox()
        f_memo = Gtk.Frame(label="Memo")
        scrolltext = Gtk.ScrolledWindow()
        scrolltext.set_hexpand(True)
        scrolltext.set_vexpand(True)

        vbox_main = Gtk.VBox()
        L_nombre_cod = Gtk.Label("Nombre Código")
        self.E_nombre_cod = Gtk.Entry()
        L_nombre_col = Gtk.Label("color del Código")
        self.E_nombre_col = Gtk.ColorButton()
        gcol = Gdk.color_parse("#FF0000")
        self.E_nombre_col.set_color(gcol)
        ######################################################################
        #  configuraciones del textview
        ######################################################################
        # Widget con el textview donde se visualizan el texto a codificar
        self.pagina = Gtk.TextView()
        # Corto el texto en las palabras si se pasan del tamaño del textview
        self.pagina.set_wrap_mode(Gtk.WrapMode.WORD)
        self.pagina.set_tooltip_text("")
        # self.pagina.connect("button-press-event", self.boton_mouse)
        self.p_buffer = self.pagina.get_buffer()
        # codigo hardcodeado para probar
        self.p_buffer.set_text("")
        scrolltext.add(self.pagina)
        hbox_L.pack_start(L_nombre_cod, True, True, 0)
        hbox_L.pack_start(L_nombre_col, True, True, 0)

        hbox_C.pack_start(self.E_nombre_cod, True, True, 0)
        hbox_C.pack_start(self.E_nombre_col, True, True, 0)

        hbox.pack_start(hbox_L, True, True, 10)
        hbox.pack_start(hbox_C, True, True, 10)
        vbox_main.pack_start(hbox, False, True, 0)
        f_memo.add(scrolltext)
        vbox_main.pack_start(f_memo, True, True, 0)

        boton_aceptar = Gtk.Button("Aceptar")

        boton_cancelar = Gtk.Button("Cancelar")
        boton_cancelar.connect("clicked", self.cancelar)
        hbox_b = Gtk.HBox()
        hbox_b.pack_start(boton_cancelar, True, True, 0)
        hbox_b.pack_start(boton_aceptar, True, True, 0)
        vbox_main.pack_start(hbox_b, True, True, 0)
        if self.editar is not False:
            self.__edicion(editar)
            boton_aceptar.connect("clicked", self.aceptar_ed)
        else:

            boton_aceptar.connect("clicked", self.aceptar)
        self.ventana.add(vbox_main)
        self.ventana.show_all()

    def __edicion(self, ed):
        """TODO: Docstring for __edicion.
        :returns: TODO

        """
        cod_tam = 'SELECT * FROM codigo WHERE id_cod = ' + ed

        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        t = cursorObj.fetchall()
        tam = t[0] 
        self._id_cod = tam[0]
        self.E_nombre_cod.set_text(tam[1])
        gcol = Gdk.color_parse(tam[2])
        self.E_nombre_col.set_color(gcol)
        self.p_buffer.set_text(tam[3])


        print(tam)

    def cancelar(self, widget):
        """TODO: Docstring for cancelar.
        :returns: TODO

        """
        self.ventana.hide()

    def aceptar_ed(self, widget):
        """TODO: Docstring for aceptar_ed.

        :widget: TODO
        :returns: TODO

        """
        col = self.E_nombre_col.get_rgba().to_string()
        col = col.strip("rgba()")
        col = col.split(",")
        t_col = (int(col[0]), int(col[1]), int(col[2]))
        color = '#%02x%02x%02x' % t_col
        #fecha_alt = time.strftime("%d/%m/%y"),
        nombre_cod = self.E_nombre_cod.get_text()
        if nombre_cod == "":
            print("debes completar algun nombre")
            return False
        memo = self.p_buffer.get_text(self.p_buffer.get_start_iter(),
                                      self.p_buffer.get_end_iter(), True)
        cursorObj = self.con.cursor()
        c1 = 'UPDATE codigo SET nombre_cod = "' + nombre_cod + '"  where id_cod = ' +str(self._id_cod)
        cursorObj.execute(c1)
        self.con.commit()
        c2 = 'UPDATE codigo SET color = "' + color + '"  where id_cod = ' + str(self._id_cod)
        cursorObj.execute(c2)
        self.con.commit()
        c3 = 'UPDATE codigo SET memo = "' + memo + '"  where id_cod = ' + str(self._id_cod)
        cursorObj.execute(c3)
        self.con.commit()
        self.padre.actualizar_tabla(widget)
        self.ventana.hide()

    def aceptar(self, widget):
        """TODO: Docstring for aceptar.
        id_cod
        nombre_cod
        color
        memo
        id_prop
        fecha_alt
        status
        """
        cod_tam = ('SELECT MAX(id_cod) FROM codigo')
        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        tam = cursorObj.fetchall()
        if tam[0][0] is not None:
            id_cod = int(tam[0][0])+1
        else:
            id_cod = 1

        col = self.E_nombre_col.get_rgba().to_string()
        col = col.strip("rgba()")
        col = col.split(",")
        t_col = (int(col[0]), int(col[1]), int(col[2]))
        color = '#%02x%02x%02x' % t_col
        fecha_alt = time.strftime("%d/%m/%y"),
        status = 1
        id_prop = self.id_prop
        nombre_cod = self.E_nombre_cod.get_text()
        if nombre_cod == "":
            print("debes completar algun nombre")
            return False
        memo = self.p_buffer.get_text(self.p_buffer.get_start_iter(),
                                      self.p_buffer.get_end_iter(), True)
        n_cod = [int(id_cod),
                 nombre_cod,
                 color,
                 memo,
                 int(id_prop),
                 fecha_alt[0],
                 int(status)]

        cursorObj.execute('INSERT INTO codigo(id_cod, nombre_cod, color,memo, id_prop, fecha_alt, status) VALUES(?, ?, ?, ?,?,? ,?)', n_cod)
        self.con.commit()
        self.padre.actualizar_tabla(widget)
        self.ventana.hide()

#con = sqlite3.connect("saturar2.db")
#n = NUEVO_COD(con,1)
#Gtk.main()
