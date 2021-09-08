#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# SATURAR, software para codificación y analisis basado en 
# teoría fundamentada
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
import os
import vlc
import sys

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from .utils import DIALOGOS
from .codificar import CODIFICAR
from .codigos import CODIGOS
from .paginas import PAGINAS
from .cuadernos import CUADERNOS
from .categorias import CATEGORIA
from .categorizacion import CATEGORIZAR
from .nueva_proyecto import NUEVO_PROYECTO
from .multimedia import VideoPlayer
from .reportes.reporte_codigos import REPORTE_CODS
from .reportes.reporte_nube import REPORTE_NUBES
from .reportes.reporte_nodos import REPORTE_NODOS
from .reportes.buscador import BUSCADOR
class SATURAR(object):

    """Clase central de SATURAR. con el manejador de archivos y carga """

    def __init__(self):
        """TODO: to be defined. """
        #######################################################################
        # Variables globales del proyecto
        #######################################################################
        self.proyecto = ""
        self.id_cuad = 1
        ruta_s = os.path.dirname(os.path.abspath( __file__ ))
        if 'linux' in sys.platform:
            # Inform libvlc that Xlib is not initialized for threads
            #print("inicio vlc --no-xlib")
            self.vlcinstance = vlc.Instance("--no-xlib")
        else:
            self.vlcinstance = vlc.Instance()
        #######################################################################
        # inicio la ventana central
        #######################################################################
        version = "0.1"
        nombre = "versión " + version
        self.ventana = Gtk.Window()
        self.ventana.set_title(nombre)
        self.ventana.maximize()
        hbox_header = Gtk.HBox()
        self.cuaderno = None

        self.mensajes = DIALOGOS(self.ventana)
        # "accessories-calculator" 
        #######################################################################
        # Creo el boton de menu principal con su popover
        #######################################################################
        boton_menu = Gtk.Button()#.new_from_icon_name("open-menu-symbolic", 1)

        menu_img = Gtk.Image.new_from_file(ruta_s + "/img/menu.png")
        boton_menu.set_image(menu_img)
        popover = Gtk.PopoverMenu.new()
        popover.set_relative_to(boton_menu)
        boton_menu.connect("clicked", self.boton_click, popover)
        pbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        popover.add(pbox)
        nuevo = Gtk.ModelButton.new()
        nuevo.set_property('margin', 10)
        nuevo.set_label("Nuevo proyecto")
        nuevo.connect("clicked", self.nuevo_proyecto)
        abrir_p = Gtk.ModelButton.new()
        abrir_p.set_property('margin', 10)
        abrir_p.set_label("Abrir proyecto")
        abrir_p.connect("clicked", self.abrir_proyecto)
        cerrar_p = Gtk.ModelButton.new()
        cerrar_p.set_property('margin', 10)
        cerrar_p.set_label("Salir")
        cerrar_p.connect("clicked", self.salir)
        pbox.pack_start(nuevo, False, False, 0)
        pbox.pack_start(abrir_p, False, False, 0)
        pbox.pack_start(cerrar_p, False, False, 0)
        hbox_header.pack_start(boton_menu, True, True, 0)
        ######################################################################

        #######################################################################
        # Creo el boton de para operaciones con su popover
        #######################################################################
        self.boton_menu_c = Gtk.Button()# .new_from_icon_name("accessories-calculator", 1)
        self.boton_menu_c.set_sensitive(False)
        menu_c_img = Gtk.Image.new_from_file(ruta_s + "/img/reportes.png")
        self.boton_menu_c.set_image(menu_c_img)
        popover_c = Gtk.PopoverMenu.new()
        popover_c.set_relative_to(self.boton_menu_c)
        self.boton_menu_c.connect("clicked", self.boton_click_c, popover_c)
        pbox_c = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        popover_c.add(pbox_c)
        oper1 = Gtk.ModelButton.new()
        oper1.set_property('margin', 10)
        oper1.set_label("Reporte de Códigos")
        oper1.connect("clicked", self.reporte_cod)
        pbox_c.pack_start(oper1, False, False, 0)

        oper2 = Gtk.ModelButton.new()
        oper2.set_property('margin', 10)
        oper2.set_label("Reporte de Códigos mediante nodos")
        oper2.connect("clicked", self.reporte_nod)
        pbox_c.pack_start(oper2, False, False, 0)

        oper3 = Gtk.ModelButton.new()
        oper3.set_property('margin', 10)
        oper3.set_label("Nube de palabras")
        oper3.connect("clicked", self.nube_palabras)
        pbox_c.pack_start(oper3, False, False, 0)


        hbox_header.pack_start(self.boton_menu_c, True, True, 0)
        #######################################################################
        # Creo el boton de para busqueda con su popover
        #######################################################################
        self.boton_menu_d = Gtk.Button()# .new_from_icon_name("accessories-calculator", 1)
        self.boton_menu_d.set_sensitive(False)
        menu_d_img = Gtk.Image.new_from_file(ruta_s + "/img/buscar.png")
        self.boton_menu_d.set_image(menu_d_img)
        popover_d = Gtk.PopoverMenu.new()
        popover_d.set_relative_to(self.boton_menu_d)
        self.boton_menu_d.connect("clicked", self.boton_click_d, popover_d)
        pbox_d = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        popover_d.add(pbox_d)
        operd1 = Gtk.ModelButton.new()
        operd1.set_property('margin', 10)
        operd1.set_label("Buscar")
        operd1.connect("clicked", self.buscador)
        pbox_d.pack_start(operd1, False, False, 0)
        hbox_header.pack_start(self.boton_menu_d, True, True, 0)
        ######################################################################
        self.ventana.connect("destroy", Gtk.main_quit)
        headerbar = Gtk.HeaderBar()
        headerbar.set_title("SATURAR")
        headerbar.set_subtitle(version)
        headerbar.set_show_close_button(True)
        headerbar.add(hbox_header)
        self.ventana.set_titlebar(headerbar)
        self.paginas = Gtk.Notebook()

        self.paginas.set_tab_pos(Gtk.PositionType.LEFT)

        ######################################################################
        # crear paginas
        ######################################################################
        self.caja_cuaderno = Gtk.HBox()
        cuad_h = Gtk.HBox()
        cuad_lab = Gtk.Label("Cuadernos")
        cuad_img = Gtk.Image.new_from_file(ruta_s + "/img/cuaderno.png")
        cuad_h.pack_start(cuad_img, True, True, 10)
        cuad_h.pack_start(cuad_lab, True, True, 0)
        self.p_cuaderno = Gtk.Box()
        self.p_cuaderno.set_border_width(5)
        self.p_cuaderno.add(self.caja_cuaderno)
        self.paginas.append_page(self.p_cuaderno, cuad_h)
        cuad_h.show_all()


        pag_h = Gtk.HBox()
        pag_lab = Gtk.Label("Paginas")
        pag_img = Gtk.Image.new_from_file(ruta_s + "/img/paginas.png")
        pag_h.pack_start(pag_img, True, True, 10)
        pag_h.pack_start(pag_lab, True, True, 0)
        self.caja_pagina = Gtk.HBox()
        self.p_paginas = Gtk.Box()
        self.p_paginas.set_border_width(5)
        self.p_paginas.add(self.caja_pagina)
        self.paginas.append_page(self.p_paginas, pag_h)
        pag_h.show_all()

        cod_h = Gtk.HBox()
        cod_lab = Gtk.Label("Códigos")
        cod_img = Gtk.Image.new_from_file(ruta_s + "/img/codigos.png")
        cod_h.pack_start(cod_img, True, True, 10)
        cod_h.pack_start(cod_lab, True, True, 0)
        self.caja_cod = Gtk.HBox()
        self.page_cod = Gtk.Box()
        self.page_cod.set_border_width(5)
        self.page_cod.add(self.caja_cod)
        self.paginas.append_page(self.page_cod, cod_h)
        cod_h.show_all()

        codi_h = Gtk.HBox()
        codi_lab = Gtk.Label("Codificar")
        codi_img = Gtk.Image.new_from_file(ruta_s + "/img/codificar.png")
        codi_h.pack_start(codi_img, True, True, 10)
        codi_h.pack_start(codi_lab, True, True, 0)
        self.p_codific = Gtk.Box()
        self.p_codific.set_border_width(5)
        self.caja_codific = Gtk.HBox()
        self.p_codific.add(self.caja_codific)
        self.paginas.append_page(self.p_codific, codi_h)
        codi_h.show_all()

        cat_h = Gtk.HBox()
        cat_lab = Gtk.Label("Categorias")
        cat_img = Gtk.Image.new_from_file(ruta_s + "/img/categorias.png")
        cat_h.pack_start(cat_img, True, True, 10)
        cat_h.pack_start(cat_lab, True, True, 0)
        self.p_categoria = Gtk.Box()
        self.p_categoria.set_border_width(5)
        self.caja_categoria = Gtk.HBox()
        self.p_categoria.add(self.caja_categoria)
        self.paginas.append_page(self.p_categoria, cat_h)
        cat_h.show_all()

        cate_h = Gtk.HBox()
        cate_lab = Gtk.Label("Categorizar")
        cate_img = Gtk.Image.new_from_file(ruta_s + "/img/categorizar.png")
        cate_h.pack_start(cate_img, True, True, 10)
        cate_h.pack_start(cate_lab, True, True, 0)
        self.p_cod_ax = Gtk.Box()
        self.p_cod_ax.set_border_width(5)
        self.caja_cod_ax = Gtk.HBox()
        self.p_cod_ax.add(self.caja_cod_ax)
        self.paginas.append_page(self.p_cod_ax, cate_h)
        cate_h.show_all()
        self.ventana.add(self.paginas)
        self.paginas.connect("switch-page", self.boton_pagina)
        self.paginas.set_show_tabs(False)
        self.ventana.show_all()

    def reporte_nod(self, widget):
        """TODO: Docstring for reporte_nod.
        :returns: TODO

        """
        print("nodos")
        REPORTE_NODOS(self.arch)
        return True

    def nube_palabras(self, widget):
        """TODO: Docstring for reporte_nod.
        :returns: TODO

        """
        #print("nodos")
        REPORTE_NUBES(self.arch)
        return True

    def reporte_cod(self, widget):
        """TODO: Docstring for reporte.

        :widget: Representa el widget del boton que esta en el menu
        :returns: True

        """
        print(widget)
        REPORTE_CODS(self.arch)
        return True

    def salir(self, widget):
        """TODO: Docstring for salir.

        :widget: TODO
        :returns: TODO

        """
        Gtk.main_quit()

    def nuevo_proyecto(self, widget):
        """TODO: Docstring for nuevo_proyecto.
        :returns: TODO

        """
        NP = NUEVO_PROYECTO(self)

    def abrir_proyecto(self, widget):
        """TODO: Docstring for nuevo_proyecto.

        :widget: TODO
        :returns: TODO

        """
        dialog = Gtk.FileChooserDialog(
                    title="Seleccione un archivo PDF o TXT", 
                    parent=self.ventana,
                    action=Gtk.FileChooserAction.OPEN
                    )
        dialog.add_buttons(
                            Gtk.STOCK_CANCEL,
                            Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OPEN,
                            Gtk.ResponseType.OK,)

        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("Archivos sqlite")
        filter_pdf.add_pattern("*.db")
        dialog.add_filter(filter_pdf)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            arch = dialog.get_filename()
            self.cargar(arch)

        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

    def cargar(self, arch):
        """TODO: Docstring for cargar.

        :arg1: TODO
        :returns: TODO

        """

        self.arch = arch
        self.con = sqlite3.connect(arch)  # "saturar2.db")
        self.page_cod.remove(self.caja_cod)
        self.caja_cod = Gtk.HBox()
        self.page_cod.add(self.caja_cod)
        CODIGOS(1, self.con, self.caja_cod, self.arch)



        self.p_paginas.remove(self.caja_pagina)
        self.caja_pagina = Gtk.HBox()
        self.p_paginas.add(self.caja_pagina)
        self.t_paginas = PAGINAS(self.id_cuad, 
                                 self.con, 
                                 self.caja_pagina,
                                 self.ventana)


        self.p_categoria.remove(self.caja_categoria)
        self.caja_categoria = Gtk.HBox()
        self.p_categoria.add(self.caja_categoria)
        self.t_categoria = CATEGORIA(self.id_cuad, self.con, self.caja_categoria)

        self.p_cuaderno.remove(self.caja_cuaderno)
        self.caja_cuaderno = Gtk.HBox()
        self.p_cuaderno.add(self.caja_cuaderno)
        self.cuaderno = CUADERNOS(1,
                                  self.con,
                                  self.caja_cuaderno,
                                  self.t_paginas) 
        self.p_cod_ax.remove(self.caja_cod_ax)
        self.caja_cod_ax = Gtk.HBox()
        self.p_cod_ax.add(self.caja_cod_ax)
        self.categorizar = CATEGORIZAR(1, self.con,self.caja_cod_ax)
        self.paginas.set_show_tabs(True)
        self.boton_menu_c.set_sensitive(True)
        self.boton_menu_d.set_sensitive(True)

    def boton_click(self, button, popover):
        if popover.get_visible():
            popover.hide()
        else:
            popover.show_all()

    def boton_click_c(self, button, popover):
        if popover.get_visible():
            popover.hide()
        else:
            popover.show_all()

    def boton_click_d(self, button, popover):
        if popover.get_visible():
            popover.hide()
        else:
            popover.show_all()

    def buscador(self, arg1):
        """TODO: Docstring for buscador.

        :arg1: TODO
        :returns: TODO

        """
        c = BUSCADOR(self.arch,self)
        print ("inicio la busqueda")

    def buscar(self, id_p, caracter):
        """TODO: Docstring for buscar.

        :arg1: TODO
        :returns: TODO

        """
        print("buscar")


        self.paginas.set_current_page(3)
        self.p_codific.remove(self.caja_codific)
        self.caja_codific = Gtk.HBox()
        # id_pag = self.t_paginas.obtener_id_pag()
        id_prop = 1
        self.c = CODIFICAR(id_p, id_prop, self.con, self.caja_codific,self.ventana)
        self.p_codific.add(self.caja_codific)
        self.c.entry_salt.set_text(str(caracter))
        #self.c.pagina.set_can_focus(True)
        self.ventana.set_focus(self.c.bot_salt)
        #self.c.iniciar_en_caract(2159)
        self.c.bot_salt.activate()




    def boton_pagina(self, a, b, c):
        """ C == valor entero que representa cada pagina empensando por
        el numero 0
        :returns: TODO

        """
        print(a)
        print(b)
        print(c)
        print("pagi:",self.paginas.get_current_page())
        if self.paginas.get_current_page() == -1:
            return False
        if c == 1 and self.cuaderno is not None:
            if self.cuaderno.id_cuad is None:
                self.mensajes.error(texto="Debes elegir un cuaderno antes.",
                                    subtexto="se seleccionara el primer cuaderno de la lista")
                self.paginas.set_current_page(0)
            else:
                self.id_cuad = self.cuaderno.obtener_id_cuad()
                self.p_paginas.remove(self.caja_pagina)
                self.caja_pagina = Gtk.HBox()
                self.p_paginas.add(self.caja_pagina)
                self.t_paginas = PAGINAS(self.id_cuad, 
                                         self.con, 
                                         self.caja_pagina,
                                         self.ventana)



        if c == 2:
            pass

        if c == 3:
            self.p_codific.remove(self.caja_codific)
            self.caja_codific = Gtk.HBox()
            id_pag = self.t_paginas.obtener_id_pag()
            tipo_pag = self.t_paginas.obtener_tipo_pag()
            print("el tipo de archivo es: ", tipo_pag)
            id_prop = 1
            if tipo_pag == "texto":
                self.c = CODIFICAR(id_pag, 
                                   id_prop, 
                                   self.con,
                                   self.caja_codific,
                                   self.ventana)
                self.p_codific.add(self.caja_codific)
            # esta parte le falta, hay que meter todo en una clase.. y esta el problema
            # de la variable global instance 
            elif tipo_pag == "multimedia":
                self.c =  VideoPlayer(self.con,
                                      id_prop,
                                      id_pag,
                                      self.caja_codific,
                                      self.arch,
                                      self.vlcinstance,
                                      self.ventana)
                self.c.main()

                self.p_codific.pack_start(self.caja_codific,True, True,0)

        if c == 5:
            pass
            self.categorizar.actualizar_tabla(None)
            self.categorizar.actualizar_tabla_cat_cod(None)
            self.categorizar.actualizar_tabla_cod(None)


