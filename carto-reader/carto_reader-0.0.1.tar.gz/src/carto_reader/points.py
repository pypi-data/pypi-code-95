from collections.abc import MutableMapping
from enum import IntEnum
from xml.etree import ElementTree as etree
import re
import numpy as np


class PointType(IntEnum):
    NORMAL = 0
    LOCATION_ONLY = 1
    SCAR = 2
    FLOATING = 3
    TRANSIENT_EVENT = 4


class PointLabel(IntEnum):
    NO_TAG = -1
    NONE = 4
    HIS = 5
    PACING_SITE = 6
    DOUBLE_POTENTIAL = 7
    FRAGMENTED_SIGNAL = 8
    ABLATION = 9
    SCAR = 10
    LOCATION_ONLY = 11
    TRANSIENT_EVENT = 12
    CUSTOM_1 = 13
    CUSTOM_2 = 14
    CUSTOM_3 = 15
    CUSTOM_4 = 16


class SigReference:
    _lazy_properties = ['id', 'date', 'time', 'ts', 'ref_ts_delay',
                        'lat_ts_delay', 'woi', 'uni', 'bi',
                        'uni_chan', 'bi_chan', 'ref_chan']

    def __init__(self, data_source, filename):
        self._data_source = data_source
        self._filename = filename
        self._loaded = False
        for prop in self._lazy_properties:
            self.__setattr__(prop, None)

    def load(self):
        with self._data_source.open(self._filename) as f:
            root = etree.parse(f).getroot()
            self.id = root.get('ID')
            self.date = root.get('Date')
            self.time = root.get('Time')

            # Annotations
            annotations = root.find('Annotations')
            self.ts = int(annotations.get('StartTime'))
            ref_ts_delay = int(annotations.get('Reference_Annotation'))
            self.ref_ts_delay = ref_ts_delay
            lat_ts_delay = int(annotations.get('Map_Annotation'))
            if lat_ts_delay - ref_ts_delay == - 10000:
                self.lat_ts_delay = np.nan
            else:
                self.lat_ts_delay = lat_ts_delay

            # WOI
            woi = root.find('WOI')
            self.woi = (int(woi.get("From")), int(woi.get("To")))

            # Voltages
            voltages = root.find('Voltages')
            self.uni = float(voltages.get("Unipolar"))
            self.bi = float(voltages.get("Bipolar"))

            # ECG datafile
            ecg = root.find('ECG')
            ecg_filename = ecg.get('FileName')

        # Read the headers of the ecg_filename
        with self._data_source.open(ecg_filename) as f:
            f.readline()  # Skip headers
            f.readline()
            mapping_chan_line = f.readline().decode('utf-8')
        mapping_chan = re.match(r'Unipolar Mapping Channel=(?P<uni>[\w-]+) '
                                r'Bipolar Mapping Channel=(?P<bi>[\w-]+)'
                                r'( Reference Channel=(?P<ref>[\w-]+))?', mapping_chan_line)

        uni_chan, bi_chan, ref_chan = mapping_chan['uni'], mapping_chan['bi'], mapping_chan['ref']
        self.uni_chan = uni_chan.replace('_', ' ')
        self.bi_chan = bi_chan.replace('_', ' ')
        self.ref_chan = ref_chan.replace('_', ' ')
        self._loaded = True

    def __getattribute__(self, item):
        if item in SigReference._lazy_properties:
            if not self._loaded:
                self.load()
        return super().__getattribute__(item)

    def __repr__(self):
        if self._loaded:
            ref_info = f' ref: {self.ref_chan}' if self.ref_chan else ''
            return f'<Signal Reference: @ts {self.ts}, channels: {self.uni_chan} | {self.bi_chan}{ref_info}>'
        return '<Signal Reference (lazy load)>'

    @property
    def filename(self):
        return self._filename

    @property
    def loaded(self):
        return self._loaded


class Point:
    def __init__(self, id, x, y, z,
                 a=0., b=0., g=0.,
                 uni=0., bi=0.,
                 lat=np.nan, imp=0.,
                 type=0, label=-1, cath_id=0,
                 sig_ref: SigReference = None):
        self.id = id
        self.x, self.y, self.z = x, y, z
        self.a, self.b, self.g = a, b, g
        self.uni, self.bi = uni, bi
        self.lat, self.imp = lat, imp
        self.type, self.label, self.cath_id = PointType(type), PointLabel(label), cath_id
        self._ref = sig_ref

    @classmethod
    def from_line(cls, line):
        components = line.split("\t")
        pt_id = components[2]
        cath_id = int(components[19])
        xyzabg = [float(i) for i in components[4:10]]
        unibi = [float(i) for i in components[10:12]]
        lat = int(components[12])
        if lat == -10000:
            lat = np.nan
        imp = float(components[13])
        type_label = [int(i) for i in components[14:16]]
        return cls(pt_id, *xyzabg, *unibi, lat, imp, *type_label, cath_id)

    def __repr__(self):
        return f"<Point id='{self.id}' @ {self.x}, {self.y}, {self.z} - bi:{self.uni}, uni:{self.uni}, lat:{self.lat}>"

    @property
    def pos(self):
        return [self.x, self.y, self.z]

    @pos.setter
    def pos(self, value):
        self.x, self.y, self.z = value

    @property
    def angle(self):
        return [self.a, self.b, self.g]

    @angle.setter
    def angle(self, value):
        self.a, self.b, self.g = value

    @property
    def ref(self):
        if not self._ref.loaded:
            self._ref.load()
        return self._ref

    @ref.setter
    def ref(self, value):
        if not isinstance(value, SigReference):
            raise ValueError('Signal reference must be a reference object.')
        self._ref = value


class PointSet(MutableMapping):
    def __init__(self, name, points:dict =None):
        self._name = name
        self._points = points if points else {}

    @classmethod
    def from_file(cls, data_source, filename):
        with data_source.open(filename) as car_file:
            line = car_file.readline().decode('utf-8')
            header = re.match(r'VERSION_(?P<version>[\d_])+ (?P<map_name>[^\r\n]+)', line)
            name = header['map_name']
            version = header['version'].replace('_', '.')
            points = {}
            for line in car_file:
                pt = Point.from_line(line.decode('utf-8'))
                pt.ref = SigReference(data_source, f'{name}_P{pt.id}_Point_Export.xml')
                points[pt.id] = pt
        return cls(name, points)

    @property
    def name(self):
        return self._name

    @property
    def car_filename(self):
        return f"{self.name}_car.txt"

    def __getitem__(self, item):
        if isinstance(item, int):
            item = list(self.keys())[item]
        return self._points.__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = list(self.keys())[key]
        if isinstance(key, str):
            if not key.isnumeric() or int(key) < 1:
                raise TypeError('Keys must be a string representation of a positive integer.')
        return self._points.__setitem__(key, value)

    def __delitem__(self, key):
        if isinstance(key, int):
            key = list(self.keys())[key]
        return self._points.__delitem__(key)

    def __len__(self):
        return self._points.__len__()

    def __iter__(self):
        return self._points.__iter__()

    def __repr__(self):
        return f"<Map '{self.name}': {len(self._points)} points>"