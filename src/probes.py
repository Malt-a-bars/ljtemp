class TemperatureProbe():
    """ Class for temperature sensors settings. """
    def __init__(self, name='',
                 kind='RTD',
                 model='PT1000',
                 plus_input='AIN0',
                 minus_input='GND'
                 ):
        """ Configure a new probe

        Arguments:
        - `name` (str): user defined name for the probe
        - `kind` (str): 'RTD' is the only kind supported
        - `model` (str): 'PT100' or 'PT1000'
        - `plus_input` (str): labjack input to measure voltage from
        - `minus_input` (str): labjack input to substract voltage from. Can be 'GND'
        """
        self.name = name
        self.kind = kind
        self.model = model
        self.plus_input = plus_input
        self.minus_input = minus_input
        self._mock_temp = 66.0
