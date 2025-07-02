import serial
import time
from time import sleep
import threading  # Import threading for parallel execution

# Initialize serial connection
ser = serial.Serial('COM5', 115200, timeout=1)  # Adjust for your device
time.sleep(2)

if not ser.isOpen():
    print("opened")
    ser.open()

# Create a lock to synchronize access to the serial port
serial_lock = threading.Lock()

# Helper function to send a command with the lock to ensure thread-safe access to the serial port
def send_command(command):
    with serial_lock:  # Acquire the lock before writing
        ser.write(command)
        response = ser.readline()
        if command == b"*RDY?\n\r" or b'*IDN?\n\r':
            print(response.decode())

# Operation to set voltage to a channel
def set_voltage(channel, voltage):
    channel = str(channel)
    voltage = str(voltage)
    command = "SET\n,\n" + channel + "\n,\n" + voltage + "\n\r"
    with serial_lock:  # Acquire the lock before writing
        ser.write(command.encode())

# Voltage sweep function for a single channel
def sweep_voltage(channel, start_voltage, end_voltage, step_size, delay_seconds):
    """
    Sweeps the voltage from start_voltage to end_voltage with a given step_size.
    A delay in seconds is added between each voltage setting.
    Displays the estimated actual voltage sensed by the multimeter (5% higher).
    """
    current_voltage = start_voltage
    while current_voltage <= end_voltage:
        set_voltage(channel, current_voltage)
        sensed_voltage = current_voltage * 1.05  # 5% higher
        print(f"Set channel {channel} to {current_voltage:.2f}V (estimated sensed: {sensed_voltage:.2f}V)")
        sleep(delay_seconds)
        current_voltage += step_size


# Voltage sweep function for multiple channels with independent parameters
def sweep_multiple_channels(channels_params):
    threads = []  # List to hold threads for parallel execution
    for channel, params in channels_params.items():
        start_voltage, end_voltage, step_size, delay_seconds = params
        # Create a thread for each channel with its own parameters
        thread = threading.Thread(target=sweep_voltage, args=(channel, start_voltage, end_voltage, step_size, delay_seconds))
        threads.append(thread)
        thread.start()  # Start the thread

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

# Example usage: Sweep voltages for each channel with independent parameters
channels_params = {
#    0: (0, 3.5, 0.1, 1),  # Channel 0: Sweep from 0V to 5V in steps of 0.1V, 0.5s delay
#    1: (1, 3, 0.2, 0.3),  # Channel 1: Sweep from 1V to 3V in steps of 0.2V, 0.3s delay
#    2: (0, 2, 0.1, 0.5),  # Channel 2: Sweep from 0V to 2V in steps of 0.05V, 0.2s delay
#    3: (2, 4, 0.1, 0.4),  # Channel 3: Sweep from 2V to 4V in steps of 0.1V, 0.4s delay
}

# Sweep all channels independently
sweep_multiple_channels(channels_params)

# Set all voltages to 0V as a final state (optional)
set_voltage(0, 0)
set_voltage(1, 0)
set_voltage(2, 0)
set_voltage(3, 0)

print("Ended")
