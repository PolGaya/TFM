
"""
Created 10/05/2024
@author Urtzi Jauregi Aberasturi
General code to perform every operation with the DAC_ADC. Class of the device to call
it from other scripts.
"""


import serial
import time

class DAC_ADC:
    def __init__(self, port='COM5', baudrate=115200, timeout=1):
        '''
        To open serial port to the device.
        '''
        #ser = serial.Serial('/dev/ttyACM0',115200,timeout=1) #Find serial port Linux
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        print("DAC-ADC device serial port opened.")
        if not self.ser.isOpen():
            print("Serial port not open, trying to open it...")
            self.ser.open()
            print("Serial port opened.")

    def send_command(self, command):
        self.ser.write(command)
        response = self.ser.readline()
        if command == b"*RDY?\n\r" or b'*IDN?\n\r':
            print(response.decode())

    def get_device_id(self):
        '''
        Operation to get device identification
        '''
        self.ser.write(b'*IDN?\n\r')
        print((self.ser.readline()).decode('utf-8', errors='ignore'))

    def is_device_ready(self):
        '''
        Operation to check if device is ready
        '''
        self.ser.write(b"*RDY?\n\r")
        print((self.ser.readline()).decode('utf-8', errors='ignore'))

    def set_voltage(self, channel, voltage):
        '''
        Operation to set voltage to a channel
        '''
        command = f"SET\n,\n{channel}\n,\n{voltage}\n\r"
        self.ser.write(command.encode())
        print((self.ser.readline()).decode('utf-8', errors='ignore'))

    def get_adc_voltage(self, channel):
        ''''
        Operation to get voltage read by an input channel
        '''
        command = f"GET_ADC\n,\n{channel}\n\r"
        self.ser.write(command.encode())
        voltage = (self.ser.readline()).decode('utf-8', errors='ignore').split()
        return float(voltage[0])

    def ramp_channel(self, channel, initial_voltage, final_voltage, num_steps, delay_microseconds):
        '''
        Operation to ramp one channel from an initial voltage to a final voltage
        '''
        command = f"RAMP1\n,\n{channel}\n,\n{initial_voltage}\n,\n{final_voltage}\n,\n{num_steps}\n,\n{delay_microseconds}\n\r"
        self.ser. write(command.encode())

    def ramp_channels(self, channel1, channel2, initial_voltage1, initial_voltage2, final_voltage1, final_voltage2, num_steps, delay_microseconds):
        '''
        Operation to ramp two channels from initial voltages to final voltages
        '''
        command = f"RAMP2\n,\n{channel1}\n,\n{channel2}\n,\n{initial_voltage1}\n,\n{initial_voltage2}\n,\n{final_voltage1}\n,\n{final_voltage2}\n,\n{num_steps}\n,\n{delay_microseconds}\n\r"
        self.ser.write(command.encode())

    def buffer_ramp(self, dac_channels, adc_channels, initial_voltages, final_voltages, num_steps, delay_microseconds, num_readings_to_avg):
        """
        This function is the one we will use for the characterization of SETS as we can do several sweeps at the same time
        and synchronously measure signals using the ACD.
        To insert the channels we want to use for the DAC and ADC we will need to introduce a list.
        For example to use channels 0,1 and 2 --> [0,1,2] will be the introduced list.

        To perform the sweep the order of the introduced voltages will be the same as the one we introduced
        at the DAC. Equally, we will be using a list so having chosen DAC channels "012" I will have initial voltages
        [0,-1,-2] and final voltages [4,2,5] the next way. CH0 [0,4]; CH1 [-1,2] and CH2 [-2,5].
        
        num_steps will be introduced asan integer such as delay_microseconds and num_readings_to_avg.
        """
        dac_channel_str = ''.join(str(channel) for channel in dac_channels)
        adc_channel_str = ''.join(str(channel) for channel in adc_channels)
        initial_voltages_str = ','.join(str(v) for v in initial_voltages)
        final_voltages_str = ','.join(str(v) for v in final_voltages)
        command = f"BUFFER_RAMP\n,\n{dac_channel_str}\n,\n{adc_channel_str}\n,\n{initial_voltages_str}\n,\n{final_voltages_str}\n,\n{num_steps}\n,\n{delay_microseconds}\n,\n{num_readings_to_avg}\n\r"
        self.ser.write(command.encode())
        print((self.ser.readline()).decode('utf-8', errors='ignore'))
    
    def convert_time(self,channel,time):
        command = f"CONVERT_TIME\n,\n{channel}\n,\n{time}\n\r"
        self.ser.write(command.encode())
    
    def close(self):
        self.ser.close()
    
    def snapshot(self, update=False):
        """
        Returns a dictionary representing the current state of the device.
        """
        # Example: Return an empty dictionary if the device state cannot be queried
        return {}