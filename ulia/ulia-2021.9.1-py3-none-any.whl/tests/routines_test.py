#!/usr/bin/env python3

import unittest
import numpy as np
import ulia.routines as rt


class RoutinesIntegrationTest(unittest.TestCase):

    def setUp(self):
        """
        Connect to the database, create/clear the table.
        """
        self.modulation_frequency = 5000.0
        self.sampling_rate = 200000.0
        self.time = np.arange(0, 0.3*self.sampling_rate) / self.sampling_rate
        self.signal = np.cos(2*np.pi*self.time*self.modulation_frequency)
        self.reference = np.cos(2*np.pi*self.time*self.modulation_frequency)

    def test_create_ulia(self):
        """
        Check that a ulia object can be created.
        """
        # TODO

    def test_demodulate_simple_signal(self):
        """
        Check the correct demodulation of simple noiseless signal.
        """
        lia = rt.ULIA(self.signal.size, self.sampling_rate, 0.03, 2, 0.2)
        lia.load_data(self.reference, self.signal)
        lia.execute()

        x = np.mean(lia.x[int(0.3*lia.x.size):int(0.9*lia.x.size)])
        y = np.mean(lia.y[int(0.3*lia.y.size):int(0.9*lia.y.size)])

        # Amplitude
        self.assertAlmostEqual(np.abs(x+1j*y), 0.5000, places=4)
        # Phase
        self.assertAlmostEqual(np.angle(x+1j*y), 0.0, places=4)

    def test_demodulate_white_noise_signal(self):
        """
        Check the correct demodulation of simple noisy signal.
        """
        np.random.seed(1234)
        lia = rt.ULIA(self.signal.size, self.sampling_rate, 0.03, 2, 0.2)
        lia.load_data(self.reference,
                      self.signal + np.random.normal(size=self.signal.size))
        lia.execute()

        x = np.mean(lia.x[int(0.3*lia.x.size):int(0.9*lia.x.size)])
        y = np.mean(lia.y[int(0.3*lia.y.size):int(0.9*lia.y.size)])

        self.assertAlmostEqual(np.abs(x+1j*y), 0.4982, places=4)

    def test_demodulate_noise_frequencies_signal(self):
        """
        Check the correct demodulation of a signal contaminated by other
        frequencies.
        """
        parasitic_frequencies = [30, 3000, 6000, 34500]
        lia = rt.ULIA(self.signal.size, self.sampling_rate, 0.03, 2, 0.2)
        signal = self.signal
        for pf in parasitic_frequencies:
            signal += np.cos(2*np.pi*self.time*pf)
        lia.load_data(self.reference, signal)
        lia.execute()

        x = np.mean(lia.x[int(0.3*lia.x.size):int(0.9*lia.x.size)])
        y = np.mean(lia.y[int(0.3*lia.y.size):int(0.9*lia.y.size)])

        # Amplitude
        self.assertAlmostEqual(np.abs(x+1j*y), 0.5000, places=4)
        # Phase
        self.assertAlmostEqual(np.angle(x+1j*y), 0.0, places=4)

    def test_filter_cherb1_bandpass(self):
        """
        Chech the correct filter functionality of the Cherbyshev 1 bandpass
        filter.
        """
        parasitic_frequencies = [30, 3000, 6000, 34500]
        signal = self.signal
        for pf in parasitic_frequencies:
            signal += np.cos(2*np.pi*self.time*pf)

        signal = rt.cheb_bandpass_filter(signal, (4900, 5100),
                                         self.sampling_rate)
        fourier_signal = np.fft.fft(signal)

        self.assertEqual(np.where(fourier_signal == np.max(fourier_signal))[0],
                         58500)


if __name__ == "__main__":
    unittest.main()
