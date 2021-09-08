#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# Visor de reportes textuales
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
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import os
from ..utils import DIALOGOS
from pathlib import Path
class VISOR_REPORTES(object):

    """Docstring for VISOR_REPORTES. """

    def __init__(self, texto):
        """TODO: to be defined. """
        self.ruta = str(Path.home()) + "/"
        self.ventana = Gtk.Window()
        self.ventana.set_title("Visor de reporte")
        self.ventana.resize(800,600)

        
        self.mensajes = DIALOGOS(self.ventana)
        vbox = Gtk.VBox()

        scrolltext = Gtk.ScrolledWindow()
        scrolltext.set_hexpand(True)
        scrolltext.set_vexpand(True)
        frame = Gtk.Frame()
        #frame.set_label("Resultado")
        frame.set_shadow_type(1)
        hbox = Gtk.HBox()
        ######################################################################
        #  configuraciones del textview
        ######################################################################
        # Widget con el textview donde se visualizan el texto a codificar
        self.pagina = Gtk.TextView()
        # Deshabilito la edición del textview
        self.pagina.set_editable(False)
        # Corto el texto en las palabras si se pasan del tamaño del textview
        self.pagina.set_wrap_mode(Gtk.WrapMode.WORD)
        self.p_buffer = self.pagina.get_buffer()
        self.p_buffer.set_text(texto)
        scrolltext.add(self.pagina)
        frame.add(scrolltext)
        boton_pdf = Gtk.Button("Exportar PDF")
        boton_html = Gtk.Button("Exportar HTML")
        boton_pdf.connect("clicked",self.boton_pdf_aceptar)
        boton_html.connect("clicked",self.boton_html_aceptar)
        hbox.pack_start(boton_pdf, True, True, 0)
        hbox.pack_start(boton_html, True, True, 0)
        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.ventana.add(vbox)
        self.ventana.show_all()

    def obtener_text(self):
        """TODO: Docstring for obtener_text.
        :returns: TODO

        """
        
        texto = self.p_buffer.get_text(self.p_buffer.get_start_iter(),
                                       self.p_buffer.get_end_iter(),
                                       True)
        return texto

    def boton_html_aceptar(self, widget):
        """TODO: Docstring for boton_pdf_aceptar.
        :returns: TODO

        """

        print("preparo el html")
        texto = self.obtener_text()
        tmp = self.ruta+"temp.md"
        archivo = open(tmp,"w")
        archivo.writelines(texto)
        archivo.close()
        html = "pandoc "+tmp+" -o " +self.ruta+"reporte.html"
        os.system(html)
        self.mensajes.informacion(texto = "el archivo fue creado correctamente",
                                    subtexto = "con el nombre 'reporte.html', cargado en el home")

    def boton_pdf_aceptar(self, widget):
        """TODO: Docstring for boton_pdf_aceptar.
        :returns: TODO

        """
        texto = self.obtener_text()
        tmp = self.ruta + "temp.md"
        archivo = open(tmp, "w")

        archivo.writelines(texto)
        archivo.close()
        html = "pandoc "+tmp+" -o"  +self.ruta+"temp.html"

        os.system(html)
        pdf =  "pandoc " + self.ruta + "temp.html" + " -o ~/reporte.pdf"
        os.system(pdf)
        #os.system("rm ~temp.md")
        self.mensajes.informacion(texto = "el archivo fue creado correctamente",
                                    subtexto = "con el nombre 'reporte.pdf', cargado en el home")
#VISOR_REPORTES("hola")
#Gtk.main()
