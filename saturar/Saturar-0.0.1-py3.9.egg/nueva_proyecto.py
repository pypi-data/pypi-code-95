#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# creador de proyectos para SATURAR
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
import gi
import os.path
import time
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class NUEVO_PROYECTO(object):

    """Docstring for NUEVO_PROYECTO. """

    def __init__(self, saturar):
        """TODO: to be defined. """
        #######################################################################
        # Variables globales de la clase
        #######################################################################
        self.__saturar = saturar
        #######################################################################
        self.ventana = Gtk.Window()
        self.ventana.set_modal(True)
        vbox1 = Gtk.VBox()
        frame_proy = Gtk.Frame(label="Proyecto")
        l_nom_proy = Gtk.Label("Titulo")
        self.e_nom_proy = Gtk.Entry()
        hb_proy1 = Gtk.HBox()
        hb_proy1.pack_start(l_nom_proy, False, True, 0)
        hb_proy1.pack_start(self.e_nom_proy, False, True, 10)
        vb_proy = Gtk.VBox()
        vb_proy.pack_start(hb_proy1, False, True, 0)
        ######################################################################
        #  configuraciones del textview
        ######################################################################
        frame = Gtk.Frame(label="Memo:")
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

        vb_proy.pack_start(frame, True, True, 0)
        frame_proy.add(vb_proy)
        ######################################################################

        frame_inv = Gtk.Frame(label="Investigador")
        l_nom_inv = Gtk.Label("Nombre")
        self.e_nom_inv = Gtk.Entry()
        l_ape_inv = Gtk.Label("Apellido")
        self.e_ape_inv = Gtk.Entry()
        hb_proy2 = Gtk.HBox()
        hb_proy2.pack_start(l_nom_inv, False, True, 0)
        hb_proy2.pack_start(self.e_nom_inv, False, True, 10)
        hb_proy3 = Gtk.HBox()
        hb_proy3.pack_start(l_ape_inv, False, True, 0)
        hb_proy3.pack_start(self.e_ape_inv, False, True, 10)
        vb_inv = Gtk.VBox()
        vb_inv.pack_start(hb_proy2, False, True, 0)
        vb_inv.pack_start(hb_proy3, False, True, 0)
        frame_inv.add(vb_inv)
        vbox1.pack_start(frame_proy, True, True, 10)
        vbox1.pack_start(frame_inv, False, True, 10)
        #######################################################################
        # botones
        #######################################################################
        boton_canc = Gtk.Button("Cancelar")
        boton_sig = Gtk.Button("Siguiente")
        boton_canc.connect("clicked", self.cancelar)
        boton_sig.connect("clicked", self.siguiente)
        hb_proy3 = Gtk.HBox()
        hb_proy3.pack_end(boton_sig, False, False, 0)
        hb_proy3.pack_end(boton_canc, False, False, 0)

        vbox1.pack_start(hb_proy3, False, True, 0)
        self.ventana.add(vbox1)
        self.ventana.show_all()

    def cancelar(self, widget):
        """TODO: Docstring for cancelar.

        :widget: objeto boton

        """
        self.ventana.hide()

    def siguiente(self, widget):
        """TODO: Docstring for siguiente.

        :widget: objeto boton

        """
        dialog = Gtk.FileChooserDialog(
            title="Seleccione un nombre para el archivo",
            parent=self.ventana, action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        self.add_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            nombre_arch = dialog.get_filename()
            nom, ext = os.path.splitext(nombre_arch)
            #if ext == "":
            #    ext = ".db"
            print("-----------------",nom)
            os.mkdir(nom)
            os.mkdir(nom+"/img")
            nombre_arch = nom + "/saturar.db"
            crear = self.crear_pr(nombre_arch)
            dialog.destroy()
            return crear
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def crear_pr(self, arch):
        """TODO: Docstring for crear_pr.

        :arch: string, nombre del archivo para crear la DB
        :returns: TRUE

        """
        titulo = self.e_nom_proy.get_text()
        nombre = self.e_nom_inv.get_text()
        ape = self.e_ape_inv.get_text()
        memo = self.p_buffer.get_text(self.p_buffer.get_start_iter(),
                                      self.p_buffer.get_end_iter(), True)
        if titulo == "" or nombre == "" or ape == "":
            print("error, debes completar todos los datos")
            return False
        else:
            con = self.conn(arch)
            cursorObj = con.cursor()
            cursorObj.execute("CREATE TABLE pagina(id_pagina integer PRIMARY KEY,id_cuaderno integer, titulo text, contenido text,fecha_alt text, status integer, tipo text)")
            cursorObj.execute("CREATE TABLE codificacion(id_codificacion integer PRIMARY KEY,id_cod integer,id_prop integer,id_pagina integer, text_cod text, c_ini integer, c_fin integer, fecha_alt text, status integer, memo text)")
            cursorObj.execute("CREATE TABLE codigo(id_cod integer PRIMARY KEY, nombre_cod text, color text ,memo text, id_prop integer, fecha_alt text, status integer)")
            cursorObj.execute("CREATE TABLE cuaderno(id_cuaderno integer PRIMARY KEY,id_proy integer ,nombre_cuad text, memo text , fecha_alt text, status integer)")
            cursorObj.execute("CREATE TABLE proyecto(id_proy integer PRIMARY KEY,id_prop integer ,nombre text, memo text , fecha_alt text, status integer)")
            cursorObj.execute("CREATE TABLE investigador(id_prop integer PRIMARY KEY,nombre text, apellido text , fecha_alt text, status integer)")
            cursorObj.execute("CREATE TABLE categoria(id_cat integer PRIMARY KEY, nombre_cat text, color text ,memo text, id_prop integer, fecha_alt text, status integer)")
            cursorObj.execute("CREATE TABLE cod_axial(id_axial integer PRIMARY KEY, id_cod int, id_cat int, fecha_alt text, status integer)")
            con.commit()
            fecha_alt = time.strftime("%d/%m/%y")
            status = 1
            base_proy = (1, 1, titulo, memo, fecha_alt[0], status)
            base_inv = (1, nombre, ape, fecha_alt[0], status)
            cursorObj.execute('INSERT INTO investigador(id_prop, nombre, apellido, fecha_alt, status) VALUES(?, ?, ?, ?, ?)', base_inv)
            cursorObj.execute('INSERT INTO proyecto(id_proy, id_prop,nombre, memo, fecha_alt, status) VALUES(?, ?, ?, ?, ?, ?)', base_proy)
            con.commit()
            self.__saturar.cargar(arch)
            self.ventana.hide()

    def add_filters(self, dialog):
        filter_db = Gtk.FileFilter()
        filter_db.set_name("archivos saturar")
        filter_db.add_mime_type("text/db")
        dialog.add_filter(filter_db)

    def conn(self, arch):
        """TODO: Docstring for conn.

        :arch: String con el nombre del archivo de conexón
        :returns: objeto SQLite

        """
        try:
            con = sqlite3.connect(arch)
            return con
        except Exception:
            print(Exception)
            return False


#N = NUEVO_PROYECTO()
#print("aca bla bla bla bla")
#Gtk.main()
