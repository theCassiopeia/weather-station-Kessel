#!/usr/bin/python3
# import os
import glob
import time

# add the lines below to /etc/modules (reboot to take effect)
# w1-gpio
# w1-therm


class DS18B20(object):
    def __init__(self):        
        self.device_file = glob.glob("/sys/bus/w1/devices/28*")[0] + "/w1_slave"
        
    def read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        f.close()
        return lines
        
    def crc_check(self, lines):
        return lines[0].strip()[-3:] == "YES"
        
    def read_temp(self):
        temp_c = -255
        attempts = 0
        
        lines = self.read_temp_raw()
        success = self.crc_check(lines)
        
        while not success and attempts < 3:
            time.sleep(.2)
            lines = self.read_temp_raw()            
            success = self.crc_check(lines)
            attempts += 1
        
        if success:
            temp_line = lines[1]
            equal_pos = temp_line.find("t=")            
            if equal_pos != -1:
                temp_string = temp_line[equal_pos+2:]
                temp_c = float(temp_string)/1000.0
                if temp_c > 1000:  # could be max 125 degrees Celsius
                    temp_c -= 4096
                    temp_c = temp_c.__format__(".3f")  # otherwise it provides a lot of digits
                if temp_c == 85:
                    # 85 = power-on reset value
                    temp_c = None
        
        return temp_c


if __name__ == "__main__":
    obj = DS18B20()
    print("Temp: %s C" % obj.read_temp())
