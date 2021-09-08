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


class NUEVA_PAGINA(object):

    """Docstring for NUEVA_PAGINA. """

    def __init__(self, con, id_cuaderno, padre):
        """
        """
        self.padre = padre
        self.con = con
        self.id_cuaderno = id_cuaderno
        self.ventana = Gtk.Window(title="cargador de páginas")
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
        frame = Gtk.Frame(label="texto de la página:")
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
        boton_importar = Gtk.Button("importar txt")
        boton_importar.connect("clicked", self.importar)
        boton_cancelar.connect("clicked", self.cancelar)

        hbox_b = Gtk.HBox()
        hbox_b.pack_start(boton_cancelar, False, True, 0)
        hbox_b.pack_start(boton_importar, False, True, 0)
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
        tipo
        """
        cod_tam = ('SELECT MAX(id_pagina) FROM pagina')
        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        tam = cursorObj.fetchall()
        if tam[0][0] is not None:
            id_pagina = int(tam[0][0])+1
        else:
            id_pagina = 1
        id_cuaderno = self.id_cuaderno
        titulo = self.e_titulo.get_text()
        if titulo == "":
            print("debes completar algun nombre")
            return False
        contenido = self.p_buffer.get_text(self.p_buffer.get_start_iter(),
                                      self.p_buffer.get_end_iter(), True)
        fecha_alt = time.strftime("%d/%m/%y"),
        status = 1

        n_cod = [int(id_pagina),
                 int(id_cuaderno),
                 titulo,
                 contenido,
                 fecha_alt[0],
                 int(status),
                 "texto"]

        cursorObj.execute('INSERT INTO pagina(id_pagina, id_cuaderno, titulo, contenido, fecha_alt, status,tipo) VALUES( ?, ?, ?,?,? ,?,?)', n_cod)
        self.con.commit()
        self.padre.actualizar_tabla(widget)
        self.ventana.hide()



    def importar(self, widget):
        """TODO: Docstring for importar.

        :widget: TODO
        :returns: TODO

        """
        print("importar")
        dialog = Gtk.FileChooserDialog(
                    title="Seleccione un archivo TXT", 
                    parent=self.ventana,
                    action=Gtk.FileChooserAction.OPEN
                    )
        dialog.add_buttons(
                            Gtk.STOCK_CANCEL,
                            Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OPEN,
                            Gtk.ResponseType.OK,)

        self.add_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            arch = dialog.get_filename()
            #if arch.split(".")[-1] == "pdf":
            #    self.cargar_pdf(arch)
            #else:
            self.cargar_txt(arch)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

    # def cargar_pdf(self, arch):
        # """TODO: Docstring for cargar_pdf.

        # :arch: TODO
        # :returns: TODO

        # """
        # with open(arch, "rb") as f:
            # pdf = pdftotext.PDF(f)
        # cadena = "\n\n".join(pdf)
        # self.p_buffer.set_text(cadena)
    
    def cargar_txt(self, arch):
        """TODO: Docstring for cargar_txt.

        :arch: TODO
        :returns: TODO

        """
        a_txt = open(arch, "r")
        cadena = "\n\n".join(a_txt.readlines())
        a_txt.close()
        self.p_buffer.set_text(cadena)

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("archivos TXT")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("Archivos PDF")
        filter_pdf.add_pattern("*.pdf")
        dialog.add_filter(filter_pdf)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Cualquier archivo")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)


 
