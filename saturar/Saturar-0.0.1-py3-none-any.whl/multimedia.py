#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# manejador y codificador de archivos multimedias (video/audio)
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

"""VLC Gtk3 Widget classes + example application.

This module provides two helper classes, to ease the embedding of a
VLC component inside a pygtk application.

VLCWidget is a simple VLC widget.

DecoratedVLCWidget provides simple player controls.

When called as an application, it behaves as a video player.
"""

from gettext import gettext as _
import vlc
import sys
from gi.repository import Gtk, GObject
from gi.repository import Gdk
import sqlite3
import gi
import time
import os
from .anotador_multimedia import ANOTADOR
#import csv
#from gi.repository import Gtk
#import gi
#gi.require_version('Gtk', '3.0')
import locale
from gtkspellcheck import SpellChecker


from .utils import DIALOGOS
from operator import itemgetter

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
Gdk.threads_init()



class tabla_codificado(Gtk.HBox):

    def __init__(self, archivo_db, id_pag):
        super(tabla_codificado, self).__init__()
        self.con = archivo_db

        self.tabla = Gtk.TreeView()
        self.hbox = Gtk.HBox()
        self.id_pag = id_pag
        self.crear_tabla()

        self.add(self.hbox)
        self.show_all()

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        self.tabla.set_tooltip_text("")
        if treeiter is not None:
            self._tabla_valor = model[treeiter][0]
            self.seg = model[treeiter][1]

            # Con esto podemos sacar el memo del código y ponerlo en un tooltip
            cod = 'SELECT text_cod, memo FROM codificacion WHERE id_codificacion = '+str(self._tabla_valor)
            cursorObj = self.con.cursor()
            cursorObj.execute(cod)
            res = cursorObj.fetchall()
            cadena = "trancripción: \n"
            cadena = cadena + res[0][0] + "\n memo: \n"+res[0][1] 
            self.tabla.set_tooltip_text(cadena)

    def crear_tabla(self):
        """TODO: Docstring for crar_tabla.
        :returns: TODO

        """
        ######################################################################
        # Configuraciones de la tabla
        ######################################################################
        # creamos la lista de almacenamienta
        # variable para guardar el valor del codigo elegido en la tabla

        self.cod_data = self.actualizar_cod(self.id_pag)
        self._tabla_valor = ""
        self.store = Gtk.ListStore(str, str, str, str,str,str)
        for i in self.cod_data:
            self.store.append([i['id_cod'], str(i['c_ini']),str(i['c_fin']),i['text_cod'],  i['memo'], i['color']])



        self.tabla.set_model(self.store)
        # definimos las columnas
        col_cod_id = Gtk.TreeViewColumn("ID",
                                     Gtk.CellRendererText(),
                                     text=0,
                                     background=5)
        self.tabla.append_column(col_cod_id)
        col_cod = Gtk.TreeViewColumn("inicio",
                                     Gtk.CellRendererText(),
                                     text=1,
                                     background=5)

        self.tabla.append_column(col_cod)
        col_cod = Gtk.TreeViewColumn("final",
                                     Gtk.CellRendererText(),
                                     text=2,background=5)
 
        self.tabla.append_column(col_cod)
        col_cod = Gtk.TreeViewColumn("transcripción",
                                     Gtk.CellRendererText(),
                                     text=3,background=5)

        self.tabla.append_column(col_cod)


        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.hbox.pack_start(self.scrollable_treelist,True,True,0)

        self.scrollable_treelist.add(self.tabla)
        self.seg = 0
        tree_selection = self.tabla.get_selection()
        tree_selection.connect("changed", self.on_tree_selection_changed)


    def actualizar_tabla(self, widget):
        for col in self.tabla.get_columns():
            self.tabla.remove_column(col)
        #self.hbox.remove(self.scrollable_treelist)
        self.crear_tabla()
    

    def actualizar_cod(self, id_pag):
        """TODO: Docstring for actualizar_cod.
        :returns: TODO

        """
        cod = 'SELECT id_codificacion,id_cod,text_cod,c_ini,c_fin,status,memo FROM codificacion WHERE id_pagina = '+str(id_pag)
        cursorObj = self.con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []

        for r in res:
            if r[5] == 1:
                cod1 = 'SELECT color FROM codigo WHERE id_cod = '+str(r[1])
                cursorObj1 = self.con.cursor()
                cursorObj1.execute(cod1)
                res1 = cursorObj1.fetchall()

                tag = {'id_cod': str(r[0]),
                       'text_cod': r[2],
                       'c_ini': r[3],
                       'c_fin': r[4],
                       'memo': r[6],
                       'color': res1[0][0]}
                cod_data.append(tag)

        cod_data_ord = sorted(cod_data, key=itemgetter('c_ini')) 
        return cod_data_ord



