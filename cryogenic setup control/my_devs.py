'''
Create the experimental station with the devices that will be used in the experiment.
'''
import qcodes as qc
from qcodes.instrument_drivers.stanford_research.SR830 import SR830
from DAC_ADC import DAC_ADC
from agilent_33220a import Agilent_33220A

station = qc.Station()

li = SR830(name='lock-in',address='GPIB0::8::INSTR')
dac_adc = DAC_ADC(port='COM5', baudrate=115200, timeout=1)
agilent = Agilent_33220A('GPIB0::30::INSTR')

station.add_component(li)
station.add_component(dac_adc)
station.add_component(agilent)