#!/usr/bin/python3
import sys
import time
import datetime
import gspread

# import interrupt_client
# import MCP342X
# import wind_direction
# import HTU21D
import bmp085
# import tgs2600
import ds18b20_therm
import si1145
import database

debug = False

BMP180 = bmp085.BMP085()
temp_probe = ds18b20_therm.DS18B20()
uv_sensor = si1145.SI1145()



# Google Docs account email, password, and spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'Weather Station theCassiopeia'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 30


def login_open_sheet(spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        gc = gspread.oauth()
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except:
        print('Unable to login and get spreadsheet.  Check email, password, spreadsheet name.')
        sys.exit(1)


print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
worksheet = None
while True:
    # Login if necessary.
    if worksheet is None:
        worksheet = login_open_sheet(GDOCS_SPREADSHEET_NAME)

    # Append the data in the spreadsheet, including a timestamp
    try:
        uv_index = float(uv_sensor.readUVIndex()) / 100
        ambient_light = uv_sensor.readAmbientLight()
        IR_light = uv_sensor.readIRLight()
        temp_DS18B20 = temp_probe.read_temp()
        temp_BMP180 = BMP180.get_temperature()
        pressure_BMP180 = BMP180.get_pressure()
        if debug:
            print("Temperature from DS18B20 : %.2f C\n"
                  "Temperature from  BMP180 : %.2f C\n"
                  "Pressure from     BMP180 : %d hPa\n"
                  "UV Index                 : %.2f\n"
                  "Visible Light            : %d lux\n"
                  "IR Light                 : %d lux" % (
                      temp_DS18B20, temp_BMP180, pressure_BMP180, uv_index, ambient_light, IR_light))

        # air_qual = tgs2600.TGS2600(adc_channel = 0)
        # humidity = HTU21D.HTU21D()
        # wind_dir = wind_direction.wind_direction(adc_channel = 0, config_file="wind_direction.json")
        # interrupts = interrupt_client.interrupt_client(port = 49501)

        db = database.WeatherDatabase()  # Local SQLite db

        # wind_average = wind_dir.get_value(10)  # ten seconds

        # TODO : first lecture from temp_probe gives a strange value (85) instead something like 18-23 degrees C.
        #  It either should be checked when read or a initial reading needs to be

        # TODO : add column to capture UV measurement

        # TODO : add table (?) or at least columns to capture gyroscope sensors & magneto / accelerometer data

        print("Inserting into SQLite database...")
        # Need to use None instead of "null"
        db.insert(temp_DS18B20, temp_BMP180, None, pressure_BMP180, None, None, None, None, None, None)
        # db.insert(humidity.read_temperature(), temp_probe.read_temp(), air_qual.get_value(), pressure.get_pressure(),
        # humidity.read_humidity(), wind_average, interrupts.get_wind(), interrupts.get_wind_gust(),
        # interrupts.get_rain())
        print("done")

        # interrupts.reset()
        print("Inserting into Google Spreadsheet...")
        worksheet.append_row((str(datetime.datetime.now()), temp_DS18B20, temp_BMP180, pressure_BMP180, uv_index,
                              ambient_light, IR_light))
        print("done")
    except:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print('Append error, logging in again')
        worksheet = None
        time.sleep(FREQUENCY_SECONDS)
        continue

    # Wait 30 seconds before continuing
    print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
    time.sleep(FREQUENCY_SECONDS)