class tabla_cod(Gtk.HBox):

    def __init__(self, archivo_db):
        super(tabla_cod, self).__init__()
        self.con = archivo_db
        self.cod_data = self.actualizar_cod(1)
        self.id_tabla = 0
        self.hbox = Gtk.HBox()
        self.crear_tabla()
        self.add(self.hbox)
        self.show_all()


    def crear_tabla(self):
        """TODO: Docstring for crar_tabla.
        :returns: TODO

        """
        ######################################################################
        # Configuraciones de la tabla
        ######################################################################
        # creamos la lista de almacenamienta
        # variable para guardar el valor del codigo elegido en la tabla
        self._tabla_valor = ""
        self.store = Gtk.ListStore(str, str, str, str)
        for i in self.cod_data:
            self.store.append([i['cod'], i['memo'],  i['b'], i['id_cod']])
            color = Gdk.RGBA()
            color.parse(i['b'])
        self.tabla = Gtk.TreeView(self.store)
        # definimos las columnas
        col_cod_id = Gtk.TreeViewColumn("ID",
                                     Gtk.CellRendererText(),
                                     text=3,
                                     background=2)
        self.tabla.append_column(col_cod_id)
        col_cod = Gtk.TreeViewColumn("codigos",
                                     Gtk.CellRendererText(),
                                     text=0,
                                     background=2)
        self.tabla.append_column(col_cod)

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.hbox.pack_start(self.scrollable_treelist,True,True,0)

        self.scrollable_treelist.add(self.tabla)
        self.seg = 0
        tree_selection = self.tabla.get_selection()
        tree_selection.connect("changed", self.on_tree_selection_changed)




    def on_tree_selection_changed(self, selection):

        model, treeiter = selection.get_selected()
        if treeiter is not None:
            self.id_tabla = model[treeiter][3]
            print(self.id_tabla)
    
    def actualizar_tabla(self, widget):
        for col in self.tabla.get_columns():
            self.tabla.remove_column(col)
        self.crear_tabla()
    
    def actualizar_cod(self, id_prop):
        """TODO: Docstring for actualizar_cod.
        :returns: TODO

        """
        cod = 'SELECT * FROM codigo WHERE id_prop = '+str(id_prop)
        cursorObj = self.con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_data = []
        for r in res:
            if r[6] == 1:
                tag = {'id_cod': str(r[0]),
                       'cod': r[1],
                       'memo': r[3],
                       'b': r[2]}
                cod_data.append(tag)
        return cod_data


class VLCWidget(Gtk.DrawingArea):
    """Simple VLC widget.

    Its player can be controlled through the 'player' attribute, which
    is a vlc.MediaPlayer() instance.
    """
    __gtype_name__ = 'VLCWidget'

    def __init__(self, instance, *p):
        Gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        #self.tp = (800, 600)
        #self.directorio_trabajo = ""

        def handle_embed(*args):
            if sys.platform == 'win32':
                self.player.set_hwnd(self.get_window().get_handle())
            else:
                self.player.set_xwindow(self.get_window().get_xid())
            return True
        self.connect("realize", handle_embed)
        #self.set_size_request(self.tp[0], self.tp[1])
        self.connect("draw", self.da_draw_event)

    def da_draw_event(self, widget, cairo_ctx):
        cairo_ctx.set_source_rgb(0, 0, 0)
        cairo_ctx.paint()


