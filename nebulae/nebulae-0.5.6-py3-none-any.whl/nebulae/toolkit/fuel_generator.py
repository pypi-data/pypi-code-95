#!/usr/bin/env python
'''
Created by Seria at 02/11/2018 3:00 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-

from PIL import Image
import io
import os
import csv
import h5py
import numpy as np
from piexif import remove as rm_exif

from .decorator import Timer
from ..law import Law

class FuelGenerator(object):

    def __init__(self, config=None, file_dir=None, file_list=None, dtype=None,
                 height=0, width=0, channel=1, encode='', is_seq=False, keep_exif=True):
        self.param = {}
        self.modifiable_keys = ['file_dir', 'file_list', 'dtype',
                                'height', 'width', 'channel', 'encode', 'keep_exif']
        self.valid_dtypes = ['uint8', 'uint16', 'uint32', 'int8', 'int16', 'int32', 'int64',
                             'float16', 'float32', 'float64', 'str', 'bool']
        if config:
            self.param['file_dir'] = config.get('file_dir')
            self.param['file_list'] = config.get('file_list')
            self.param['dtype'] = [np.dtype(dt) for dt in config.get('dtype')]
            self.param['height'] = config.get('height', height)
            self.param['width'] = config.get('width', width)
            self.param['channel'] = config.get('channel', channel)
            self.param['encode'] = config.get('encode', encode)
            self.param['is_seq'] = config.get('is_seq', is_seq)
            self.param['keep_exif'] = config.get('keep_exif', keep_exif)
        else:
            self.param['file_dir'] = file_dir
            self.param['file_list'] = file_list
            self.param['dtype'] = dtype
            self.param['height'] = height
            self.param['width'] = width
            self.param['channel'] = channel
            self.param['encode'] = encode
            self.param['is_seq'] = is_seq
            self.param['keep_exif'] = keep_exif

        # check if key arguments are valid
        if self.param['file_list'].split('.')[-1] != 'csv':
            raise Exception('file list should be a csv file.')
        for dt in self.param['dtype']:
            if dt not in self.valid_dtypes:
                raise Exception('%s is not a valid data type.' % dt)


    def _compress(self, img_path):
        ch_err = Exception('Images having %d channels are invalid.' % self.param['channel'])
        with io.BytesIO() as buffer:
            if self.param['keep_exif']:
                if self.param['channel'] == 1:
                    image = Image.open(img_path).convert('L')
                elif self.param['channel'] == 3:
                    image = Image.open(img_path).convert('RGB')
                else:
                    raise ch_err
                if self.param['width']>0 and self.param['height']>0:
                    image = image.resize((self.param['width'], self.param['height']))
                image.save(buffer, format=self.param['encode'])
            else:
                rm_exif(img_path, buffer)
            encoded_bytes = buffer.getvalue()
        np_bytes = np.frombuffer(encoded_bytes, dtype=np.uint8)

        return np_bytes

    def _write(self, dst_path, patch, data, info_keys, max_frames):
        if patch < 0:
            hdf5 = h5py.File(dst_path, 'w')
        else:
            hdf5 = h5py.File(dst_path[:-5] + '_%d.hdf5'%patch, 'w')
        for k, key in enumerate(info_keys):
            if k == 0:  # dealing with raw data
                dt = h5py.special_dtype(vlen=self.param['dtype'][k])
                hdf5.create_dataset(key, dtype=dt, data=np.array(data[key]))
            else:
                hdf5[key] = np.array(data[key]).astype(self.param['dtype'][k])
        if self.param['is_seq']:
            hdf5[Law.FRAME_KEY] = max_frames
        hdf5.close()

    @Timer
    def _file2Byte(self, dst_path, shards):
        data = {}
        print('+' + (60 * '-') + '+')
        nsample = len(open(os.path.join(self.param['file_dir'], self.param['file_list']), 'r').readlines()) - 1
        patch_size = int(nsample/shards) + 1
        if shards == 1:
            patch = -1
        else:
            patch = 0
        with open(os.path.join(self.param['file_dir'], self.param['file_list']), 'r') as filelist:
            content = csv.reader(filelist, delimiter=Law.CHAR_SEP, quotechar=Law.FIELD_SEP)
            ending_char = '\r'
            for l, line in enumerate(content):
                # display progress bar
                progress = int(l/nsample*19 + 0.4)
                yellow_bar = progress * ' '
                space_bar = (19-progress) * ' '
                if l == nsample:
                    ending_char = '\n'
                print('| Integrating data %7d / %-7d ⊰⟦\033[43m%s\033[0m%s⟧⊱ |'
                      % (l, nsample, yellow_bar, space_bar), end=ending_char)
                if l == 0: # initialize data dict
                    info_keys = line
                    if len(line) != len(self.param['dtype']):
                        raise Exception('number of given dtypes does not match the provided csv file.')
                    for key in line:
                        data[key] = []
                    max_frames = 0
                else:
                    for k, key in enumerate(info_keys):
                        if k == 0 and len(self.param['encode']) > 0: # dealing with raw data
                            if self.param['is_seq']:
                                csl = line[k].split(Law.CHAR_SEP)  # comma separated line
                                max_frames = len(csl) if len(csl) > max_frames else max_frames
                                temp_data = []
                                for f in csl:
                                    temp_data.append(self._compress(os.path.join(self.param['file_dir'], f)))
                                data[key].append(temp_data)
                            else:
                                data[key].append(self._compress(os.path.join(self.param['file_dir'], line[k])))
                        else:
                            csl = line[k].split(Law.CHAR_SEP) # comma separated line
                            if len(csl) == 1:
                                data[key].append(line[k])
                            else:
                                temp_data = []
                                for f in csl:
                                    temp_data.append(f)
                                data[key].append(temp_data)
                    if l%patch_size == 0:
                        self._write(dst_path, patch, data, info_keys, max_frames)
                        for key in info_keys:
                            data[key] = []
                        max_frames = 0
                        patch += 1
        self._write(dst_path, patch, data, info_keys, max_frames)

    def generateFuel(self, dst_path, shards=1):
        if not h5py.is_hdf5(dst_path):
            raise Exception('hdf5 file is recommended for storing compressed data.')
        if shards < 1 or (not isinstance(shards, int)):
            raise ValueError('The number of shards must be an positive integer.')
        duration = self._file2Byte(dst_path, shards)
        print('+' + (60 * '-') + '+')
        print('| \033[1;35m%-23s\033[0m has been generated within \033[1;35m%7.2fs\033[0m |'
              % (os.path.basename(dst_path), duration))
        print('+' + (60 * '-') + '+')

    def editProperty(self, config=None, **kwargs):
        if config:
            kwargs = config
        for key in kwargs:
            if key not in self.modifiable_keys:
                print('%s is not a modifiable parameter or has not been defined.' % key)
            else:
                self.param[key] = kwargs[key]