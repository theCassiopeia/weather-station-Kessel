#!/usr/bin/python3

# import interrupt_client
# import MCP342X
# import wind_direction
# import HTU21D
import smbus
import bmp085
# import tgs2600
import ds18b20_therm
import si1145
from scd30_i2c import SCD30  # to be installed : sudo pip3 install scd30-i2c
import database
import time

debug = True

I2C_address_SI1145 = 0x60
I2C_address_BMP180 = 0x77
I2C_address_SCD30 = 0x61

uv_sensor = None
temp_probe = None
BMP180 = None
scd30 = None

# initialize all sensor-output parameters to None
temp_DS18B20 = None
temp_BMP180 = None
pressure_BMP180 = None
uv_index = None
ambient_light = None
IR_light = None
scd30_co2 = None
scd30_temp = None
scd30_rh = None

EN_DS18B20 = True
EN_BMP180 = True
EN_SI1145 = True
EN_SCD30 = True

data_retrieval = True

bus = smbus.SMBus(1)      # 1 indicates /dev/i2c-1

if debug:
    for device in range(128):
        try:
            bus.read_byte(device)
            print(hex(device))
        except Exception:  # exception if read_byte fails
            pass


try:
    bus.read_byte(I2C_address_BMP180)
except Exception:
    EN_BMP180 = False
try:
    bus.read_byte(I2C_address_SI1145)
except Exception:
    EN_SI1145 = False
try:
    bus.read_byte(I2C_address_SCD30)
except Exception:
    EN_SCD30 = False
try:
    temp_probe = ds18b20_therm.DS18B20()
except Exception:
    EN_DS18B20 = False

if debug:
    print("BMP180 : ", EN_BMP180, "\nSI1145 : ", EN_SI1145, "\nSCD30 : ", EN_SCD30, "\nDB18b20 : ", EN_DS18B20, "\n")
# TODO : test if sensor connected before handling it
if EN_SCD30:
    scd30 = SCD30()
    scd30.set_measurement_interval(5)
    scd30.start_periodic_measurement()
if EN_BMP180:
    BMP180 = bmp085.BMP085()
if EN_DS18B20:
    temp_probe = ds18b20_therm.DS18B20()
if EN_SI1145:
    uv_sensor = si1145.SI1145()

# Append the data in the sqlite-database, including a timestamp
try:
    if EN_SI1145:
        uv_index = float(uv_sensor.readUVIndex()) / 100
        ambient_light = uv_sensor.readAmbientLight()
        IR_light = uv_sensor.readIRLight()
    if EN_DS18B20:
        temp_DS18B20 = temp_probe.read_temp()
    if EN_BMP180:
        temp_BMP180 = BMP180.get_temperature()
        pressure_BMP180 = BMP180.get_pressure()
    if EN_SCD30:
        t = 0
        gdr = scd30.get_data_ready()
        if debug:
            print("Get Data Ready flag : ", gdr)
        while (not gdr) and (t < 5):
            time.sleep(2)
            t += 1
            gdr = scd30.get_data_ready()
            if debug:
                print("Get Data Ready flag : ", gdr)
                print("Trials : ", t, "\n")
        if gdr:
            m = scd30.read_measurement()
            scd30_co2 = round(m[0], 2)
            scd30_temp = round(m[1], 2)
            scd30_rh = round(m[2], 2)
        else:
            print("Data not ready")

    if debug:
        print("CO2 Air quality          : %.2f\n"
              "Temperature from SCD30   : %.2f C\n"
              "Humidity from SCD30      : %.2f " % (
                  scd30_co2, scd30_temp, scd30_rh))
        print("Temperature from DS18B20 : %.2f C", temp_DS18B20)
        print("Temperature from  BMP180 : %.2f C", temp_BMP180)
        print("Pressure from     BMP180 : %d hPa", pressure_BMP180)
        print("UV Index                 : %.2f", uv_index)
        print("Visible Light            : %d lux", ambient_light)
        print("IR Light                 : %d lux", IR_light)

    # air_quality = tgs2600.TGS2600(adc_channel = 0)
    # humidity = HTU21D.HTU21D()
    # wind_dir = wind_direction.wind_direction(adc_channel = 0, config_file="wind_direction.json")
    # interrupts = interrupt_client.interrupt_client(port = 49501)

except Exception:
    # Error appending data, most likely because credentials are stale.
    # Null out the worksheet so a login is performed at the top of the loop.
    print('Data retrieval error')
    data_retrieval = False

if data_retrieval:
    try:
        db = database.WeatherDatabase()  # Local SQLite db

    # wind_average = wind_dir.get_value(10)  # ten seconds

    # TODO : add table (?) or at least columns to capture gyroscope sensors & magneto / accelerometer data

        print("Inserting into SQLite database...")
    # Need to use None instead of "null"
        db.insert(temp_DS18B20, temp_BMP180, scd30_co2, pressure_BMP180, scd30_rh, scd30_temp, None, None, None,
                  uv_index, ambient_light, IR_light, None)
    # db.insert(humidity.read_temperature(), temp_probe.read_temp(), air_quality.get_value(), pressure.get_pressure(),
    # humidity.read_humidity(), wind_average, interrupts.get_wind(), interrupts.get_wind_gust(),
    # interrupts.get_rain())
        print("done")

    # interrupts.reset()

    except Exception:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print('Append error')
