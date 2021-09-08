#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# Reporte de nubes de palabras
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
from gi.repository import Gtk#, Gdk
#from reportes.saturapi import SATURAPI
#import numpy as np
#import pandas as pd
from os import path
#from PIL import Image

from nltk.corpus import stopwords
from wordcloud import WordCloud

#from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
#from nltk.corpus import stopwords
import pandas as pd 


from ..reportes.saturapi import SATURAPI
#from saturapi import SATURAPI

import matplotlib
matplotlib.use('TkAgg')  # or 'GTK3Cairo'
import matplotlib.pyplot as plt

from ..utils import DIALOGOS

class REPORTE_NUBES(object):

    """Docstring for REPORTE_NUBES. """

    def __init__(self, sql):
        """TODO: to be defined. """
        self.s = SATURAPI()
        self.s.conectar(sql)
        self.archivo = sql
        self.id_pag = None
        self.ventana = Gtk.Window()
        self.ventana.set_title("Nubes de palabras")

        self.mensajes = DIALOGOS(self.ventana)
        vbox = Gtk.VBox()
        pag_cargados = self.pag_cargados()
        drp_cod = Gtk.ComboBox.new_with_model_and_entry(pag_cargados)
        drp_cod.set_entry_text_column(1)
        hbox1 = Gtk.HBox()
        l_max_font = Gtk.Label("cantidad maxima de palabras")
        ad1 = Gtk.Adjustment(1, 1, 1000, 1.0, 0, 0)
        self.e_max_font = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=ad1)
        self.e_max_font.set_digits(0)
        hbox1.pack_start(l_max_font, False, True, 0)
        hbox1.pack_start(self.e_max_font, True, True, 0)
        hbox2 = Gtk.HBox()
        l_font_tam = Gtk.Label("Tamaño de la fuente")
        ad2 = Gtk.Adjustment(10, 1, 1000, 1.0, 0, 0)
        self.e_font_tam = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=ad2)
        self.e_font_tam.set_digits(0)
        hbox2.pack_start(l_font_tam, False, True, 0)
        hbox2.pack_start(self.e_font_tam, True, True, 0)
        hbox3 = Gtk.HBox()
        l_stop = Gtk.Label("palabras vacias")
        self.e_stop = Gtk.Entry()
        hbox3.pack_start(l_stop, False, True, 0)
        hbox3.pack_start(self.e_stop, True, True, 0)
        b_aceptar = Gtk.Button("Aceptar")
        b_aceptar.connect("clicked", self.aceptar)
        drp_cod.connect("changed", self.cambio)
        vbox.pack_start(drp_cod, True, True, 0)
        vbox.pack_start(hbox1, True, True, 0)
        vbox.pack_start(hbox2, True, True, 0)
        vbox.pack_start(hbox3, True, True, 0)
        vbox.pack_start(b_aceptar, True, True, 0)
        self.ventana.connect("destroy", self.cerrar)
        self.ventana.add(vbox)
        self.ventana.show_all()

    def cerrar(self, arg1):
        """TODO: Docstring for cerrar.

        :arg1: TODO
        :returns: TODO

        """
        print("cierro nube")
        self.ventana.hide()

    def cambio(self, widget):
        """TODO: Docstring for cambio.
        :returns: TODO

        """
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:
            model = widget.get_model()
            id = model[tree_iter][0]
            self.id_pag = id

    def aceptar(self, arg1):
        """TODO: Docstring for aceptar.

        :arg1: TODO
        :returns: TODO

        """
        max_text = int(self.e_max_font.get_value())
        text_tam = int(self.e_font_tam.get_value())
        palabras_stop = self.e_stop.get_text()
        palabras_stop = palabras_stop.split(",")
        if self.id_pag is not None:
            pag = self.s.recuperar_pagina_especifica(self.id_pag)
            texto = pag[0]['contenido']
            texto = texto.lower()
            #self.nube(texto,"nube")
            self.nube_palabras(texto,
                               self.archivo,
                               max_text,
                               text_tam,
                               palabras_stop)
        else:
            self.mensajes.error(texto="Error.",
                                    subtexto="Debes elegir una página")

    def nube_palabras(self, text, arch, max_text, text_tam, palabras_stop):
        """TODO: Docstring for nube_palabras.
        :returns: TODO

        """
        stop = set(stopwords.words('spanish')) | set(stopwords.words('english'))
        stop.update(palabras_stop)

        wordcloud = WordCloud(stopwords=stop,
                              max_font_size=text_tam,
                              max_words=max_text,
                              scale=3,
                              random_state=3,
                              background_color="white").generate(text)
        wordcloud.recolor(random_state=1)

       

        #wordcloud_svg = wordcloud.to_svg()
        #ruta = path.dirname(arch)
        #f = open(ruta + "/nube2.svg", "w+")
        #f.write(wordcloud_svg)
        #f.close()

        plt.figure(figsize=(20, 15))
        #plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()
        #plt.close()



    def pag_cargados(self):
        """TODO: Docstring for pag_cargados.

        :widget: TODO
        :returns: TODO

        """
        name_store = Gtk.ListStore(str, str)
        codigos = self.s.recuperar_paginas(None)
        for c in codigos:
            name_store.append([c['id_pagina'],c['titulo']])
        return name_store


#C = REPORTE_NUBES ( "/home/vbasel/Doctorado/owncloud/saturar/doctorado_valen_2020.db")
#Gtk.main()
