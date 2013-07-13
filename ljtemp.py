# 200ua current out: calibration at Block 5, starting byte 8
# see: http://labjack.com/support/u6/users-guide/5.4

import u6
import csv
import re

# TODO: only one sensor supported for now. When adding more, just modify voltage to return
# the right differential voltages
MAX_NUM_PROBES = 3


class LJTemp():

    def __init__(self):
        self.probes = []
        self.connected = False
        self.__rtd_table = {}

    def connect(self):
        """ Connect to labjack device. """
        if not self.connected:
            self.lj = u6.U6()
            self.lj.getCalibrationData()
            self.connected = True

    def disconnect(self):
        """ Disconnect from labjack device """
        if self.connected:
            self.connected = False
            self.lj.close()

    def add_probe(self, probe):
        """ Add a probe to the list of connected probes.

        Arguments:

        - `probe`: a TemperatureProbe object
        """
        self.probes.append(probe)

    def temperature_of_probe(self, probe):
        """ Return temperature measured by the probe in celsius"""
        if not self.connected:
            raise Exception('Not connected to labjack')
        volts = self._voltage(probe)
        if (probe.kind == 'RTD'):
            resistance = self._resistance_for(volts, self._calibrated_current())
            return self._rtd_temperature(resistance, probe.model)
        else:
            raise Exception('TemperatureProbe kind {0} not supported.'.format(probe.kind))

    def _calibrated_current(self):
        """ Return factory calibration data for the U6 200uA current source in volts"""
        if not self.connected:
            raise Exception('Not connected to labjack')
        return self.lj.calInfo.currentOutput1

    def _voltage(self, probe):
        """ Return voltage difference between probe plus_input and minus_input

        Arguments:

        - `probe` (TemperatureProbe): a configured probe object
        """
        if not self.connected:
            raise Exception('Not connected to labjack')

        # Build map of supported labjack AIN registers
        register = {}
        for i in range(0, MAX_NUM_PROBES+1):
            register['AIN'+str(i)] = i

        # ensure supported values were given
        if (probe.plus_input not in register):
            raise Exception("Invalid ain_input: {0}".format(probe.plus_input))
        if (probe.minus_input not in (register.keys() + ['GND'])):
            raise Exception("Invalid ain_reference: {0}".format(probe.minus_input))

        # read AIN0-AIN3 all at once to a list
        ains = self.lj.readRegister(0, numReg=8)
        plus_volt = ains[register[probe.plus_input]]
        if probe.minus_input == 'GND':
            minus_volt = 0.0
        else:
            minus_volt = ains[register[probe.minus_input]]
        result = plus_volt - minus_volt
        return result

    def _resistance_for(self, volts, amps):
        """ Return the resistance in ohms for given current and voltage"""
        if amps == 0:
            raise ZeroDivisionError('Cannot measure resistance if current is null.')
        return volts / amps

    def _rtd_table(self, probe_model):
        """ Return array of (resistance, temperature) tuples for the given RTD probe model.
        Load data from file if needed and cache it."""

        if probe_model not in self.__rtd_table:
            # load table from csv file, which must be sorted by resistance!
            with open('maltabar.csv', 'rU') as csvfile:
                reader = csv.DictReader(csvfile)
                self.__rtd_table[probe_model] = []
                for row in reader:
                    # only add entries that have a not empty resistance
                    if row[probe_model]:
                        resistance = float(row[probe_model])
                        temperature = float(re.sub('_', '-', row['Celsius']))
                        datapoint = (resistance, temperature)
                        self.__rtd_table[probe_model].append(datapoint)
        return self.__rtd_table[probe_model]

    def _rtd_temperature(self, ohms, probe_model):
        """ Return the temperature in Celsius for a RTD sensor given its resistance

        Uses linear interpolation from table at http://en.wikipedia.org/wiki/Resistance_thermometer

        Arguments:
        - `ohms` (float): measured resistance in ohms
        - `probe_model`: one of 'pt100', 'pt1000', 'ptc', 'ntc-101', ..., 'ntc-105'
        """
        # open table with resistance / temp mappings
        model_codes = {'pt100': '404',
                        'pt1000': '501',
                        'ptc': '201',
                        'ntc-101': '101',
                        'ntc-102': '102',
                        'ntc-103': '103',
                        'ntc-104': '104',
                        'ntc-105': '105'}
        if probe_model not in model_codes:
            raise Exception('unsupported probe model: {0}'.format(probe_model))
        model_code = model_codes[probe_model]

        data = self._rtd_table(model_code)

        # find closest match in table of resistances
        ohms = float(ohms)
        previous_res = None
        previous_temp = None
        for res, temp in data:
            if res == ohms:
                return temp
            if res < ohms:
                previous_res = res
                previous_temp = temp
            if res > ohms:
                if previous_res is None:
                    raise Exception('Resistance {0} ohms out of range, too small'.format(ohms))
                return self._interpolate(previous_res, previous_temp, res, temp, ohms)
        raise Exception('Resistance out of range, too large')

    def _interpolate(self, x1, y1, x2, y2, x3):
        """ Return y3 for x3, given points (x1,y1) and (x2,y2). """
        return float(y1 + (y2-y1) * (x3-x1) / (x2-x1))
