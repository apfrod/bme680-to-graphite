#!/usr/bin/env python

# see /lib/systemd/system/sensors.service

# from https://github.com/pimoroni/bme680/tree/master/examples

import bme680
import time
import os
import socket

CARBON_SERVER = '0.0.0.0'
CARBON_PORT = 2003
DEBUG = False

# Set the humidity baseline to 40%, an optimal indoor humidity.
hum_baseline = 40.0
# calculation of air_quality_score (25:75, humidity:gas)
hum_weighting = 0.25

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

def temperature_of_raspberry_pi():
    cpu_temp = os.popen("vcgencmd measure_temp").readline()
    cpu_temp = cpu_temp.replace("temp=", "")
    return cpu_temp.replace("'C", "").strip()


start_time = time.time()
curr_time = time.time()
burn_in_time = 300

burn_in_data = []

try:
    # Collect gas resistance burn-in values, then use the average
    # of the last 50 values to set the upper limit for calculating
    # gas_baseline.
    print('Collecting gas resistance burn-in data for 5 mins\n')
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            time.sleep(1)

    print('Gas: {0} Ohms'.format(gas))

    gas_baseline = sum(burn_in_data[-50:]) / 50.0
    print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
        gas_baseline,
        hum_baseline))

    while True:

	    if sensor.get_sensor_data():
		timestamp = int(time.time())
		lines = [
		'sensor.cpu            {0} {1}'.format(temperature_of_raspberry_pi(),    timestamp),
		'sensor.temperature    {0:.2f} {1}'.format(sensor.data.temperature,    timestamp),
		'sensor.pressure       {0:.2f} {1}'.format(sensor.data.pressure,       timestamp),
		'sensor.humidity       {0:.2f} {1}'.format(sensor.data.humidity,       timestamp)
		]
		if sensor.data.heat_stable:
		    lines.append(
			'sensor.gas_resistance {0:.2f} {1}'.format(sensor.data.gas_resistance, timestamp)
		    )
		    gas = sensor.data.gas_resistance
		    gas_offset = gas_baseline - gas
		    hum = sensor.data.humidity
		    hum_offset = hum - hum_baseline
		    # Calculate hum_score as the distance from the hum_baseline.
		    if hum_offset > 0:
			hum_score = (100 - hum_baseline - hum_offset)
			hum_score /= (100 - hum_baseline)
			hum_score *= (hum_weighting * 100)

		    else:
			hum_score = (hum_baseline + hum_offset)
			hum_score /= hum_baseline
			hum_score *= (hum_weighting * 100)

		    # Calculate gas_score as the distance from the gas_baseline.
		    if gas_offset > 0:
			gas_score = (gas / gas_baseline)
			gas_score *= (100 - (hum_weighting * 100))

		    else:
			gas_score = 100 - (hum_weighting * 100)

		    # Calculate air_quality_score.
		    air_quality_score = hum_score + gas_score

		    lines.append(
			'sensor.air_quality_score {0:.2f} {1}'.format(air_quality_score, timestamp)
		    )

		message = '\n'.join(lines) + '\n'

		if DEBUG == True:
		    print(message)

		send_msg(message)

		time.sleep(1)

except KeyboardInterrupt:
    pass

sock.close()
