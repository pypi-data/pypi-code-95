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
import time
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from .nueva_categoria import NUEVA_CAT

class CATEGORIA(object):

    """Docstring for CODIGOS. """

    def __init__(self, id_prop, archivo_db, ventana):
        """TODO: to be defined. """
        self.id_prop = id_prop
        self.con = archivo_db
        self._id_cod_sel = "0"
        # ventana = Gtk.Window()
        self.scrolltabla = Gtk.ScrolledWindow()
        vbox = Gtk.VBox()
        self.scrolltabla.set_hexpand(True)
        self.scrolltabla.set_vexpand(True)
        scrolltext = Gtk.ScrolledWindow()
        scrolltext.set_hexpand(True)
        scrolltext.set_vexpand(True)
        frame = Gtk.Frame()
        frame.set_label("Memo")
        frame.set_shadow_type(1)
        hbox = Gtk.HBox()
        boton_actu = Gtk.Button("actualizar")
        boton_actu.connect("clicked", self.actualizar_tabla)
        boton_edit = Gtk.Button("Editar Categoría")
        boton_edit.connect("clicked", self.editar_cat)
        boton_borrar = Gtk.Button("borrar Categoría")
        boton_borrar.connect("clicked", self.borrar_cod)
        boton_nuevo = Gtk.Button("Nueva Categoría")
        boton_nuevo.connect("clicked", self.nuevo_cod)
        hbox.pack_start(boton_nuevo, True, True, 0)
        hbox.pack_start(boton_edit, True, True, 0)
        hbox.pack_start(boton_actu, True, True, 0)
        hbox.pack_start(boton_borrar, True, True, 0)
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
        vbox.pack_start(hbox, False, True, 0)
        ventana.add(vbox)
        ventana.show_all()

    def obtener_id_cat(self):
        """TODO: Docstring for obtener_id_pag.
        :returns: TODO

        """
        return self._id_cod_sel

    def editar_cat(self, widget):
        """TODO: Docstring for editar_cat.
        :returns: TODO

        """
        if self._id_cod_sel != "0":
            print("editar el id: ", self._id_cod_sel)
            NUEVA_CAT(self.con, self.id_prop,self,self._id_cod_sel) 

    def borrar_cod(self, widget):
        """TODO: Docstring for borrar_cod.
        :returns: TODO

        """
        if self._id_cod_sel != "0":
            cod = 'UPDATE categoria SET status = 0 where id_cat = '+ self._id_cod_sel
            cursorObj = self.con.cursor()
            cursorObj.execute(cod)
            self.con.commit()
            self.actualizar_tabla(widget)

    def nuevo_cod(self, widget):
        """TODO: Docstring for nuevo_cod.
        :returns: TODO

        """
        print("nuevo registro")
        n = NUEVA_CAT(self.con, self.id_prop,self)
        
        #self.actualizar_tabla(widget)

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
            store.append([i['id_cat'],
                          i['nombre_cat'],
                          i['color'],
                          i['memo'],
                          i['fecha_alt'],
                          i['status']])
        # definimos las columnas
        # codigos
        col_cod = Gtk.TreeViewColumn("Categorias",
                                     Gtk.CellRendererText(),
                                     text=1)
        self.tabla.append_column(col_cod)
        # colores
        col_col = Gtk.TreeViewColumn("color",
                                     Gtk.CellRendererText(),
                                     text=2,
                                     background=2)
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
            self._id_cod_sel = model[treeiter][0]
            # Con esto podemos sacar el memo del código y ponerlo en un tooltip
            # self.tabla.set_tooltip_text(model[treeiter][1])

    def actualizar_cod(self, id_prop):
        """TODO: Docstring for actualizar_cod.
        :returns: TODO

        """
        cod = 'SELECT * FROM categoria WHERE id_prop = '+str(id_prop)
        cursorObj = self.con.cursor()
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

# con = sqlite3.connect("saturar4.db")

# p = CATEGORIA(1,con)

# Gtk.main()
