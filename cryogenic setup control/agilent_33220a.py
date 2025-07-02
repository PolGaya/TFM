import pyvisa
import numpy as np
from time import sleep
import pyvisa

class Agilent_33220A:
    """
    Class for controlling the Agilent 33220A function generator. It only contains
    the functions to open and close connections and set the offset voltage.
    
    """
    def __init__(self, address):
        """
        To open GPIB conneection to the device:
        address: str, GPIB address of the device
        """
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(address)

    def set_offset(self, val):
        """
        Set the offset voltage of the function generator. 
        val, float, offset voltage in volts
        """
        self.instrument.write(f'VOLT:OFFS {val}')

    def close(self):
        self.instrument.close()

    def snapshot(self, update=False):
        """
        Returns a dictionary representing the current state of the device.
        """
        # Example: Return an empty dictionary if the device state cannot be queried
        return {}


device = Agilent_33220A('GPIB0::30::INSTR') # Open connection to device
device.set_offset(1.0)  # Set offset to 1.0 volts
device.close() #close connection