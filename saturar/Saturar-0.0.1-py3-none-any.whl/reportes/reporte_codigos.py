#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# Sistema para generar reportes de códigos
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

import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from ..reportes.saturapi import SATURAPI
from ..reportes.visor_reportes import  VISOR_REPORTES
from pathlib import Path
class REPORTE_CODS(object):

    """Docstring for REPORTE_CODS. """

    def __init__(self, sql):
        """TODO: to be defined. """
        self.archivo = sql
        self.s = SATURAPI()
        self.s.conectar(sql)
        self.id_cod = None
        self.ventana = Gtk.Window()
        self.ventana.set_title("reporte de códigos")
        vbox = Gtk.VBox()
        cod_cargados = self.cargar_cod()
        drp_cod = Gtk.ComboBox.new_with_model_and_entry(cod_cargados)
        drp_cod.set_entry_text_column(1)
        b_aceptar = Gtk.Button("Aceptar")
        b_aceptar.connect("clicked", self.aceptar)
        drp_cod.connect("changed", self.cambio)
        vbox.pack_start(drp_cod, True, True, 0)
        vbox.pack_start(b_aceptar, True, True, 0)
        self.ventana.add(vbox)
        self.ventana.show_all()

    def aceptar(self, widget):
        """TODO: Docstring for aceptar.
        :returns: TODO

        """
        cods = """## Código {}

### ID: **{}**

---

"""

        mkd_cod = """### Reporte ###

Titulo cuaderno: **{}**

Titulo página: **{}**

tipo de registro: **{}**

fecha de codificación: **{}**


"""

        mkd_text = """Carácter inicial: **{}**

Carácter final: **{}**

### Texto recuperado: ###
{}

### Memo ###

{}

---

"""
        mkd_img = """Milisegundo inicial: **{}**

Milisegundo final: **{}**

### Imagen: ###

<img src="{}" alt=""
	title="" width="400" />

### Transcripción: ###
{}

### Memo ###

{}

---

"""
        sel_cod = self.id_cod
        s = self.s
        codigos = s.recuperar_codigos()
        arch = ""
        for c in codigos:
            if c['id_cod'] == sel_cod:
                codi = c['nombre_cod']
                cid = c['id_cod']
                arch = arch + cods.format(codi,cid)
        codifi = s.recuperar_codificado(sel_cod)
        for a in codifi:
            datos = []
            pag = s.recuperar_pagina_especifica(str(a['id_pagina']))
            cuad = s.recuperar_cuaderno_especifico(str(pag[0]['id_cuaderno']))
            datos.append(str(cuad[0]['nombre_cuad']) )
            datos.append(str(pag[0]['titulo']))
            tipo = str(pag[0]['tipo'])
            datos.append(tipo)
            fech = a['fecha_creac']
            datos.append(fech)
            #datos.append(c_ini)
            #datos.append(c_fin)
            cod_f = mkd_cod.format(*datos)
            texto = a['text_cod']
            #datos.append(texto)
            memo = a['memo']
            #datos.append(texto)
            if tipo == "texto":
                c_ini = str(a['c_ini'])
                c_fin = str(a['c_fin'])

                cod_c = mkd_text.format(c_ini,c_fin,texto,memo)
            elif tipo == "multimedia":
                c_ini = str(a['c_ini'])
                c_fin = str(a['c_fin'])
                direc = os.path.split(self.archivo)
                im = direc[0] + "/img/" + str(a['id_codificacion'] + ".png")
                cod_c = mkd_img.format(c_ini,c_fin,im,texto,memo)
            arch = arch + cod_f + cod_c
        VISOR_REPORTES(arch)


    def cargar_cod(self):
        """TODO: Docstring for cargar_cod.
        :returns: TODO

        """
        name_store = Gtk.ListStore(str, str)
        codigos = self.s.recuperar_codigos()
        for c in codigos:
            name_store.append([c['id_cod'],c['nombre_cod']])

        return name_store
    
    def cambio(self, widget):
        """TODO: Docstring for cambio.
        :returns: TODO

        """
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:
            model = widget.get_model()
            id = model[tree_iter][0]
            #print("Selected: country=%s" % country)
            self.id_cod = id

#C = REPORTE_CODS ( "/home/vbasel/Doctorado/owncloud/saturar/doctorado_valen_2020.db")
#Gtk.main()
