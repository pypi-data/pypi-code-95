#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# Ventana para codificar archivos de texto planos dentro de SATURAR
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
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango, GtkSource


class CODIFICAR(object):

    """Ventana para codificar en SATURAR

    VentanaPrincipal
            |
             -> HPaned
                 |
                  -> frame_tabla
                 |      |
                 |       -> vbox
                 |           |
                 |           | -> hbox
                 |           |     |
                 |           |      -> marcar
                 |           |     |
                 |           |      -> desmarcar
                 |           |
                 |            -> frame
                 |                |
                 |                 -> scrolltabla
                 |                       |
                 |                        -> tabla
                 |
                  - > frame
                        |
                         -> hbox_text
                                |
                                 -> scrolltext
                                        |
                                         -> pagina

    """

    def __init__(self, id_pag, id_prop, archivo_db, hbox_ventana,ventana):
        """TODO: to be defined. """
        # codigos puesto hardcodeadamente para probar
        self.con = archivo_db # self.conectar_base(archivo_db)
        self.id_codificacion = 0
        self.id_prop = id_prop
        self.id_pag = id_pag
        self.cod_data = self.actualizar_cod(id_prop)
        titulo, texto = self.iniciar_base(id_pag)
        self.tags_marcados = self.actualizar_tag(id_pag)
        self.tags = {}
        # Ventana principal
        self.VentanaPrincipal = hbox_ventana
        self.ventana = ventana
        # Gtk.Window(title="Codificador")
        self.VentanaPrincipal.connect("destroy", Gtk.main_quit)
        # contendores
        hbox = Gtk.HBox()
        vbox = Gtk.VBox()
        hbox_text = Gtk.HBox()
        HPaned = Gtk.HPaned()
        HPaned.props.wide_handle = True
        frame = Gtk.Frame()
        #titulo = "Página: " + titulo
        #frame.set_label(titulo)
        frame.set_shadow_type(1)
        frame_tabla = Gtk.Frame()
        frame_tabla.set_shadow_type(1)
        scrolltext = Gtk.ScrolledWindow()
        scrolltext.set_hexpand(True)
        scrolltext.set_vexpand(True)
        scrolltabla = Gtk.ScrolledWindow()
        scrolltabla.set_hexpand(True)
        scrolltabla.set_vexpand(True)
        ######################################################################
        #  configuraciones del textview
        ######################################################################
        # Widget con el textview donde se visualizan el texto a codificar
        # self.pagina = GtkSource.View() #Gtk.TextView()

        # self.pagina.modify_font(Pango.FontDescription('Sans 17'))
        self.pagina = Gtk.TextView() 

        # self.pagina.set_show_line_numbers(True)
        
        # Deshabilito la edición del textview
        self.pagina.set_editable(False)
        # Corto el texto en las palabras si se pasan del tamaño del textview
        self.pagina.set_wrap_mode(Gtk.WrapMode.WORD)
        self.pagina.set_tooltip_text("")
        self.pagina.connect("button-release-event", self.boton_mouse)
        self.p_buffer = self.pagina.get_buffer()
        # codigo hardcodeado para probar
        self.p_buffer.set_text(texto)
        self.tag_found = self.p_buffer.create_tag("found", background="yellow")
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
            self.tag = self.p_buffer.create_tag(i['cod'], background_rgba=color)
            self.tags[i['cod']] = self.tag
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
        select = self.tabla.get_selection()
        select.connect("changed", self.on_tree_selection_changed)
        ######################################################################
        # botones para marcar y des marcar codigos
        ######################################################################
        boton_marcar = Gtk.Button(label="marcar")
        boton_marcar.connect("clicked", self.on_marcar_clicked)
        boton_desmarcar = Gtk.Button(label="desmarcar")
        boton_desmarcar.connect("clicked", self.on_desmarcar_clicked)
        boton_fuente = Gtk.Button(label="fuente")
        boton_fuente.connect("clicked", self.on_fuente_clicked)
        #boton_buscar=Gtk.Button(label="buscar")
        #boton_buscar.set_icon_name("system-search-symbolic")
        #boton_buscar.connect("clicked", self.on_search_clicked)
        frame_codigos = Gtk.Frame()
        #frame_codigos.set_label("Códigos de la página")
        self.label_cod = Gtk.Label("Códigos en la página: ")
        frame_codigos.add(self.label_cod)
        ######################################################################
        # Agrego todo al main windows
        ######################################################################
        self.bot_salt = Gtk.Button("Ir a")
        self.bot_salt.connect("clicked",self.salto)
        self.entry_salt = Gtk.Entry()
        hbox_salt = Gtk.HBox()
        hbox_salt.pack_start(self.entry_salt, False, False, 0)
        hbox_salt.pack_start(self.bot_salt, False, False, 0)

        hbox.pack_start(boton_marcar, False, False, 0)
        hbox.pack_start(boton_desmarcar, False, False, 0)
        hbox.pack_start(boton_fuente, False, False, 0)
        # hbox.pack_start(boton_buscar, False, False, 0)
        

        vbox.pack_start(frame_codigos, False, False, 10)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(scrolltabla, True, True, 0)

        vbox.pack_start(hbox_salt, False, False, 20)
        scrolltext.add(self.pagina)
        scrolltabla.add(self.tabla)
        self.label_caracter = Gtk.Label(label="caracter: ", xalign=0)
        vbox_texto = Gtk.VBox()
        frame_text = Gtk.Frame()
        frame_text.add(scrolltext)
        vbox_texto.pack_start(frame_text, True, True, 0)
        hbox_text.pack_start(vbox_texto, True, True, 0)
        vbox_texto.pack_start(self.label_caracter, False, False, 10)
        frame.add(hbox_text)
        frame_tabla.add(vbox)
        HPaned.add1(frame_tabla)
        HPaned.add2(frame)
        self.VentanaPrincipal.add(HPaned)
        self._crear_datos_tags()
        self.VentanaPrincipal.show_all()
        print("inicio la codificacion")
        self.VentanaPrincipal.grab_focus()

    def iniciar_en_caract(self, caracter):
        """TODO: Docstring for iniciar_en_caract.
        :returns: TODO

        """

        pr = self.p_buffer.get_iter_at_offset(caracter)
        self.p_buffer.place_cursor(pr)
        self.pagina.scroll_to_iter(pr, 0, True, 0, 0)
        print("caracter")


    def salto(self, arg1):
        """TODO: Docstring for salto.

        :arg1: TODO
        :returns: TODO

        """
        #######################################################################
        #  prueba para posicionar el cursor en un pusto especifico
        #######################################################################
        salto = self.entry_salt.get_text()
        if salto.isnumeric() is True:
            pr = self.p_buffer.get_iter_at_offset(int(salto))
            self.p_buffer.place_cursor(pr)
            self.pagina.scroll_to_iter(pr, 0, True, 0, 0)
        else:
            print("error")
        #######################################################################

    def on_fuente_clicked(self, widget):
        """TODO: Docstring for function.

        :arg1: TODO
        :returns: TODO

        """
        fdia = Gtk.FontSelectionDialog("Seleccione una fuente")
        response = fdia.run()
        if response == Gtk.ResponseType.OK:
            font_desc = Pango.FontDescription(fdia.get_font_name())
            if font_desc:
                self.pagina.modify_font(font_desc)
        fdia.destroy()

    def iniciar_base(self, id):
        """TODO: Docstring for actialzar_base.
        :returns: TODO

        """
        cod = 'SELECT * FROM pagina WHERE id_pagina = ' + str(id) 
        cursorObj = self.con.cursor()
        cursorObj.execute(cod)
        resultado = cursorObj.fetchall()

        return resultado[0][2], resultado[0][3]

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

    def actualizar_tag(self, id_pagina):
        """TODO: Docstring for actualizar_tag.
        :returns: TODO

        """
        cod = 'SELECT * FROM codificacion WHERE id_pagina = '+str(id_pagina) 
        cursorObj = self.con.cursor()
        cursorObj.execute(cod)
        res = cursorObj.fetchall()
        cod_tam = ('SELECT MAX(id_codificacion) FROM codificacion')
        cursorObj = self.con.cursor()
        cursorObj.execute(cod_tam)
        tam = cursorObj.fetchall()
        #print(tam[0][0])
        if tam[0][0] is not None:
            self.id_codificacion = int(tam[0][0])
        else:
            self.id_codificacion = 0
        cod_st = 'SELECT id_cod, status FROM codigo WHERE id_prop = '+str(self.id_prop)
        cursorObjst = self.con.cursor()
        cursorObjst.execute(cod_st)
        rest = cursorObjst.fetchall()
        dic_rest = {}
        for v, a in rest:
            dic_rest[v] = a
        res_f = []
        #print(dic_rest)
        for codigos in res:
            #print("------------",codigos)
            if dic_rest[codigos[1]] == 1:
                res_f.append(codigos)
        return res_f

    def _crear_datos_tags(self):
        """TODO: Docstring for _crear_datos_tags.
        :returns: TODO

        """
        cod = 'SELECT id_cod, nombre_cod,status FROM codigo WHERE id_prop = '+str(self.id_prop) 
        cursorObj = self.con.cursor()
        cursorObj.execute(cod)
        cc = cursorObj.fetchall()
        #print(cc)
        ban = ""
        for res in self.tags_marcados:

            for a, b, c in cc:
                if a == res[1] and c == 1:
                    ban = b
            #print(ban)
            if res[8] == 1:
                tag = self.tags[ban]
                start = self.p_buffer.get_iter_at_offset(res[5])
                end = self.p_buffer.get_iter_at_offset(res[6])
                self.p_buffer.apply_tag(tag, start, end)

    def boton_mouse(self, widget, event):
        """
        Capturo cuando el boton del mouse hace click sobre el textview
        para poder ver la posición del cursor
        """
        print(event.type)
        cursor = self.p_buffer.props.cursor_position
        
        self.label_caracter.set_text("Caracter: "+str(cursor))

        tags = self.p_buffer.get_iter_at_offset(cursor)
        tag_final = tags.get_tags()
        
        self.pagina.set_tooltip_text("")
        print(len(tag_final))
        if len(tag_final) > 0:
            texto = "códigos en la página: \n"
            for label in tag_final:
                texto = texto + label.props.name + " \n"
            #self.pagina.set_tooltip_text("memo: ")
            self.label_cod.set_text(texto)
        else:
            self.label_cod.set_text("")

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        self.tabla.set_tooltip_text("")
        if treeiter is not None:
            self._tabla_valor = model[treeiter][0]
            # Con esto podemos sacar el memo del código y ponerlo en un tooltip
            self.tabla.set_tooltip_text(model[treeiter][1])

    def agregar_cod(self, cod):
        """TODO: Docstring for agregar_cod.

        :cod: TODO
        :returns: TODO

        """
        cursorObj = self.con.cursor()
        cursorObj.execute('INSERT INTO codificacion(id_codificacion, id_cod, id_prop, id_pagina, text_cod,c_ini, c_fin, fecha_alt, status, memo) VALUES(?, ?, ?, ?, ?,?,?,?,?,?)', cod)
        self.con.commit()

    def on_marcar_clicked(self, widget):
        bounds = self.p_buffer.get_selection_bounds()
        tag = self.tags[self._tabla_valor]

        self.id_codificacion += 1
        cod = 'SELECT id_cod, nombre_cod,status FROM codigo WHERE id_prop = '+str(self.id_prop) 
        cursorObj = self.con.cursor()
        cursorObj.execute(cod)
        cc = cursorObj.fetchall()
        ban = ""
        if len(bounds) != 0:
            start, end = bounds
            self.p_buffer.apply_tag(tag, start, end)
            sel_ini = start.get_offset()
            sel_fin = end.get_offset()
            seleccion = self.p_buffer.get_text(start, end, True)
            for a, b, c in cc:
                if b == tag.props.name and c == 1:
                    ban = a
            cod = ban # tag.props.name
            codific_final = [self.id_codificacion,
                             cod,
                             self.id_prop,
                             self.id_pag,
                             seleccion,
                             sel_ini,
                             sel_fin,
                             time.strftime("%d/%m/%y"),
                             1,
                             ""]
            self.tags_marcados.append(codific_final)
            self.agregar_cod(codific_final)
            #print(self.tags_marcados)

    def on_desmarcar_clicked(self, widget):
        """TODO: Docstring for on_desmarcar_clicked.
        :returns: TODO

        """
        # para poder borrar un tag, voy a tener que implementar una funcion
        # de actualizacion, donde cuando borre una marca, esta este guardada en
        # una lista, y despues se actualice todo (pensanod luego en inteegrarlo
        # con sql
        # self.p_buffer.remove_all_tags(self.p_buffer.get_start_iter(),
        #                              self.p_buffer.get_end_iter())
        start, end = self.p_buffer.get_selection_bounds()
        cod_ini = start.get_offset()
        cod_fin = end.get_offset()
        # print("datos cursor: ", cod_ini, cod_fin, self._tabla_valor)
        cod = 'SELECT id_cod, nombre_cod,status FROM codigo WHERE id_prop = '+str(self.id_prop) 
        cursorObj = self.con.cursor()
        cursorObj.execute(cod)
        cc = cursorObj.fetchall()
        ban = ""
        for a, b, c in cc:
            if b == self._tabla_valor and c == 1:
                ban = a

        for dato in self.tags_marcados:
            #print(dato [0],">---->",dato[1],self._tabla_valor)
            #print("dat comp: ", dato[5], dato[6], dato[1], dato[8])
            if (dato[5] <= cod_ini and
                dato[6] >= cod_fin and
                dato[1] == ban and
                dato[8] == 1):
                #print("encotre el siguiente dato: ", dato)
                in_f = self.p_buffer.get_iter_at_offset(dato[5])
                fin_f = self.p_buffer.get_iter_at_offset(dato[6])
                #print("id_codificacion: ", dato[0])
                self.p_buffer.remove_tag_by_name(self._tabla_valor,
                                                 in_f,
                                                 fin_f)
                cursorObj = self.con.cursor()
                cad = 'UPDATE codificacion SET status = 0 where id_codificacion = ' + str(dato[0])
                cursorObj.execute(cad)
                self.con.commit()
                # self.tags_marcados = self.actualizar_tag(self.id_pag)
                return True

            else:
                print("no encontre",  dato[5], dato[6], dato[1], dato[8])
                #print(type(dato[8]))

######## PARA TENER EN CUENTA #############
# podría usar la expresión "descriptores" en vez de "códigos"
