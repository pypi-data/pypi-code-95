#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# Clase anotador para los contenidos multimedia
#
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

#import sys
from gi.repository import Gtk, GObject
#from gi.repository import Gdk
import sqlite3
import gi
import time
import os
gi.require_version('Gtk', '3.0')
import locale
from gtkspellcheck import SpellChecker


class ANOTADOR(object):

    """Docstring for ANOTADOR. """

    def __init__(self, con, t_cod, arch_saturar, editar=False):
        """TODO: to be defined. """
        self.arch_saturar = arch_saturar
        self._id_prop = 0
        self._id_pag = 0
        self._id_cod = 0
        self._id_codificacion = 0
        self._player = None
        self.con = con
        self.t_cod = t_cod
        cad = "trancripción y memos del punto de interes"
        self.main_windows = Gtk.Window(title=cad)
        self.main_windows.set_default_size(-1, 350)
        self.dir = ""
        # ID
        #  hbox1 = Gtk.HBox()
        vbox1 = Gtk.VBox()

        # inicio
        hbox2 = Gtk.HBox()
        l2 = Gtk.Label(label="Inicio")
        self.entry_inic = Gtk.Entry()
        hbox2.pack_start(l2, True, True, 0)
        hbox2.pack_start(self.entry_inic, True, True, 0)
        vbox1.pack_start(hbox2, False, False, 0)
        # fin
        hbox3 = Gtk.HBox()
        l3 = Gtk.Label(label="final")
        self.entry_fin = Gtk.Entry()
        hbox3.pack_start(l3, True, True, 0)
        hbox3.pack_start(self.entry_fin, True, True, 0)
        vbox1.pack_start(hbox3, False, False, 0)
        # transcripcion
        hbox4 = Gtk.HBox()
        ######################################################################
        #  configuraciones del textview
        ######################################################################
        frametrans = Gtk.Frame(label="Transcripción:")
        scrolltexttrans = Gtk.ScrolledWindow()
        scrolltexttrans.set_hexpand(True)
        scrolltexttrans.set_vexpand(True)
        # Widget con el textview donde se visualizan el texto a codificar
        self.paginatrans = Gtk.TextView()
        spellchecker = SpellChecker(self.paginatrans,
                                    locale.getdefaultlocale()[0])
        # Deshabilito la edición del textview
        self.paginatrans.set_editable(True)
        self.p_buffer_trans = self.paginatrans.get_buffer()
        # Corto el texto en las palabras si se pasan del tamaño del textview
        self.paginatrans.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolltexttrans.add(self.paginatrans)
        frametrans.add(scrolltexttrans)

        hbox4.pack_start(frametrans, True, True, 0)

        vbox1.pack_start(hbox4, False, False, 0)
        # memo
        hbox5 = Gtk.HBox()
        ######################################################################
        #  configuraciones del textview
        ######################################################################
        framememo = Gtk.Frame(label="memo:")
        scrolltextmemo = Gtk.ScrolledWindow()
        scrolltextmemo.set_hexpand(True)
        scrolltextmemo.set_vexpand(True)
        # Widget con el textview donde se visualizan el texto a codificar
        self.paginamemo = Gtk.TextView()
        spellchecker2 = SpellChecker(self.paginamemo,
                                     locale.getdefaultlocale()[0])
        # Deshabilito la edición del textview
        self.paginamemo.set_editable(True)
        self.p_buffer_memo = self.paginamemo.get_buffer()
        # Corto el texto en las palabras si se pasan del tamaño del textview
        self.paginamemo.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolltextmemo.add(self.paginamemo)
        framememo.add(scrolltextmemo)

        hbox5.pack_start(framememo, True, True, 0)
        vbox1.pack_start(hbox5, False, False, 0)
        # Boton agregar / editar
        hbox5 = Gtk.HBox()
        if editar is False:
            bto_agregar = Gtk.Button("Agregar")
            bto_agregar.connect("clicked", self.agregar)
        else:
            bto_agregar = Gtk.Button("Editar")
            bto_agregar.connect("clicked", self.editar)

        hbox5.pack_start(bto_agregar, True, True, 0)
        vbox1.pack_start(hbox5, False, False, 0)
        self.main_windows.add(vbox1)

    def editar(self, widget):
        """TODO: Docstring for editar.
        :returns: TODO

        """
        ini = self.entry_inic.get_text()
        fin = self.entry_fin.get_text()
        start = self.p_buffer_memo.get_start_iter()
        end = self.p_buffer_memo.get_end_iter()
        memo = self.p_buffer_memo.get_text(start, end, True)
        startt = self.p_buffer_trans.get_start_iter()
        endt = self.p_buffer_trans.get_end_iter()
        trans = self.p_buffer_trans.get_text(startt, endt, True)
        dat = os.path.split(self.arch_saturar)
        arch = dat[0] + "/img/" + str(self._id_codificacion) + ".png"
        self._player.video_take_snapshot(0, arch, 0, 0)
        cursorObj = self.con.cursor()
        cursorObj.execute("""UPDATE  codificacion  SET
                                 id_cod=?,
                                 id_prop=?,
                                 id_pagina=?,
                                 text_cod=?,
                                 c_ini=?,
                                 c_fin=?,
                                 fecha_alt=?,
                                 status=?,
                                 memo=?
                                 WHERE id_codificacion=?""",
                          (int(self._id_cod),
                           self._id_prop,
                           self._id_pag,
                           trans,
                           int(ini),
                           int(fin),
                           time.strftime("%d/%m/%y"),
                           1,
                           memo,
                           int(self._id_codificacion)))
        self.con.commit()
        self.t_cod.actualizar_tabla(None)
        self.main_windows.destroy()

    def agregar(self, widget):
        """TODO: Docstring for agregar.
        :returns: TODO

        """
        ini = self.entry_inic.get_text()
        fin = self.entry_fin.get_text()
        start = self.p_buffer_memo.get_start_iter()
        end = self.p_buffer_memo.get_end_iter()
        memo = self.p_buffer_memo.get_text(start, end, True)
        startt = self.p_buffer_trans.get_start_iter()
        endt = self.p_buffer_trans.get_end_iter()
        trans = self.p_buffer_trans.get_text(startt, endt, True)
        #print(self.id_cod)
        #print(trans)
        #print(memo)
        cod_tam = ('SELECT MAX(id_codificacion) FROM codificacion')
        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        tam = cursorObj.fetchall()
        #print(tam[0][0])
        if tam[0][0] is not None:
            id_codificacion = int(tam[0][0]) + 1
        else:
            id_codificacion = 1
        if id_codificacion == 0:
            print("error de codific")
            self.main_windows.hide()
            return 1
        if self._id_cod == 0:
            print("error no se selcciono ningun codigo")
            self.main_windows.hide()
            return 1
        codific_final = [id_codificacion,
                         int(self._id_cod),
                         self._id_prop,
                         self._id_pag,
                         trans,
                         int(ini),
                         int(fin),
                         time.strftime("%d/%m/%y"),
                         1,
                         memo]
        print(codific_final)
        # con esto puedo hacer una captura de pantalla .. puedo usar el ID 
        # del código para identificar la captura de pantalla 
        dat = os.path.split(self.arch_saturar)
        arch = dat[0]+ "/img/" +str(id_codificacion)+".png"
        self._player.video_take_snapshot(0, arch, 0, 0)
        self.agregar_cod(codific_final)
        self.t_cod.actualizar_tabla(None)
        self.main_windows.destroy()

    def agregar_cod(self, cod):
        """TODO: Docstring for agregar_cod.

        :cod: TODO
        :returns: TODO

        """
        cursorObj = self.con.cursor()
        cursorObj.execute('INSERT INTO codificacion(id_codificacion, id_cod, id_prop, id_pagina, text_cod,c_ini, c_fin, fecha_alt, status, memo) VALUES(?, ?, ?, ?, ?,?,?,?,?,?)', cod)
        self.con.commit()

    def hhmmss(self, segundostotales):

        #self.entry_id.set_text(str(segundostotales))
        self.entry_inic.set_text(str(segundostotales))
        self.entry_fin.set_text(str(segundostotales))
        return True



