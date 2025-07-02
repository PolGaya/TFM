import time
import threading
import matplotlib.pyplot as plt
import numpy as np
import qcodes as qc  
from my_devs import li, station, dac_adc, agilent
from qcodes.instrument_drivers.stanford_research.SR830 import SR830

# -------------------- Serial Access from dac_adc --------------------

# Try to access the serial port used by dac_adc (if exposed)
try:
    ser = dac_adc.ser  # ← must exist in your DAC_ADC class
except AttributeError:
    raise AttributeError("Your 'DAC_ADC' class must expose 'self.ser' for direct serial access.")

serial_lock = threading.Lock()

def set_voltage(channel, voltage):
    command = f"SET\n,\n{channel}\n,\n{voltage}\n\r"
    with serial_lock:
        ser.write(command.encode())

# -------------------- QCoDeS Instrument Setup --------------------

station = qc.Station()
station.add_component(li)
station.add_component(dac_adc)
station.add_component(agilent)

# Agilent Parameters
frequency = 137
real_amplitude_rms = 0.01  # Vrms
scaling_offset = 1
scaling_ac = 1
set_amplitude_rms = real_amplitude_rms / scaling_ac

# Configure Agilent
agilent.instrument.write('FUNC SIN')                    
agilent.instrument.write('VOLT:UNIT VRMS')              
agilent.instrument.write(f'FREQ {frequency}')           
agilent.instrument.write(f'VOLT {set_amplitude_rms:.6f}')  
agilent.instrument.write('OUTP ON')                     

# Configure Lock-in Amplifier
li.reference_source('external')                         
li.frequency(frequency)
li.sensitivity(1e-9)                                       
li.time_constant(0.3)                                   

print("Waiting for lock-in to stabilize...")
time.sleep(5)

# -------------------- Sweep Config --------------------

# DAC sweep values
dac_channel = 2
dac_voltage_values = np.linspace(0.25, 1, 10)

# Agilent offset sweep
real_offset_range = np.linspace(-0.5, 0.5, 101)
set_offset_values = real_offset_range / scaling_offset

# Storage for results
results = []

# -------------------- Real-Time Plotting Setup --------------------
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(figsize=(10, 6))

# Create a line for each DAC voltage value
lines = {}
colors = plt.cm.viridis(np.linspace(0, 1, len(dac_voltage_values)))

for i, dac_v in enumerate(dac_voltage_values):
    line, = ax.plot([], [], label=f'DAC = {dac_v:.2f} V', color=colors[i])
    lines[dac_v] = line

ax.set_xlabel('Agilent Offset Voltage (V)')
ax.set_ylabel('Measured Current (A)')
ax.set_title('Real-Time Current vs Agilent Offset Voltage')
ax.grid(True)
ax.legend()
plt.tight_layout()

# -------------------- Main Experiment Loop --------------------
for dac_v in dac_voltage_values:
    print(f"\nSetting DAC channel {dac_channel} to {dac_v:.2f} V")
    set_voltage(dac_channel, dac_v)
    time.sleep(1)

    currents = []
    offsets = []

    for v_real, v_set in zip(real_offset_range, set_offset_values):
        agilent.instrument.write(f'VOLT:OFFS {v_set:.6f}')
        time.sleep(0.3)

        x = li.X()
        y = li.Y()
        r = li.R()
        theta = li.P()

        resistance = real_amplitude_rms / r if r != 0 else float('inf')
        results.append((dac_v, v_real, x, r, resistance))
        currents.append(r)
        offsets.append(v_real)

        print(f"DAC: {dac_v:.2f} V | Agilent: {v_real:.2f} V | R: {r:.2e} A | Resistance: {resistance:.2f} Ω")

        # Real-time update of plot
        line = lines[dac_v]
        line.set_data(offsets, currents)
        ax.relim()  # Recalculate limits
        ax.autoscale_view()  # Autoscale the view
        plt.pause(0.01)  # brief pause to refresh the figure

# -------------------- Cleanup --------------------
agilent.instrument.write('OUTP OFF')
agilent.close()
set_voltage(dac_channel, 0)

# -------------------- Finalize Plot --------------------
plt.ioff()  # Turn off interactive mode
plt.show(block=True)  # Keep the plot open until manually closed

dac_adc.close()
