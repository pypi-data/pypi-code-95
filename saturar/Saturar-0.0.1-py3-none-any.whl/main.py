#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# cargador de saturar
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
import os
import sys
from threading import Thread
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject
lib_path = os.path.abspath(os.path.join(__file__, '..', '..', '..', 'lib'))
sys.path.append(lib_path)
from .saturar import SATURAR


class MAIN(Thread):

    """Docstring for MAIN. """

    def __init__(self):
        super(MAIN, self).__init__()
        """TODO: to be defined. """
        ruta_s = os.path.dirname(os.path.abspath(__file__))
        self.ventana = Gtk.Window()
        self.ventana.set_decorated(False)
        self.ventana.set_position(Gtk.WindowPosition.CENTER)
        self.ventana.connect('destroy', Gtk.main_quit)
        img = Gtk.Image.new_from_file(ruta_s+"/img/inicial.png")
        self.ventana.add(img)
        self.ventana.set_auto_startup_notification(True)
        self.ventana.show_all()

    def run(self):
        # Show the splash screen without causing startup notification
        # https://developer.gnome.org/gtk3/stable/GtkWindow.html
        #gtk-window-set-auto-startup-notification 
        #self.ventana.set_auto_startup_notification(False)
        self.ventana.show_all()
        self.ventana.set_auto_startup_notification(True)

        # Need to call Gtk.main to draw all widgets
        Gtk.main()

    def destroy(self):
        self.ventana.destroy()

def main():
    splash = MAIN()
    # Esto es para que la pantalla de inicio se muestre
    # si no, la pantalla aparecera pero no mostrar imagenes
    #splash.start()
    #time.sleep(5)
    #splash.destroy()
    while Gtk.events_pending():
        Gtk.main_iteration()
    #Here you can do all that nasty things that take some time.
    time.sleep(9) 
    #app = yourApp()
    #We don't need splScr anymore.
    splash.destroy()
    SATURAR()
    Gtk.main()
    return 0


if __name__ == '__main__':
    main()
