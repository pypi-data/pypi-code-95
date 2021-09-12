#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

import sys
import getopt
from typing import List
from os import path
from .marke37 import Marke37

# TODO: aceptar plantilla de página o pdf.

def _archivo_de_entrada_existe(archivo):
    if path.exists(archivo):
        return True
    else:
        return False

def main(argv: List[str] = sys.argv[1:]):
    archivo_me37 = None
    archivo_salida = None
    formato = "html"

    try:
        optlist, args = getopt.getopt(argv, "hi:o:f:")
    except getopt.GetoptError:
        print('me37 -i <archivo_me37> -f <formato> -o <archivo_convertido>')
        sys.exit(2)

    for opt, arg in optlist:
        if opt == '-h':
            print('me37 -i <archivo_me37> -f <formato> -o <archivo_convertido>')
            sys.exit()
        elif opt in ("-i"):
            archivo_me37 = arg
        elif opt in ("-f"):
            formato = arg
        elif opt in ("-o"):
            archivo_salida = arg

    if not _archivo_de_entrada_existe(archivo_me37):
        print("Archivo de entrada [{}] no encontrado...".format(archivo_me37))

    convertidor = Marke37()
    letra_convertida = convertidor.convertir(archivo_me37, formato)
    if not archivo_salida:
        print(letra_convertida)
    else:
        archivo_salida = open(archivo_salida, "w")
        archivo_salida.write(letra_convertida)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
