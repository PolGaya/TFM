import matplotlib.pyplot as plt
import numpy as np
import qcodes as qc  
from my_devs import li, station, dac_adc, agilent
from qcodes.instrument_drivers.stanford_research.SR830 import SR830 
import time

# Set up station
station = qc.Station()
station.add_component(li)
station.add_component(dac_adc)
station.add_component(agilent)

# Experimental parameters
frequency = 137                           # Hz
real_amplitude_rms = 0.01                  # Vrms (what we want as real AC output)

# Correction factors based on measurements
scaling_offset = 1                     # Real DC offset = 2.15 * set value
scaling_ac = 1                        # Real AC output = 1.821 * set AC voltage

# Compensated values to apply
set_amplitude_rms = real_amplitude_rms / scaling_ac

real_offset_range = np.linspace(0, 0.5, 101)           # Real DC offset sweep (0 V to 1 V)
set_offset_values = real_offset_range / scaling_offset  # Compensated values to send to Agilent

# ------------------------
# Configure Function Generator (Agilent)
# ------------------------
agilent.instrument.write('FUNC SIN')                    
agilent.instrument.write('VOLT:UNIT VRMS')              
agilent.instrument.write(f'FREQ {frequency}')           
agilent.instrument.write(f'VOLT {set_amplitude_rms:.6f}')   # Apply corrected AC voltage
agilent.instrument.write('OUTP ON')                     

# ------------------------
# Configure Lock-in Amplifier (SR830)
# ------------------------
li.reference_source('external')                         
li.frequency(frequency)
li.sensitivity(1e-9)                                       
li.time_constant(0.3)                                   

print("Waiting for lock-in to stabilize...")
time.sleep(5)

# ------------------------
# Sweep Loop
# ------------------------
currents = []
results = []

for v_real, v_set in zip(real_offset_range, set_offset_values):
    agilent.instrument.write(f'VOLT:OFFS {v_set:.6f}')  # Set corrected offset
    time.sleep(0.2)  # Stabilization

    x = li.X()
    y = li.Y()
    r = li.R()
    theta = li.P()

    resistance = real_amplitude_rms / r if r != 0 else float('inf')

    print(f"Real V_offset: {v_real:.2f} V | X: {x:.6e} A | R: {r:.6e} A | Resistance: {resistance:.2f} Ω")

    currents.append(r)
    results.append((v_real, x, r, resistance))

# ------------------------
# Cleanup
# ------------------------
agilent.instrument.write('OUTP OFF')
agilent.close()
dac_adc.close()


# Plotting
voltages = real_offset_range
plt.figure(figsize=(8, 5))
plt.plot(voltages, currents, 'o-', color='blue', label='I vs V')
plt.xlabel('Applied DC Offset (V)')
plt.ylabel('Measured Current (A)')
plt.title('Current vs DC Offset Voltage')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()