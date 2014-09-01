#!/usr/bin/env python

from ljtemp import LJTemp
from ljtemp import TemperatureProbe

ljt = LJTemp()
ljt.connect()
probe = TemperatureProbe(name='R0', kind='RTD', model='pt1000',
                                 plus_input='AIN0', minus_input='GND')
ljt.add_probe(probe)
for probe in ljt.probes:
    temp = ljt.temperature_of_probe(probe)
    print temp
