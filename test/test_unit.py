import unittest

# set to False to disable tests requiring a connected labjack device
connected_mode = True


class TestLabjack(unittest.TestCase):

    def setUp(self):
        import ljtemp
        self.ljt = ljtemp.LJTemp()
	if connected_mode: 
	    self.ljt.connect()
        probe = ljtemp.Probe(name='R0', kind='RTD', model='pt1000', plus_input='AIN0',
                             minus_input='GND')
        self.ljt.add_probe(probe)

    def tearDown(self):
        self.ljt.disconnect()

    @unittest.skipIf(not connected_mode, "in disconnected mode.")
    def test_calibrated_current(self):
        # read factory calibrated current from the labjack
        current = self.ljt._calibrated_current()
        self.assertAlmostEqual(current, 0.000200, delta=0.000010,
                               msg='Calibrated current not close to 200uA')

    @unittest.skipIf(not connected_mode, "in disconnected mode.")
    def test_voltage_range(self):
        # make sure we can read voltages and in range [0 - 0.35] volt
        # for 3 resistors
        # for PT100, expect [0.016 - 0.035] V
        # for PT1000, expect [0.16 - 0.35] V
        for probe in self.ljt.probes:
            volt = self.ljt._voltage(probe)
            self.assertTrue((volt > 0.016) and (volt < 0.35),
                            msg='Voltage of probe {0} is {1}, should be in range [0.016-0.350] volt'
                .format(probe.name, volt))

    @unittest.skipIf(not connected_mode, "in disconnected mode.")
    def test_null_voltage(self):
        # make sure we get 0V between two similar entries
        for connector in ['AIN0', 'AIN1', 'AIN2', 'AIN3']:
            from ljtemp import Probe
            probe = Probe(name='test'+connector, kind='RTD', model='PT1000', plus_input=connector,
                          minus_input=connector)
            volt = self.ljt._voltage(probe)
            self.assertEqual(volt, 0, 'Voltage on single input should be zero')

    @unittest.skipIf(not connected_mode, "in disconnected mode.")
    def test_temp_range(self):
        # temp in range [-50 - 200] celcius
        for probe in self.ljt.probes:
            temp = self.ljt.temperature_of_probe(probe)
            self.assertTrue((temp > -50.0) and (temp < 200.0),
                            msg='Temperature of probe {0} is {1}, should be in range [-50-200] celsius'
                .format(probe.name, temp))

    def test_resistance_for(self):
        # should obey Ohm's law
        self.assertEqual(self.ljt._resistance_for(volts=10, amps=0.2), 50, "Ohm's law violated")

    def test_interpolate(self):
        self.assertEqual(self.ljt._interpolate(0, 0, 10, 100, 2), 20.0)

    def test_rtd_temperature_match(self):
        # should return correct temperatures for resistances in the table
        self.assertEqual(-50.0, self.ljt._rtd_temperature(80.31, 'pt100'))
        self.assertEqual(-50.0, self.ljt._rtd_temperature(803.1, 'pt1000'))
        self.assertEqual(-50.0, self.ljt._rtd_temperature(1032.0, 'ptc'))
        self.assertEqual(0.0, self.ljt._rtd_temperature(100.0, 'pt100'))
        self.assertEqual(0.0, self.ljt._rtd_temperature(1000.0, 'pt1000'))
        self.assertEqual(0.0, self.ljt._rtd_temperature(1628.0, 'ptc'))
        self.assertEqual(100.0, self.ljt._rtd_temperature(138.5, 'pt100'))
        self.assertEqual(100.0, self.ljt._rtd_temperature(1385.0, 'pt1000'))
        self.assertEqual(100.0, self.ljt._rtd_temperature(3390.0, 'ptc'))

    def test_rtd_temperature_interpolate(self):
        # should return correct temperatures for resistances interpolated from the table
        self.assertAlmostEqual(-6.0, self.ljt._rtd_temperature(97.65, 'pt100'), 5)
        self.assertAlmostEqual(-6.0, self.ljt._rtd_temperature(976.5, 'pt1000'), 5)
        self.assertAlmostEqual(-6.0, self.ljt._rtd_temperature(1547.4, 'ptc'), 5)

    def test_rtd_temperature_out_of_range(self):
        # resistance too low
        self.assertRaises(Exception, self.ljt._rtd_temperature, 80.30, 'pt100')
        self.assertRaises(Exception, self.ljt._rtd_temperature, 803.0, 'pt1000')
        self.assertRaises(Exception, self.ljt._rtd_temperature, 1031.0, 'ptc')
        # resistance too high
        self.assertRaises(Exception, self.ljt._rtd_temperature, 175.85, 'pt100')
        self.assertRaises(Exception, self.ljt._rtd_temperature, 1758.5, 'pt1000')
        self.assertRaises(Exception, self.ljt._rtd_temperature, 3391.0, 'ptc')


if __name__ == '__main__':
    unittest.main()