class DecoratedVLCWidget(Gtk.VBox):
    """Decorated VLC widget.

    VLC widget decorated with a player control toolbar.

    Its player can be controlled through the 'player' attribute, which
    is a Player instance.
    """
    __gtype_name__ = 'DecoratedVLCWidget'

    def __init__(self,instance, *p):
        super(DecoratedVLCWidget, self).__init__()
        self._vlc_widget = VLCWidget(instance, *p)
        self.player = self._vlc_widget.player
        # con esto voy a implementar la posibilidad de duplicar po 2,3,4,5 la velocdad de reproducción
        # los rangos deben ir de 0 a un numero positivo (creo que con 100 sobra)
        # se pueden incrementar x2, pero para que vaya lento deberia ir de 0.1 a 0.9
        # los botones podrian ser:
        # -1x -0.1x ,normal, +0.1x , +1x  

        self.player.set_rate(1) # esta es una prueba para duplicar la velociddad de reproducción
        ad1 = Gtk.Adjustment(0, 0, 100, 1, 20, 0)
        self.scaled = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=ad1)
        self.scaled.connect("button-release-event", self.scale_moved)
        self.pack_start(self._vlc_widget, True, True, 0)
        self.pack_start(self.scaled, False, False, 0)
        self._toolbar = self.get_player_control_toolbar()
        # self.pack_start(self._toolbar, False, False, 0)
        hbox = Gtk.HBox()
        label_text = Gtk.Label("x(ms)")
        self.segundero = Gtk.Entry(text="1000")
        self.label = Gtk.Label("0.0")
        Xs = [0.5,1,1.5,2]
        hbox.pack_start(self._toolbar, False, False, 0)
        hbox.pack_start(label_text, False, False, 0)
        hbox.pack_start(self.segundero, False, False, 0)
        hbox.pack_start(self.label, False, False, 0)
        for x in Xs:
            lab = str(x)+"X"
            bto_x = Gtk.Button(label=lab)
            bto_x.connect("clicked",self.veloc,x)
            hbox.pack_start(bto_x, False, False, 0)

        self.pack_start(hbox, False, False, 0)
        # self.add(self.vbox)
        GObject.timeout_add(1000, self.on_timeout, None)
        self.show_all()

    def veloc(self, widget,V):
        """TODO: Docstring for veloc.

        :arg1: TODO
        :returns: TODO

        """
        self.player.set_rate(V) # esta es una prueba para duplicar la velocidad de reproducción
        print (V)

    def scale_moved(self, a, b):
        """TODO: Docstring for scale_moved.

        :arg1: TODO
        :returns: TODO

        """
        s = self.player.get_state()
        if s != vlc.State.NothingSpecial and self.player.get_time() > -1:
            t = self.player.get_time()
            print(t)
            segundos = a.get_value()
            print(int(segundos))
            self.player.set_time(int(segundos)*1000)





    def on_timeout(self, arg1):
        """TODO: Docstring for on_timeout.

        :arg1: TODO
        :returns: TODO

        """
        s = self.player.get_state()
        if s != vlc.State.NothingSpecial and self.player.get_time() > -1:
            t = self.player.get_time()
            # print(t)
            tamaño = self.player.get_length()
            if t > 0:
                mm = float(int(t) * 100 / int(tamaño))
                # print(mm)
                self.scaled.set_value(mm)
                self.label.set_text("tiempo: "+str(float(t/1000)))
        return True

    def get_player_control_toolbar(self):
        """Return a player control toolbar
        """
        tb = Gtk.Toolbar.new()
        for text, tooltip, iconname, callback in (
            ("Play", "Play", 'media-playback-start',
             lambda b: self.player.play()),
            (_("Pause"), _("Pause"), 'media-playback-pause',
             lambda b: self.player.pause()),
            (_("Stop"), _("Stop"), 'media-playback-stop',
             lambda b: self.player.stop()),
            (_("-1S"), _("-1S"), 'media-skip-backward', self.S_menos_1),
            (_("+1S"), _("+1S"), 'media-skip-forward', self.S_mas_1),
        ):
            i = Gtk.Image.new_from_icon_name(
                iconname, Gtk.IconSize.LARGE_TOOLBAR)
            b = Gtk.ToolButton()  # i, text)
            b.set_icon_widget(i)
            b.set_tooltip_text(tooltip)
            b.connect("clicked", callback)
            tb.insert(b, -1)
        return tb

    def S_mas_1(self, arg1):
        """TODO: Docstring for S1.

        :arg1: TODO
        :returns: TODO

        """
        print("+1S")
        s = self.player.get_state()
        if s != vlc.State.NothingSpecial and self.player.get_time() > -1:
            t = self.player.get_time()
            segundos = self.segundero.get_text()
            self.player.set_time(t + int(segundos))

        return True

    def S_menos_1(self, arg1):
        """TODO: Docstring for S1.

        :arg1: TODO
        :returns: TODO

        """
        print("-1S")
        s = self.player.get_state()
        if s != vlc.State.NothingSpecial and self.player.get_time() > -1:
            t = self.player.get_time()
            segundos = self.segundero.get_text()
            self.player.set_time(t - int(segundos))
        return True


