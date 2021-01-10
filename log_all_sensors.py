#!/usr/bin/python3
# import interrupt_client
# import MCP342X
# import wind_direction
# import HTU21D
# import bmp085
# import tgs2600
import ds18b20_therm
import database 

# pressure = bmp085.BMP085()
temp_probe = ds18b20_therm.DS18B20()
# air_qual = tgs2600.TGS2600(adc_channel = 0)
# humidity = HTU21D.HTU21D()
# wind_dir = wind_direction.wind_direction(adc_channel = 0, config_file="wind_direction.json")
# interrupts = interrupt_client.interrupt_client(port = 49501)

db = database.WeatherDatabase()  # Local SQLite db

# wind_average = wind_dir.get_value(10)  # ten seconds

print("Inserting...")
# Need to use None instead of "null"
db.insert(temp_probe.read_temp(), None, None, None, None, None, None, None, None, None)
# db.insert(humidity.read_temperature(), temp_probe.read_temp(), air_qual.get_value(), pressure.get_pressure(),
# humidity.read_humidity(), wind_average, interrupts.get_wind(), interrupts.get_wind_gust(), interrupts.get_rain())
print("done")

# interrupts.reset()
