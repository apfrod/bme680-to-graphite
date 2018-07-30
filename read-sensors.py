#!/usr/bin/env python

# see /lib/systemd/system/sensors.service

# from https://github.com/pimoroni/bme680/tree/master/examples

import bme680
import time
import socket

CARBON_SERVER = '0.0.0.0'
CARBON_PORT = 2003
DEBUG = True

sensor = bme680.BME680()

# These calibration data can safely be commented
# out, if desired.

print("Calibration data:")
for name in dir(sensor.calibration_data):

    if not name.startswith('_'):
        value = getattr(sensor.calibration_data, name)

        if isinstance(value, int):
            print("{}: {}".format(name, value))

# These oversampling settings can be tweaked to 
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_4X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

print("\n\nInitial reading:")
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print("{}: {}".format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# Up to 10 heater profiles can be configured, each
# with their own temperature and duration.
# sensor.set_gas_heater_profile(200, 150, nb_profile=1)
# sensor.select_gas_heater_profile(1)

sock = socket.socket()
sock.connect((CARBON_SERVER, CARBON_PORT))

def send_msg(message):
    sock.sendall(message)

try:
    while True:

	if sensor.get_sensor_data():
	    timestamp = int(time.time())
	    lines = [
		'sensor.temperature    {0:.2f} {1}'.format(sensor.data.temperature,    timestamp),
		'sensor.pressure       {0:.2f} {1}'.format(sensor.data.pressure,       timestamp),
		'sensor.humidity       {0:.2f} {1}'.format(sensor.data.humidity,       timestamp)
	    ]
	    if sensor.data.heat_stable:
		lines.append(
		    'sensor.gas_resistance {0:.2f} {1}'.format(sensor.data.gas_resistance, timestamp)
		)

	    message = '\n'.join(lines) + '\n'

	    if DEBUG == True:
		print(message)

	    send_msg(message)

	time.sleep(1)

except KeyboardInterrupt:
    pass

sock.close()
