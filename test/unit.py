import unittest2 as unittest


class TestLabjack(unittest.TestCase):

    def setUp(self):
        import ljtemp
        self.l = ljtemp.LJTemp()

    def test_calibrated_current(self):
        # read factory calibrated current from the labjack
        current = self.l.calibrated_current()
        self.assertAlmostEqual(current, 0.000200, delta=0.000010,
                               msg='Calibrated current not close to 200uA')

    def test_voltage_range(self):
        # make sure we can read voltages and in range [0 - 0.35] volt
        # for 3 resistors
        # for PT100, expect [0.016 - 0.035] V
        # for PT1000, expect [0.16 - 0.35] V
        for i in range(0, 2):
            volt = self.l.voltage(i)
            self.assertTrue((volt > 0.016) and (volt < 0.35),
                            msg='Voltage #{0} is {1}, should be in range [0.016-0.350] volt'
                .format(i, volt))

    def test_temp_range(self):
        # temp in range [-50 - 200] celcius
        for i in range(0, 2):
            temp = self.l.temperature(i)
            self.assertTrue((temp > -50.0) and (temp < 200.0),
                            msg='Temperature #{0} is {1}, should be in range [-50-200] celcius'
                .format(i, temp))

if __name__ == '__main__':
    unittest.main()
