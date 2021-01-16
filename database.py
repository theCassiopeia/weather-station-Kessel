#!/usr/bin/python3
import sqlite3
# import datetime
# import http.client
# TODO: figure out http.client - it gives an error on target
import json
import os
import io
import gzip

debug = False

def gunzip_bytes(bytes_obj):
    in_ = io.BytesIO()
    in_.write(bytes_obj)
    in_.seek(0)
    with gzip.GzipFile(fileobj=in_, mode='rb') as fo:
        gunzipped_bytes_obj = fo.read()

    return gunzipped_bytes_obj.decode()


#
# Originally, this was a MySQL (MariaDB) database. It required a password and username.
# In this version of the Weather Station, a SQLite database is used, without username / password.
# In case a MySQL database is going to be used in the future, revert back to the original version of this file.
# The credentials file is kept for potential future use.
#


class MysqliteDatabase:
    def __init__(self):
        credentials_file = os.path.join(os.path.dirname(__file__), "credentials.mysqlite")

        f = open(credentials_file, "r")
        credentials = json.load(f)
        f.close()
        for key, value in credentials.items():  # remove whitespace
            credentials[key] = value.strip()

        if debug:
            print(credentials["DATABASE"])
        db_file = "/home/pi/Sqlite/" + credentials["DATABASE"]
        if debug:
            print(db_file)
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def execute(self, query, params=()):
        try:
            if debug:
                print(query, params)
            self.cursor.execute(query, params)
            self.connection.commit()
        except:
            self.connection.rollback()
            raise

    def query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def __del__(self):
        self.connection.close()


"""
class oracle_apex_database:
    def __init__(self, path, host="apex.oracle.com"):
        self.host = host
        self.path = path
        # self.conn = httplib.HTTPSConnection(self.host)
        self.conn = http.client.HTTPSConnection(self.host)
        self.credentials = None
        credentials_file = os.path.join(os.path.dirname(__file__), "credentials.oracle")

        if os.path.isfile(credentials_file):
            f = open(credentials_file, "r")
            self.credentials = json.load(f)
            f.close()
            for key, value in self.credentials.items():  # remove whitespace
                self.credentials[key] = value.strip()
        else:
            print("Credentials file not found")

        self.default_data = {"Content-type": "text/plain", "Accept": "text/plain"}

    def upload(self, id, ambient_temperature, ground_temperature, air_quality, air_pressure, humidity, wind_direction,
               wind_speed, wind_gust_speed, rainfall, created):
        # keys must follow the names expected by the Orcale Apex REST service
        oracle_data = {
            "LOCAL_ID": str(id),
            "AMB_TEMP": str(ambient_temperature),
            "GND_TEMP": str(ground_temperature),
            "AIR_QUALITY": str(air_quality),
            "AIR_PRESSURE": str(air_pressure),
            "HUMIDITY": str(humidity),
            "WIND_DIRECTION": str(wind_direction),
            "WIND_SPEED": str(wind_speed),
            "WIND_GUST_SPEED": str(wind_gust_speed),
            "RAINFALL": str(rainfall),
            "READING_TIMESTAMP": str(created)}

        for key in oracle_data.keys():
            if oracle_data[key] == str(None):
                del oracle_data[key]

        return self.https_post(oracle_data)

    def https_post(self, data, attempts=3):
        attempt = 0
        headers = self.default_data.copy()
        headers.update(self.credentials)
        headers.update(data)

        # headers = dict(self.default_data.items() + self.credentials.items() + data.items())
        success = False
        response_data = None

        while not success and attempt < attempts:
            try:
                self.conn.request("POST", self.path, None, headers)
                response = self.conn.getresponse()
                response_data = response.read()
                print("Response status: %s, Response reason: %s, Response data: %s" % (
                response.status, response.reason, response_data))
                success = response.status == 200 or response.status == 201
            except Exception as e:
                print("Unexpected error", e)
            finally:
                attempt += 1

        return response_data if success else None

    def __del__(self):
        self.conn.close()
"""


class WeatherDatabase:
    def __init__(self):
        self.db = MysqliteDatabase()
        self.insert_template = "INSERT INTO WEATHER_MEASUREMENT (TEMP_DS18B20, TEMP_BMP180, " \
                               "AIR_QUALITY, AIR_PRESSURE, HUMIDITY, WIND_DIRECTION, WIND_SPEED, WIND_GUST_SPEED, " \
                               "RAINFALL, UV_INDEX, AMBIENT_LIGHT, IR_LIGHT, IMAGE_LINK) " \
                               "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        #
        # removed the CREATED filed. Is automatically filled by SQLite since field = default CURRENT_TIMESTAMP
        #
        self.update_template = "UPDATE WEATHER_MEASUREMENT SET REMOTE_ID=%s WHERE ID=?;"
        self.update_google_template = ''' UPDATE WEATHER_MEASUREMENT SET UPLOADED_GOOGLE=1 WHERE ID = ?;'''
        self.upload_select_template = "SELECT * FROM WEATHER_MEASUREMENT WHERE REMOTE_ID IS NULL;"
        self.upload_google_template = "SELECT * FROM WEATHER_MEASUREMENT WHERE UPLOADED_GOOGLE IS 0;"

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_none(self, val):
        return val if val is not None else "NULL"

    def insert(self, ambient_temperature, ground_temperature, air_quality, air_pressure, humidity, wind_direction,
               wind_speed, wind_gust_speed, rainfall, uv_index, ambient_light, ir_light, image_link):
        # created=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        params = (ambient_temperature,
                  ground_temperature,
                  air_quality,
                  air_pressure,
                  humidity,
                  wind_direction,
                  wind_speed,
                  wind_gust_speed,
                  rainfall,
                  uv_index,
                  ambient_light,
                  ir_light,
                  image_link)
        # created)
        if debug:
            print(self.insert_template, params)
        self.db.execute(self.insert_template, params)

    def upload_google(self):
        results = self.db.query(self.upload_google_template)
        return results

    def update_google(self, id_row):
        params = (id_row,)
        self.db.execute(self.update_google_template, params)
        return

    """
    def upload(self):
        results = self.db.query(self.upload_select_template)

        rows_count = len(results)
        if rows_count > 0:
            print("%d rows to send..." % rows_count)
            odb = oracle_apex_database(path="/pls/apex/raspberrypi/weatherstation/submitmeasurement")

            if odb.credentials == None:
                return  # cannot upload

            for row in results:
                response_data = odb.upload(
                    row["ID"],
                    row["AMBIENT_TEMPERATURE"],
                    row["GROUND_TEMPERATURE"],
                    row["AIR_QUALITY"],
                    row["AIR_PRESSURE"],
                    row["HUMIDITY"],
                    row["WIND_DIRECTION"],
                    row["WIND_SPEED"],
                    row["WIND_GUST_SPEED"],
                    row["RAINFALL"],
                    row["CREATED"].strftime("%Y-%m-%dT%H:%M:%S"))

                if response_data != None and response_data != "-1":
                    json_dict = json.loads(gunzip_bytes(response_data))  # 2019 post-apex upgrade change
                    # json_dict = json.loads(response_data.decode()) # Python3 change
                    oracle_id = json_dict["ORCL_RECORD_ID"]
                    if self.is_number(oracle_id):
                        local_id = str(row["ID"])
                        self.db.execute(self.update_template, (oracle_id, local_id))
                        print("ID: %s updated with REMOTE_ID = %s" % (local_id, oracle_id))
                else:
                    print("Bad response from Oracle")
        else:
            print("Nothing to upload")
"""