class VideoPlayer:
    """Example simple video player.
    """

    def __init__(self, archivo_db, id_prop, id_pag, ventana, arch_saturar,vlcins,ventana_central):
    #if 'linux' in sys.platform:
        # Inform libvlc that Xlib is not initialized for threads
    #    print("inicio vlc --no-xlib")
    #    self.instance = vlc.Instance("--no-xlib")
    #else:
    #    self.instance = vlc.Instance()
        self.instance = vlcins

        self.vlc = DecoratedVLCWidget(self.instance)
        self._id_pag = id_pag
        self._id_prop = id_prop
        self.con = archivo_db
        self.ventana = ventana
        self.__ventana_central = ventana_central
        self.__arch_saturar =arch_saturar 
    def main(self):
        """
        En main esta el arbol de widget que construye la vantana principal
        de Burrhus

        w
        |
         --> hbox
              |
               --> frame
                    |
                     --> boxx
                    |      |
                    |       --> self.vlc
                    |
                     --> vbox
                          |
                           --> self.notebook_tree
                          |
                           --> boton
        """
        # Create a single vlc.Instance() to be shared by (possible) multiple players.

        w = self.ventana # Gtk.Window(title="video")
        self.mensajes = DIALOGOS(self.__ventana_central)
        hpaned = Gtk.HPaned()
        frame = Gtk.Frame(label="video")
        cod_tam = ('SELECT contenido FROM pagina WHERE id_pagina = ' + str(self._id_pag))
        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        tam = cursorObj.fetchall()

        fvideo=tam[0][0]
        #fvideo = "/home/vbasel/espacio_de_trabajo/grabacion_tutorial/Vx22_02_2021x12_44_34_325963/12_44_34_345333_2021-02-22.mkv"#fvideo[-1]
        #self.seg = self.convert_time(fvideo)
        self.vlc.player.set_media(self.instance.media_new(fvideo))
        hbox = Gtk.HBox()
        vbox = Gtk.VBox()
        self.notebook_tree = Gtk.Notebook()
        boton = Gtk.Button(label="PDI")
        boton.connect("clicked", self.boton_click)
        boton_srt = Gtk.Button(label="anotar")
        boton_srt.connect("clicked", self.boton_anotar_srt)
        boton_ed = Gtk.Button(label="Editar")
        boton_ed.connect("clicked", self.boton_editar)
        boton_borrar = Gtk.Button(label="borrar")
        boton_borrar.connect("clicked", self.boton_borrar)
        self.pagina_tree = []
        # TABLA con los códigos 
        self.t_cod = tabla_cod(self.con)


        self.notebook_tree.append_page(self.t_cod)
        nt = self.notebook_tree.get_nth_page(0)
        self.notebook_tree.set_tab_label_text(nt, "códigos")
        self.pagina_tree.append(self.t_cod)
        # TABLA con los codificado
        self.t_codific = tabla_codificado(self.con, self._id_pag)


        self.notebook_tree.append_page(self.t_codific)
        nt1 = self.notebook_tree.get_nth_page(1)
        self.notebook_tree.set_tab_label_text(nt1, "transcripciones")
        self.pagina_tree.append(self.t_codific)
        boxx = Gtk.HBox()
        boxx.pack_start(self.vlc, True, True, 0)
        frame.add(boxx)
        vbox.pack_start(self.notebook_tree, True, True, 0)
        vbox.pack_start(boton_srt, False, False, 0)
        vbox.pack_start(boton_ed, False, False, 0)
        vbox.pack_start(boton_borrar, False, False, 0)
        vbox.pack_start(boton, False, False, 0)
        hpaned.add1(frame)
        hpaned.add2(vbox)
        w.pack_start(hpaned, True, True, 0)
        w.show_all()

        w.connect("destroy", Gtk.main_quit)
        w.connect("key-press-event", self.on_key_press_event)

    def boton_editar(self, arg1):
        """TODO: Docstring for boton_editar.

        :arg1: TODO
        :returns: TODO

        """
        if self.t_codific._tabla_valor != "":
            cod = 'SELECT * FROM codificacion WHERE id_codificacion = '+str(self.t_codific._tabla_valor)
            cursorObj = self.con.cursor()
            cursorObj.execute(cod)
            res = cursorObj.fetchall()
            res = res[0]
            print(res)
            s = self.vlc.player.get_state()
            if s != vlc.State.NothingSpecial and self.vlc.player.get_time() > -1:
                t = self.vlc.player.get_time()
                if s == vlc.State.Playing:
                    self.vlc.player.pause()
                self.anotador = ANOTADOR(self.con,
                                         self.t_codific,
                                         self.__arch_saturar,
                                         editar = True)
                self.anotador._id_codificacion = res[0]
                self.anotador._id_cod = res[1]
                self.anotador._id_prop = res[2]
                self.anotador._id_pag = res[3]
                self.anotador.p_buffer_trans.set_text(res[4])
                self.anotador.entry_inic.set_text(str(res[5]))
                self.anotador.entry_fin.set_text(str(res[6]))
                self.anotador.p_buffer_memo.set_text(res[9])
                self.anotador._player = self.vlc.player
                self.anotador.main_windows.show_all()
        else:
            self.mensajes.error(texto="error",
                                subtexto="no has seleccionado ninguna transcripción")

    def boton_borrar(self, arg1):
        """TODO: Docstring for boton_borrar.

        :arg1: TODO
        :returns: TODO

        """
        c = "cod: " + self.t_codific._tabla_valor
        resp = self.mensajes.pregunta(texto="¿Esta seguro de eliminar el siguiente código?",
                                      subtexto = c)
        if resp== True:
            if self.t_codific._tabla_valor != "":
                cod = 'UPDATE codificacion SET status = 0 where id_codificacion = ' + str(self.t_codific._tabla_valor)
                cursorObj = self.con.cursor()
                cursorObj.execute(cod)
                #res = cursorObj.fetchall()

                self.con.commit()
                #print(res)
                self.t_codific.actualizar_tabla(None)
            else:
                self.mensajes.error(texto="error",
                                    subtexto="no has seleccionado ninguna transcripción")
            print("borrar")

    def boton_anotar_srt(self, arg1):
        """TODO: Docstring for boton_anotar_srt.

        :arg1: TODO
        :returns: TODO

        """
        # con esto puedo hacer una captura de pantalla .. puedo usar el ID 
        # del código para identificar la captura de pantalla 
        # arch="/home/vbasel/prueba1.png"
        # self.vlc.player.video_take_snapshot(0, arch, 0, 0)
        s = self.vlc.player.get_state()
        if s != vlc.State.NothingSpecial and self.vlc.player.get_time() > -1:
            t = self.vlc.player.get_time()
            #print(s)
            #print(type(s))
            if s == vlc.State.Playing:
                self.vlc.player.pause()
            self.anotador = ANOTADOR(self.con, self.t_codific, self.__arch_saturar)
            self.anotador.hhmmss(t)
            self.anotador._id_prop = self._id_prop
            self.anotador._id_pag = self._id_pag
            self.anotador._id_cod = self.t_cod.id_tabla
            self.anotador._player = self.vlc.player
            self.anotador.main_windows.show_all()

    def on_key_press_event(self, widget, event):
        """TODO: Docstring for on_key_press_event.

        :arg1: TODO
        :returns: TODO

        """
        print("Key val, name: ", event.keyval, Gdk.keyval_name(event.keyval))
        valor_tecla = Gdk.keyval_name(event.keyval)
        if valor_tecla == "F1":
            self.vlc.player.play()
        if valor_tecla == "space":
            self.vlc.player.pause()
        if valor_tecla == "F3":
            self.vlc.player.stop()
        if valor_tecla == "F4":
            self.boton_click(None)

    def boton_click(self, arg1):
        """TODO: Docstring for boton_click.

        :arg1: TODO
        :returns: TODO

        """

        PDI = int(self.pagina_tree[1].seg)
        print(PDI)
        if PDI > 0:
            pdi = PDI #- self.seg
            print(pdi)
            self.vlc.player.set_time(pdi)


# if __name__ == '__main__':

    # con = sqlite3.connect("/home/vbasel/prueba_multimedia_2.db")  # "saturar2.db")
    # id_prop = 1
    # id_pag = 2
    # p = VideoPlayer(con, id_prop, id_pag, Gtk.Window(title="video"))
    # p.main()
    # p.instance.release()
