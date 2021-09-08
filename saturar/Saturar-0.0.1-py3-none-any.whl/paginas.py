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
from .nueva_pagina import NUEVA_PAGINA
from .utils import DIALOGOS
import time

class PAGINAS(object):

    """Docstring for CODIGOS. """

    def __init__(self, id_cuaderno, archivo_db, caja, ventana):
        """TODO: to be defined. """
        self.id_cuaderno = id_cuaderno
        self.con = archivo_db
        self.id_pagina = 0
        self.tipo_pagina = 0
        # ventana = Gtk.Window()
        self.ventana = ventana
        self.scrolltabla = Gtk.ScrolledWindow()
        vbox = Gtk.VBox()
        self.scrolltabla.set_hexpand(True)
        self.scrolltabla.set_vexpand(True)
        scrolltext = Gtk.ScrolledWindow()
        scrolltext.set_hexpand(True)
        scrolltext.set_vexpand(True)
        frame = Gtk.Frame()
        frame.set_label("Contenido de la página")
        frame.set_shadow_type(1) 
        hbox = Gtk.HBox()

        self.mensajes = DIALOGOS(self.ventana)
        #######################################################################
        #  botones de la ventana
        ######################################################################

        boton_actu = Gtk.Button("actualizar")
        boton_actu.connect("clicked", self.actualizar_tabla)

        boton_nuev = Gtk.Button("Nueva página")
        boton_nuev.connect("clicked", self.nueva_p)


        boton_nuev_m = Gtk.Button("Nuevo multimedia")
        boton_nuev_m.connect("clicked", self.nuevo_m)

        boton_borr = Gtk.Button("Borrar página")
        boton_borr.connect("clicked", self.borrar_p)

        hbox.pack_start(boton_actu, True, True, 0)
        hbox.pack_start(boton_nuev, True, True, 0)
        hbox.pack_start(boton_nuev_m, True, True, 0)
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
        caja.add(vbox)
        caja.show_all()

    def borrar_p(self, widget):
        """TODO: Docstring for borr_p.

        :widget: TODO
        :returns: TODO

        """

        band = self.mensajes.pregunta("¿Esta seguro de borrar la  página?")
        if band == False:
            return
        if self.id_pagina != "0":

            cod = 'UPDATE pagina SET status = 0 where id_pagina = '+ self.id_pagina
            cursorObj = self.con.cursor()
            cursorObj.execute(cod)
            self.con.commit()
            cod = 'UPDATE codificacion SET status = 0 where id_pagina = '+ self.id_pagina
            cursorObj = self.con.cursor()
            cursorObj.execute(cod)
            self.con.commit()
            self.actualizar_tabla(widget)

    def nuevo_m(self, arg1):
        """TODO: Docstring for aceptar.
        id_pagina
        id_cuaderno
        titulo
        contenido
        fecha_alt
        status
        tipo
        """        
        print("busco videos")
        dialog = Gtk.FileChooserDialog(
            title="Selecciona un archivo de video", 
            parent=self.ventana, 
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            contenido = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
            return

        dialog.destroy()

        cod_tam = ('SELECT MAX(id_pagina) FROM pagina')
        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        tam = cursorObj.fetchall()
        if tam[0][0] is not None:
            id_pagina = int(tam[0][0])+1
        else:
            id_pagina = 1 
        id_cuaderno = self.id_cuaderno



        dialog2 = Gtk.Dialog(('ingrese el titulo del video:'), self.ventana)
        dialog2.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        #dialog2.set_default_response(Gtk.RESPONSE_ACCEPT)
        #dialog2.set_has_separator(False)
        #dialog2.set_resizable(False)
        #dialog2.set_border_width(8)
        
        label = Gtk.Label('ingresa un nuevo nombre para el video')
        name = Gtk.Entry()
        name.set_activates_default(True)
        
        dialog2.vbox.pack_start(label, False, False, 6)
        dialog2.vbox.pack_start(name, False, False, 6)

        dialog2.show_all()
        res = dialog2.run()
        if res == Gtk.ResponseType.OK:
            if name.get_text():
                titulo = name.get_text()
            else:
                print("error")
                return
        else:
            return
        dialog2.destroy()
        if titulo == "":
            print("debes completar algun nombre")
            return False
        print ("el contenido es: ",contenido)
        fecha_alt = time.strftime("%d/%m/%y"),
        status = 1

        n_cod = [int(id_pagina),
                 int(id_cuaderno),
                 titulo,
                 contenido,
                 fecha_alt[0],
                 int(status),
                 "multimedia"]

        cursorObj.execute('INSERT INTO pagina(id_pagina, id_cuaderno, titulo, contenido, fecha_alt, status,tipo) VALUES( ?, ?, ?,?,? ,?,?)', n_cod)
        self.con.commit()
        self.actualizar_tabla(None)
        self.hide()

    def nueva_p(self, widget):
        """TODO: Docstring for nueva_p.

        :widget: TODO
        :returns: TODO

        """
        p = NUEVA_PAGINA(self.con, self.id_cuaderno, self)
        # self.actualizar_tabla(widget)

    def obtener_id_pag(self):
        """TODO: Docstring for obtener_id_pag.
        :returns: TODO

        """
        return self.id_pagina

    def obtener_tipo_pag(self):
        """TODO: Docstring for obtener_id_pag.
        :returns: TODO

        """
        return self.tipo_pagina

    def actualizar_tabla(self, widget):
        for col in self.tabla.get_columns():
            self.tabla.remove_column(col)
        self.crear_tabla()

    def crear_tabla(self):
        """TODO: Docstring for crear_tabla.
        :returns: TODO

        """
        cod_data = self.actualizar_cod(self.id_cuaderno)
        store = Gtk.ListStore(str, str, str, str, str, str,str)
        self.tabla.set_model(store)
        for i in cod_data:
            store.append([i['id_pagina'],
                          i['id_cuaderno'],
                          i['titulo'],
                          i['contenido'],
                          i['fecha_alt'],
                          i['status'],
                          i['tipo']])
        # definimos las columnas
        # codigos
        col_cod = Gtk.TreeViewColumn("id_pagina",
                                     Gtk.CellRendererText(),
                                     text=0)
        self.tabla.append_column(col_cod)
        # colores
        col_col = Gtk.TreeViewColumn("titulo",
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
        col_status = Gtk.TreeViewColumn("tipo de registro",
                                        Gtk.CellRendererText(),
                                        text=6)
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
            # self.tabla.set_tooltip_text(model[treeiter][1])
            self.id_pagina = model[treeiter][0]
            self.tipo_pagina = model[treeiter][6]

    def actualizar_cod(self, id_cuaderno):
        """TODO: Docstring for actualizar_cod.
        :returns: TODO

        """
        cod = 'SELECT * FROM pagina WHERE id_cuaderno = '+str(id_cuaderno)
        cursorObj = self.con.cursor()
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

#con = sqlite3.connect("saturar2.db")

#p = PAGINAS(1,con)

#Gtk.main()
