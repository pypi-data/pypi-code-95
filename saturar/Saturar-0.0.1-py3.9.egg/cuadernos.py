#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# archivo python para hacer un ABM para los códigos de saturar
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

import sqlite3
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from .nuevo_cuaderno import NUEVO_CUADERNO


class CUADERNOS(object):

    """Docstring for CODIGOS. """

    def __init__(self, id_prop, archivo_db, ventana, pagina):
        """TODO: to be defined. """
        self.w_pagina = pagina
        self.id_prop = id_prop
        self.con = archivo_db
        self.id_cuad = None
        self.ventana = Gtk.Window()
        self.scrolltabla = Gtk.ScrolledWindow()
        vbox = Gtk.VBox()
        self.scrolltabla.set_hexpand(True)
        self.scrolltabla.set_vexpand(True)
        scrolltext = Gtk.ScrolledWindow()
        scrolltext.set_hexpand(True)
        scrolltext.set_vexpand(True)
        frame = Gtk.Frame()
        frame.set_label("Memo del cuaderno")
        frame.set_shadow_type(1)
        hbox = Gtk.HBox()
        boton_actu = Gtk.Button("actualizar")
        boton_actu.connect("clicked", self.actualizar_tabla)
        hbox.pack_start(boton_actu, True, True, 0)
        boton_nuev = Gtk.Button("Nuevo cuaderno")
        boton_nuev.connect("clicked", self.nueva_c)
        hbox.pack_start(boton_nuev, True, True, 0)
        boton_borr = Gtk.Button("Borrar cuaderno")
        boton_borr.connect("clicked", self.borrar_c)
        hbox.pack_start(boton_borr, True, True, 0)

        ######################################################################
        #  configuraciones del textview
        ######################################################################
        # Widget con el textview donde se visualizan el texto a codificar
        self.pagina = Gtk.TextView()
        # Deshabilito la edición del textview
        self.pagina.set_editable(False)
        # Corto el texto en las palabras si se pasan del tamaño del textview
        self.pagina.set_wrap_mode(Gtk.WrapMode.WORD)
        self.pagina.set_tooltip_text("")
        self.p_buffer = self.pagina.get_buffer()
        self._tabla_valor = ""
        self.tabla = Gtk.TreeView()
        select = self.tabla.get_selection()
        select.connect("changed", self.on_tree_selection_changed)
        self.crear_tabla()
        self.scrolltabla.add(self.tabla)
        scrolltext.add(self.pagina)
        frame.add(scrolltext)
        vbox.pack_start(self.scrolltabla, True, True, 0)
        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(hbox, False, False, 0)
        ventana.add(vbox)
        ventana.show_all()

    def borrar_c(self, widget):
        """TODO: Docstring for borr_p.

        :widget: TODO
        :returns: TODO

        """
        if self.id_cuad != "0":
            cod = 'UPDATE cuaderno SET status = 0 where id_cuaderno = ' + self.id_cuad
            cursorObj = self.con.cursor()
            cursorObj.execute(cod)
            self.con.commit()
            cod = 'UPDATE pagina SET status = 0 where id_cuaderno = ' + self.id_cuad
            cursorObj = self.con.cursor()
            cursorObj.execute(cod)
            self.con.commit()

            cod = 'SELECT id_pagina  FROM pagina WHERE id_cuaderno = ' + self.id_cuad
            cursorObj = self.con.cursor()
            cursorObj.execute(cod)
            res = cursorObj.fetchall()
            for pag in res:
                cod = 'UPDATE codificacion SET status = 0 where id_pagina = '+ str(pag[0])
                cursorObj = self.con.cursor()
                cursorObj.execute(cod)
                self.con.commit()
            self.actualizar_tabla(widget)

    def nueva_c(self, widget):
        """TODO: Docstring for nueva_p.

        :widget: TODO
        :returns: TODO

        """
        p = NUEVO_CUADERNO(self.con, self.id_prop, self)
        # self.actualizar_tabla(widget)

    def obtener_id_cuad(self):
        """TODO: Docstring for obtener_id_pag.
        :returns: TODO

        """
        return self.id_cuad

    def actualizar_tabla(self, widget):
        for col in self.tabla.get_columns():
            self.tabla.remove_column(col)
        self.crear_tabla()

    def crear_tabla(self):
        """TODO: Docstring for crear_tabla.
        :returns: TODO

        """
        cod_data = self.actualizar_cod(self.id_prop)
        store = Gtk.ListStore(str, str, str, str, str, str)
        self.tabla.set_model(store)
        for i in cod_data:
            store.append([i['id_cuaderno'],
                          i['id_proy'],
                          i['nombre_cuad'],
                          i['memo'],
                          i['fecha_alt'],
                          i['status']])
        # definimos las columnas
        # codigos
        col_cod = Gtk.TreeViewColumn("id_cuaderno",
                                     Gtk.CellRendererText(),
                                     text=0)
        self.tabla.append_column(col_cod)
        # colores
        col_col = Gtk.TreeViewColumn("nombre",
                                     Gtk.CellRendererText(),
                                     text=2)
        self.tabla.append_column(col_col)
        # memo

        col_fech = Gtk.TreeViewColumn("fecha de alta",
                                      Gtk.CellRendererText(),
                                      text=4)
        self.tabla.append_column(col_fech)
        col_status = Gtk.TreeViewColumn("status",
                                        Gtk.CellRendererText(),
                                        text=5)
        self.tabla.append_column(col_status)

    def on_tree_selection_changed(self, selection):
        """TODO: Docstring for on_tree_selection_changed.

        :arg1: TODO
        :returns: TODO

        """
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            self.p_buffer.set_text(model[treeiter][3])
            # Con esto podemos sacar el memo del código y ponerlo en un tooltip
            #self.tabla.set_tooltip_text(model[treeiter][1])
            self.id_cuad = model[treeiter][0]
            self.w_pagina.id_prop = self.id_cuad
            self.w_pagina.actualizar_tabla(None)
            #self.w_pagina.id_prop = 1

    def actualizar_cod(self, id_prop):
        """TODO: Docstring for actualizar_cod.
        :returns: TODO

        """
        cod = 'SELECT * FROM cuaderno WHERE id_proy = '+str(id_prop)
        cursorObj = self.con.cursor()
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


