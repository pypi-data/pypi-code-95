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

class CATEGORIZAR(object):

    """Docstring for CODIGOS. """

    def __init__(self, id_prop, archivo_db, ventana):
        """TODO: to be defined. """
        self.id_prop = id_prop
        self.con = archivo_db
        self._id_cod_sel = "0"
        self._id_cat_sel = "0"
        self._id_cat_cod = "0"
        # ventana = Gtk.Window()
        self.scrolltabla = Gtk.ScrolledWindow()
        self.scrolltabla_cod = Gtk.ScrolledWindow()
        self.scrolltabla_cat_cod = Gtk.ScrolledWindow()
        vbox = Gtk.VBox()
        self.scrolltabla.set_hexpand(True)
        self.scrolltabla.set_vexpand(True)
        self.scrolltabla_cod.set_hexpand(True)
        self.scrolltabla_cod.set_vexpand(True)

        self.scrolltabla_cat_cod.set_hexpand(True)
        self.scrolltabla_cat_cod.set_vexpand(True)

        scrolltext = Gtk.ScrolledWindow()
        scrolltext.set_hexpand(True)
        scrolltext.set_vexpand(True)
        frame = Gtk.Frame()
        frame.set_label("Memo")
        frame.set_shadow_type(1)
        hbox = Gtk.HBox()
        boton_agr = Gtk.Button("Agregar")
        boton_agr.connect("clicked", self.agr)
        boton_quit = Gtk.Button("quitar")
        boton_quit.connect("clicked", self.quitar)
        vbox_b = Gtk.VBox()
        vbox_b.pack_start(boton_agr, True, True, 0)
        vbox_b.pack_start(boton_quit, True, True, 0)

        self.tabla = Gtk.TreeView()
        self.tabla_cat_cod = Gtk.TreeView()
        select = self.tabla.get_selection()
        select.connect("changed", self.on_tree_selection_changed)
        self.crear_tabla_cat()
        self.tabla_cod = Gtk.TreeView()
        select_cod = self.tabla_cod.get_selection()
        select_cod.connect("changed", self.on_tree_selection_changed_cod)
        self.crear_tabla_cod()

        self.scrolltabla.add(self.tabla)
        self.scrolltabla_cod.add(self.tabla_cod)
        vbox.pack_start(self.scrolltabla, True, True, 0)
        vbox.pack_start(self.scrolltabla_cod, True, True, 0)
        #vbox.pack_start(hbox, False, True, 0)
        hbox.pack_start(vbox, True, True, 0)
        hbox.pack_start(vbox_b, False, False,0)
        self.tabla_cat_cod = Gtk.TreeView()
        #select_cat_cod = self.tabla_cat_cod.get_selection()
        #select_cat_cod.connect("changed", self.on_tree_selection_changed_cod)
        self.scrolltabla_cat_cod.add(self.tabla_cat_cod)
        hbox.pack_start(self.scrolltabla_cat_cod, True, True, 0)
 
        self.crear_tabla_cat_cod()
        ventana.add(hbox)
        ventana.show_all()

    def obtener_id_cat(self):
        """TODO: Docstring for obtener_id_pag.
        :returns: TODO

        """
        return self._id_cat_sel

    def quitar(self, widget):
        """TODO: Docstring for borrar_cod.
        :returns: TODO

        # """
        print(self._id_cat_sel)
        print(self._id_cod_sel)
        cod_tam = 'UPDATE cod_axial SET status = 0 WHERE id_cod = '+ str(self._id_cod_sel) + ' AND id_cat = ' + str(self._id_cat_sel)

        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        # tam = cursorObj.fetchall()
        self.actualizar_cat_cod(self._id_cat_sel)
        self.actualizar_tabla_cat_cod(None)

    def agr(self, widget):
        """TODO: Docstring for nuevo_cod.
        :returns: TODO
        id_axial
        id_cod
        id_cat
        fecha_alt
        status
        """
        band = True
        print(self._id_cat_sel)
        print(self._id_cod_sel)
        cod_tam = ('SELECT MAX(id_axial) FROM cod_axial')
        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        tam = cursorObj.fetchall()
        codigos = self.actualizar_cat_cod(self._id_cat_sel)
        for a in codigos:
            if a['id_cod'] == self._id_cod_sel:
                print("esta ya codificado")
                band = False
        if tam[0][0] is not None:
            id_axial =  int(tam[0][0])+1
        else:
            id_axial = 1
        fecha_alt = time.strftime("%d/%m/%y"),
        status = 1

        print(fecha_alt)
        if band is True:
            cod = [id_axial,
                   int(self._id_cod_sel),
                   int(self._id_cat_sel),
                   str(fecha_alt[0]),
                   status
                   ]
            cursorObj.execute('INSERT INTO cod_axial(id_axial, id_cod, id_cat, fecha_alt, status) VALUES(  ?, ?,?,? ,?)', cod)
            self.con.commit()
            self.actualizar_tabla_cat_cod(None)



    def actualizar_tabla(self, widget):
        for col in self.tabla.get_columns():
            self.tabla.remove_column(col)
        self.crear_tabla_cat()

    def actualizar_tabla_cod(self, widget):
        for col in self.tabla_cod.get_columns():
            self.tabla_cod.remove_column(col)
        self.crear_tabla_cod()

    def actualizar_tabla_cat_cod(self, widget):
        for col in self.tabla_cat_cod.get_columns():
            self.tabla_cat_cod.remove_column(col)
        self.crear_tabla_cat_cod()

    def crear_tabla_cat_cod(self):
        """TODO: Docstring for crear_tabla.
        :returns: TODO

        """
        res = self.actualizar_cat_cod(self._id_cat_sel)
        cod = self.actualizar_cod(self.id_prop)
        #cod_data = self.actualizar_cod(self._id_cat_sel)
        
        store = Gtk.ListStore(str, str)
        self.tabla_cat_cod.set_model(store)
        for c in cod:
            for r in res:
                if c['id_cod'] == r['id_cod']:
                    store.append([c['nombre_cod'], c['color']])

        #for i in cod_data:
        #    store.append([i['nombre_cod'],
        #                  i['color']])
        # definimos las columnas
        # codigos
        col_cod = Gtk.TreeViewColumn("Códigos",
                                     Gtk.CellRendererText(),
                                     text=0, 
                                     background=1)
        self.tabla_cat_cod.append_column(col_cod)



    def crear_tabla_cod(self):
        """TODO: Docstring for crear_tabla.
        :returns: TODO

        """
        cod_data = self.actualizar_cod(self.id_prop)
        store = Gtk.ListStore(str, str, str, str, str, str)
        self.tabla_cod.set_model(store)
        for i in cod_data:
            store.append([i['id_cod'],
                          i['nombre_cod'],
                          i['color'],
                          i['memo'],
                          i['fecha_alt'],
                          i['status']])
        # definimos las columnas
        # codigos
        col_cod = Gtk.TreeViewColumn("Códigos",
                                     Gtk.CellRendererText(),
                                     text=1)
        self.tabla_cod.append_column(col_cod)
        # colores
        col_col = Gtk.TreeViewColumn("color",
                                     Gtk.CellRendererText(),
                                     text=2,
                                     background=2)
        self.tabla_cod.append_column(col_col)
        # memo

        col_fech = Gtk.TreeViewColumn("fecha de alta",
                                      Gtk.CellRendererText(),
                                      text=4)
        self.tabla_cod.append_column(col_fech)
        col_status = Gtk.TreeViewColumn("status",
                                        Gtk.CellRendererText(),
                                        text=5)
        self.tabla_cod.append_column(col_status)




    def crear_tabla_cat(self):
        """TODO: Docstring for crear_tabla.
        :returns: TODO

        """
        cod_data = self.actualizar_cat(self.id_prop)
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
            #self.p_buffer.set_text(model[treeiter][3])
            self._id_cat_sel = model[treeiter][0]

            self.actualizar_tabla_cat_cod(None)
            #print(res)

    def on_tree_selection_changed_cod(self, selection):
        """TODO: Docstring for on_tree_selection_changed.

        :arg1: TODO
        :returns: TODO

        """
        print("cod")
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            #self.p_buffer.set_text(model[treeiter][3])
            self._id_cod_sel = model[treeiter][0]
            # Con esto podemos sacar el memo del código y ponerlo en un tooltip
            # self.tabla.set_tooltip_text(model[treeiter][1])

    def actualizar_cat_cod(self,id_cat):
        """TODO: Docstring for actualizar_cat_cod.
        :returns: TODO

        """

        cod = 'SELECT id_cod, status FROM cod_axial WHERE id_cat = '+str(id_cat)
        cursorObj = self.con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[1] == 1:
                tag = {'id_cod': str(r[0])}
                cod_data.append(tag)
        return cod_data


    def actualizar_cat(self, id_prop):
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

    def actualizar_cod(self, id_prop):
        """TODO: Docstring for actualizar_cod.
        :returns: TODO

        """
        cod = 'SELECT * FROM codigo WHERE id_prop = '+str(id_prop)
        cursorObj = self.con.cursor()
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
#con = sqlite3.connect("saturar4.db")

#p = CATEGORIA(1,con)

#Gtk.main()
