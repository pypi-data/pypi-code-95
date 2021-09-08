#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# Ventana de ABM para cargar paginas a saturar
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

#import pdftotext
import gi
import time
import sqlite3
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class NUEVO_CUADERNO(object):

    """Docstring for NUEVA_PAGINA. """

    def __init__(self, con, id_proy, padre):
        """
        """
        self.padre = padre
        self.con = con
        self.id_proy = id_proy
        self.ventana = Gtk.Window(title="Creador de cuadernos")
        vbox = Gtk.VBox()
        ######################################################################
        # datos titulos
        ######################################################################
        l_titulo = Gtk.Label("Titulo")
        self.e_titulo = Gtk.Entry()
        hbox_t = Gtk.HBox()
        hbox_t.pack_start(l_titulo, False, True, 0)
        hbox_t.pack_start(self.e_titulo, True, True, 0)
        ######################################################################
        #  configuraciones del textview
        ######################################################################
        frame = Gtk.Frame(label="Memo del cuaderno:")
        scrolltext = Gtk.ScrolledWindow()
        scrolltext.set_hexpand(True)
        scrolltext.set_vexpand(True)
        # Widget con el textview donde se visualizan el texto a codificar
        self.pagina = Gtk.TextView()
        # Deshabilito la edición del textview
        self.pagina.set_editable(True)
        self.p_buffer = self.pagina.get_buffer()
        # Corto el texto en las palabras si se pasan del tamaño del textview
        self.pagina.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolltext.add(self.pagina)
        frame.add(scrolltext)
        ######################################################################
        # botones
        ######################################################################
        boton_aceptar = Gtk.Button("Aceptar")
        boton_aceptar.connect("clicked", self.aceptar)
        boton_cancelar = Gtk.Button("Cancelar")
        hbox_b = Gtk.HBox()
        hbox_b.pack_start(boton_cancelar, False, True, 0)
        hbox_b.pack_start(boton_aceptar, False, True, 0)
        vbox.pack_start(hbox_t, False, True, 0)
        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(hbox_b, False, True, 0)
        self.ventana.add(vbox)
        self.ventana.show_all()

    def cancelar(self, widget):
        """TODO: Docstring for cancelar.

        :widget: TODO
        :returns: TODO

        """
        self.ventana.hide()

    def aceptar(self, widget):
        """TODO: Docstring for aceptar.
        id_pagina
        id_cuaderno
        titulo
        contenido
        fecha_alt
        status
        """
        cod_tam = ('SELECT MAX(id_cuaderno) FROM cuaderno')
        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        tam = cursorObj.fetchall()
        if tam[0][0] is not None:
            id_cuaderno = int(tam[0][0])+1
        else:
            id_cuaderno = 1 
        id_proy = self.id_proy
        titulo = self.e_titulo.get_text()
        if titulo == "":
            print("debes completar algun nombre")
            return False
        contenido = self.p_buffer.get_text(self.p_buffer.get_start_iter(),
                                      self.p_buffer.get_end_iter(), True)
        fecha_alt = time.strftime("%d/%m/%y"),
        status = 1

        n_cod = [int(id_cuaderno),
                 int(id_proy),
                 titulo,
                 contenido,
                 fecha_alt[0],
                 int(status)]
        print(n_cod)
        cursorObj.execute('INSERT INTO cuaderno(id_cuaderno, id_proy, nombre_cuad, memo, fecha_alt, status) VALUES( ?, ?, ?,?,? ,?)', n_cod)
        self.con.commit()
        self.padre.actualizar_tabla(widget)
        self.ventana.hide()


