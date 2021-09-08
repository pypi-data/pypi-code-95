#!/usr/bin/env python3
# -*- coding: utf-8 -*- 


###############################################################################
# Reporte de nodos usando matplotlib
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
#import matplotlib
#matplotlib.use('GTK3Cairo')  # or 'GTK3Cairo'
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from ..reportes.saturapi import SATURAPI

import networkx as nx
import pylab

import matplotlib
matplotlib.use('TkAgg')  # or 'GTK3Cairo'
import matplotlib.pyplot as plt

from ..utils import DIALOGOS

class REPORTE_NODOS(object):

    """Docstring for REPORTE_NODOS. """

    def __init__(self, sql):
        """TODO: to be defined. """
        self.s = SATURAPI()
        self.s.conectar(sql)
        self.id_cod = None
        self.sel_tipo = None
        self.ventana = Gtk.Window()
        self.ventana.set_title("reporte de códigos mediante nodos")

        self.mensajes = DIALOGOS(self.ventana)
        vbox = Gtk.VBox()
        l_cat = Gtk.Label("Categorías")
        cod_cargados = self.cargar_cod()
        drp_cod = Gtk.ComboBox.new_with_model_and_entry(cod_cargados)
        drp_cod.set_entry_text_column(1)
        b_mas = Gtk.Button("+")
        b_mas.connect("clicked", self.mas)
        hbox_drp = Gtk.HBox()

        hbox_drp.pack_start(l_cat, True, True, 0)
        hbox_drp.pack_start(drp_cod, True, True, 0)
        hbox_drp.pack_start(b_mas, True, True, 0)
        tipo_cargados = self.cargar_tipo()
        drp_tipo = Gtk.ComboBox.new_with_model_and_entry(tipo_cargados)
        drp_tipo.set_entry_text_column(0)
        hbox_graf = Gtk.HBox()
        l_graf = Gtk.Label("Categorías a graf")
        self.e_cat = Gtk.Entry()
        hbox_graf.pack_start(l_graf, True, True, 0)
        hbox_graf.pack_start(self.e_cat, True, True, 0)
        b_aceptar = Gtk.Button("Aceptar")
        b_aceptar.connect("clicked", self.aceptar)
        drp_cod.connect("changed", self.cambio_cat)
        drp_tipo.connect("changed", self.cambio_tipo)
        l_tipo = Gtk.Label("Ordenamiento")
        hbox_tip = Gtk.HBox()
        hbox_tip.pack_start(l_tipo, True, True, 0)
        hbox_tip.pack_start(drp_tipo, True, True, 0)
        vbox.pack_start(hbox_drp, True, True, 0)
        vbox.pack_start(hbox_tip, True, True, 0)
        vbox.pack_start(hbox_graf, True, False, 0)
        vbox.pack_start(b_aceptar, True, True, 0)
        self.ventana.add(vbox)
        self.ventana.show_all()

    def cargar_tipo(self):
        """TODO: Docstring for cargar_tipos.
        :returns: TODO

        """
        name_store = Gtk.ListStore(str)
        name_store.append(["circular"])
        name_store.append(["spring_layout"])
        name_store.append(["kamada_kawai_layout"])
        return name_store

    def aceptar(self, widget):
        """TODO: Docstring for aceptar.

        :arg1: TODO
        :returns: TODO

        """


        kk = 50
        layout = self.sel_tipo
        s = self.s
        categorias = []
        cat_aux = s.recuperar_categorias()
        cat_selec = self.e_cat.get_text()
        cat_selec = cat_selec.split(",")
        try:
            for cc in cat_aux:
                for c_aux in cat_selec:
                    if cc['id_cat'] == c_aux:
                        categorias.append(cc)
        except Exception as e:
            self.mensajes.error(texto = e,
                                    subtexto="Ha ocurrido un error")
        # categorias = [cat_aux[0]] 
        # return None
        nod_t = []
        col_fin = []
        cod_aux = {}
        G = nx.DiGraph(directed=True)
        for cat in categorias:
            nom_cat = cat['nombre_cat']
            G.add_node(nom_cat, color=cat['color'], tama=1, tipo='d')
            categ = s.recuperar_categorizado(cat['id_cat'])
            codigos = s.recuperar_codigos()
            for nombre, color_c in categ:
                cc = s.recuperar_todo_codificado()
                re = []
                for a in cc:
                    re.append(a['id_cod'])
                tam = s.contar_elementos(re)
                for c in codigos:
                    if int(c['id_cod']) in tam:
                        cod_aux[c['nombre_cod']] = tam[int(c['id_cod'])]
                if nombre in cod_aux:
                    G.add_node(nombre, 
                               color=color_c,
                               tama=int(cod_aux[nombre]), tipo='d')
                    G.add_edge(nombre, nom_cat, tama=cod_aux[nombre])
                else:
                    G.add_node(nombre, color=color_c, tama=0, tipo='d')
                    G.add_edge(nombre, nom_cat, tama=0)
    
        for nodes in G.nodes(data=True):
            col_fin.append(nodes[1]['color'])
        
        for nodes in G.nodes(data=True):
            nod_t.append(nodes[1]['tipo'])   
        labels = nx.get_edge_attributes(G, 'tama')
        dic_pos = {"spring_layout": nx.spring_layout(G, k=kk, iterations=10),
                   "kamada_kawai_layout": nx.kamada_kawai_layout(G),
                   "circular": nx.circular_layout(G)
                   }
        pos = dic_pos[layout]
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        nx.draw(G,
                pos,
                edge_color="blue",
                node_color=col_fin,
                font_size=10,
                node_size=600,
                node_shape='o',
                with_labels=True)
        pylab.show()
#            connectionstyle='Arc3, rad=0.5',
#            edge_cmap=plt.cm.Reds,

    def mas(self, arg1):
        """TODO: Docstring for mas.

        :arg1: TODO
        :returns: TODO

        """
        cad = self.e_cat.get_text()
        cad = cad + self.id_cod + ","
        self.e_cat.set_text(cad)

    def cambio_cat(self, widget):
        """TODO: Docstring for cambio.
        :returns: TODO

        """
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:
            model = widget.get_model()
            id = model[tree_iter][0]
            self.id_cod = id
    
    def cargar_cod(self):
        """TODO: Docstring for cargar_cod.
        :returns: TODO

        """
        name_store = Gtk.ListStore(str, str)
        codigos = self.s.recuperar_categorias()
        for c in codigos:
            name_store.append([c['id_cat'], c['nombre_cat']])
        return name_store
    def cambio_tipo(self, widget):
        """TODO: Docstring for cambio.
        :returns: TODO

        """
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:
            model = widget.get_model()
            tipo = model[tree_iter][0]
            self.sel_tipo = tipo

#REPORTE_NODOS("/home/vbasel/prueba2020.db")
#Gtk.main()
