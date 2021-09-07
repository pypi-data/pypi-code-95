# -*- encoding: utf-8 -*-
# Folder Structure Creator v0.1.5
# A simple folder structure creator.
# Copyright © 2021, David Sanchez-Wells.
# See /LICENSE for licensing information.

import os
import sys
import argparse


class Folder:

    def __init__(self, name, parents=None):

        self.name = name

        if parents is None:
            self.parents = ''
        else:
            self.parents = '-'.join(parents).split('-')
            self.parents = os.path.join(*self.parents)

        os.mkdir(os.path.join(self.parents, self.name))


def parse_args(args):
    parser = argparse.ArgumentParser(description='Create folder structure.')
    parser.add_argument('filename', type=str, help='Structure file name.')
    return parser.parse_args(args)


def file_processor(content):
    parents = list('')
    counter = 0

    while content:
        print('Line %s' % counter)
        indents = 0
        line = content.readline()

        if line == '':
            return 'La creación de carpetas ha terminado'

        elif line[-1] == '\n':
            line = line[0:-1]

        while line[0] == '\t':
            line = line[1:]
            indents += 1
            if indents > len(parents):
                raise IndentationError('File structure is not correct.')

        if line[0] != ' ':
            if indents == 0:
                Folder(line)
                parents = list([line])
            elif 0 < indents < len(parents):
                parents = parents[0:indents]
                Folder(line, parents)
                parents += [line]
            else:
                Folder(line, parents)
                parents += [line]

        else:
            raise IndentationError('File structure is not correct.')

        counter += 1


def main():
    args = parse_args(sys.argv[1:])
    content = open(args.__dict__['filename'], 'r')

    # Parsing bypass, activate only for debugging purposes
    # content = open('test_structure', 'r')

    execution_path = os.path.dirname(os.path.abspath(__file__))
    print('The folder structure will be created at', execution_path)

    file_processor(content)

    content.close()
    print("The folder structure creation has ended successfully.")
    