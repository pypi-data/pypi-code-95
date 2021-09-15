from collections.abc import Mapping
from .datasource import DataSource
from .mesh import Mesh
from .points import PointSet, Point
from .signals import Channel, CARTO_SIGNAL_FILE_LENGTH
import numpy as np
import re
from tqdm import tqdm
from xml.etree import ElementTree as etree


class Map:
    def __init__(self, data_source, map_name):
        # Initialize the mesh and point list by reading the .mesh and .car files
        self._map_name = map_name
        self._mesh = Mesh.from_file(data_source, f'{map_name}.mesh')
        self._points = PointSet.from_file(data_source, f'{map_name}_car.txt')

    @property
    def name(self):
        return self._map_name

    @property
    def points(self):
        return self._points

    @property
    def mesh(self):
        return self._mesh

    def __repr__(self):
        return f'<Map {self.name}: {len(self.points)} Points, {self.mesh.num_v} x {self.mesh.num_t} Mesh>'


class Carto(Mapping):
    def __init__(self, path):
        self._data_source = DataSource(path)

        # Get the list of maps from the list of car files
        self._maps = {file[:-8]: None for file in self._data_source.listdir() if file.endswith('_car.txt')}
        self._signals = {}
        self._integrated_files = set()

    def __getitem__(self, item):
        if isinstance(item, int):
            item = list(self.keys())[item]
        if self._maps[item] is None:
            self._maps[item] = Map(self._data_source, item)
        return self._maps.__getitem__(item)

    def __iter__(self):
        return self._maps.__iter__()

    def __len__(self):
        return self._maps.__len__()

    def __repr__(self):
        return f"<Carto Data: {self.__len__()} maps>"

    def add_signal_files(self, map_name=None):
        file_list = {file for file in self.data_source.listdir() if file.endswith('Point_Export.xml')}
        if map_name in self:
            file_list = {file for file in self.data_source.listdir() if file.startswith('map_name')}
        elif map_name is not None:
            raise ValueError('Unknown map')

        for file in tqdm(file_list, ncols=50):
            self.add_signal_file(file)

    def add_signal_file(self, filename):
        if filename in self._integrated_files:
            return

        # We first need to read the xml file to read the timestamp and the name of the txt file with the signals
        with self.data_source.open(filename) as f:
            root = etree.parse(f).getroot()
            annotations = root.find('Annotations')
            start_ts = int(annotations.get('StartTime'))
            ecg = root.find('ECG')
            ecg_filename = ecg.get('FileName')

        # We then need to open the sig file to get the channel names and check if we already have the signals we need
        with self.data_source.open(ecg_filename) as f:
            f.readline()  # Version header
            gain_line = f.readline().decode('utf-8')
            gain = float(re.match(r'Raw ECG to MV \(gain\) = (?P<gain>[\d\.]+)', gain_line)['gain'])
            mapping_chan_line = f.readline().decode('utf-8')
            # mapping_chan = re.match(r'Unipolar Mapping Channel=(?P<uni>[\w-]+) '
            #                         r'Bipolar Mapping Channel=(?P<bi>[\w-]+)'
            #                         r'( Reference Channel=(?P<ref>[\w-]+))?', mapping_chan_line)
            #
            # uni_chan, bi_chan, ref_chan = mapping_chan['uni'], mapping_chan['bi'], mapping_chan['ref']
            # uni_chan = uni_chan.replace('_', ':')
            # bi_chan = bi_chan.replace('_', ':')
            # ref_chan = ref_chan.replace('_', ':')

            labels_line = f.readline().decode('utf-8')
            labels = [re.match(r'(?P<name>[\w_-]+)\((?P<id>\d+)\)', label)['name'] for label in labels_line.split()]
            labels = [label.replace('_', ' ') for label in labels]

            # Now check we have the necessary channels info
            if all([label in self._signals and
                    self._signals[label].defined(start_ts, start_ts + CARTO_SIGNAL_FILE_LENGTH)
                    for label in labels]):
                self._integrated_files.add(filename)
                return

            # If we don't, we need to add the channels to the dataset
            # Get the signals
            signals = np.loadtxt(f).transpose()
            signals *= gain

        # Store them
        for label, signal in zip(labels, signals):
            if label not in self._signals:
                self._signals[label] = Channel(label)
            self._signals[label].add(signal, start_ts)
        self._integrated_files.add(filename)

    @property
    def data_source(self):
        return self._data_source

    @property
    def sig(self):
        return self._signals

    def signal_from_point(self, point: Point, interval: slice = slice(-500, 500)):
        if not isinstance(interval, slice):
            raise TypeError('Input interval must be a slice.')
        if interval.start is None or interval.stop is None:
            raise ValueError('Interval start and stop points must be defined.')

        offset = point.ref.ts + point.ref.ref_ts_delay
        offset_interval = slice(offset + interval.start, offset + interval.stop, interval.step)

        # Make sure we already integrated the signal file to our data
        self.add_signal_file(point.ref.filename)


        results = {
            't': np.arange(interval.start, interval.stop, interval.step),
            'uni': self.sig[point.ref.uni_chan][offset_interval],
            'bi': self.sig[point.ref.bi_chan][offset_interval],
        }

        if point.ref.ref_chan is not None:
            results['ref'] = self.sig[point.ref.ref_chan][offset_interval]

        return results

    def plot_point(self, point: Point, *args, **kwargs):
        try:
            from matplotlib import pyplot as plt
        except ImportError:
            raise ImportError('Matplotlib must be installed to plot signals. '
                              'Use pip install carto_reader[viz] to install visualization dependencies.')

        # Get signal
        sigs = self.signal_from_point(point, *args, **kwargs)

        uni = plt.plot(sigs['t'], sigs['uni'], 'r')
        bi = plt.plot(sigs['t'], sigs['bi'], 'b')
        try:
            ref = plt.plot(sigs['t'], sigs['ref'], 'g')
            plt.legend([f'Unipolar ({point.ref.uni_chan})',
                        f'Bipolar ({point.ref.bi_chan})',
                        f'Ref ({point.ref.ref_chan})'])
        except KeyError:
            plt.legend([f'Unipolar ({point.ref.uni_chan})', f'Bipolar ({point.ref.bi_chan})'])

        plt.axvline(point.ref.lat_ts_delay - point.ref.ref_ts_delay, c='k', ls='--')