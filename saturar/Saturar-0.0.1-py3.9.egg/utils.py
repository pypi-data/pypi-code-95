#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################
# Herramientas para SATURAR
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

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class DIALOGOS(object):

    """Docstring for DIALOGOS.
        La clase DIALOGOS contiene los mensajes de error, infromación, 
        preguntas y peligro.

    """

    def __init__(self,ventana):
        """TODO: to be defined. """
        self.ventana = ventana
    
    def informacion(self,  texto, subtexto=""):
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.DIALOG)
        image.show()
        dialog = Gtk.MessageDialog(
            transient_for=self.ventana,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=texto,
        )

        dialog.set_image(image)
        dialog.format_secondary_text(
            subtexto
        )
        dialog.run()
        dialog.destroy()

    def error(self,  texto, subtexto=""):
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.DIALOG)
        image.show()
        dialog = Gtk.MessageDialog(
            transient_for=self.ventana,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CANCEL,
            text=texto,
        )
        dialog.set_image(image)
        dialog.format_secondary_text(
            subtexto
        )
        dialog.run()
        dialog.destroy()

    def peligro(self, texto, subtexto=""):
        band = False
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_DIALOG_WARNING, Gtk.IconSize.DIALOG)
        image.show()
        dialog = Gtk.MessageDialog(
            transient_for=self.ventana,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=texto,
        )

        dialog.set_image(image)
        dialog.format_secondary_text(
            subtexto
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            band = True
        elif response == Gtk.ResponseType.CANCEL:
            band = False
        dialog.destroy()
        return band

    def pregunta(self,  texto, subtexto=""):
        band = False
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_DIALOG_QUESTION, Gtk.IconSize.DIALOG)
        image.show()
        dialog = Gtk.MessageDialog(
            transient_for=self.ventana,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=texto,
        )
        dialog.set_image(image)
        dialog.format_secondary_text(
            subtexto
        )
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            band = True
        elif response == Gtk.ResponseType.NO:
            band = False
        dialog.destroy()
        return band


