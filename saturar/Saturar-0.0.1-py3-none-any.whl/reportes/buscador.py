#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# Ventana de busqueda para saturar
# Copyright © 2021 Valentin Basel <valentinbasel@gmail.com>
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
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import re
from ..reportes.saturapi import SATURAPI


class BUSCADOR(object):

    """Docstring for BUSCADOR. """

    def __init__(self, conexion,ventana_central):
        """TODO: to be defined. """
        self.ventana_central = ventana_central
        self.ventana = Gtk.Window()
        self.scrolltabla = Gtk.ScrolledWindow()
        self.scrolltabla.set_hexpand(True)
        self.scrolltabla.set_vexpand(True)
        #select.connect("changed", self.on_tree_selection_changed)
        self.tabla = Gtk.TreeView()
        select = self.tabla.get_selection()

        self.conexion = conexion
        hbox = Gtk.HBox()
        vbox = Gtk.VBox()
        lb = Gtk.Label("Buscar")
        self.e_busc = Gtk.Entry()
        hbox2 = Gtk.HBox()
        b_aceptar = Gtk.Button("Aceptar")
        b_aceptar.connect("clicked", self.aceptar)
        hbox.pack_start(lb, True, True, 0)
        hbox.pack_start(self.e_busc, True, True, 0) 
        hbox.pack_start(b_aceptar, True, True,0)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(hbox2, True, True, 0)
        vbox.pack_start(self.scrolltabla, True, True, 0)

        self.ventana.add(vbox)
        self.ventana.show_all()

    def aceptar(self, arg1):
        """TODO: Docstring for aceptar.

        :arg1: TODO
        :returns: TODO

        """
        s = SATURAPI()
        s.conectar(self.conexion)
        paginas = s.recuperar_paginas()
        #pag = paginas[0]

        text = self.e_busc.get_text()
        patron = re.compile(text)

        tab = []
        for pag in paginas:
            busq = patron.finditer(pag['contenido'],re.MULTILINE)
            for d in busq:
                dic = {"id_pagina":pag['id_pagina'],"titulo":pag['titulo'],"mach":d.group(), "posición":d.start()}
                tab.append(dic) 
        self.crear_tabla(tab)


    def crear_tabla(self,text):
        """TODO: Docstring for crear_tabla.
        :returns: TODO
        
        """

        self.scrolltabla.remove(self.tabla)
        self.tabla = Gtk.TreeView()
        select = self.tabla.get_selection()
        select.connect("changed", self.on_tree_selection_changed)
        cod_data =text # [{'id_cod': str(text)}]
        store = Gtk.ListStore(str,str,str,int)
        self.tabla.set_model(store)
        for i in cod_data:
            store.append([i['id_pagina'],i['titulo'], i['mach'],i['posición']])
        # definimos las columnas
        # ID
        col_cod_id = Gtk.TreeViewColumn("id_pagina",
                                     Gtk.CellRendererText(),
                                     text=0)
        self.tabla.append_column(col_cod_id)
        col_cod_id = Gtk.TreeViewColumn("titulo",
                                     Gtk.CellRendererText(),
                                     text=1)
        self.tabla.append_column(col_cod_id)
        col_cod_id = Gtk.TreeViewColumn("mach",
                                     Gtk.CellRendererText(),
                                     text=2)
        self.tabla.append_column(col_cod_id)
        col_cod_id = Gtk.TreeViewColumn("posición",
                                     Gtk.CellRendererText(),
                                     text=3)
        self.tabla.append_column(col_cod_id)


        # codigos

        self.scrolltabla.add(self.tabla)
        self.ventana.show_all()

    def on_tree_selection_changed(self, selection):
        """TODO: Docstring for on_tree_selection_changed.

        :arg1: TODO
        :returns: TODO

        """
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            id_p = model[treeiter][0]
            caracter = model[treeiter][3]
            self.ventana_central.buscar(id_p,caracter)
            print("id: ",id_p,"caracter: ",caracter)
            #self._id_cod_sel = model[treeiter][0]
            # Con esto podemos sacar el memo del código y ponerlo en un tooltip
            # self.tabla.set_tooltip_text(model[treeiter][1])
#c = BUSCADOR("/home/vbasel/Doctorado/owncloud/saturar/doctorado_valen_2020.db")
#Gtk.main()
