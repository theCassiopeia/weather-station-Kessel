#!/usr/bin/python3
# import os, fcntl
import sys
import gspread
# import datetime
# import sqlite3
import database
import time

debug = False

# Google spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'Weather Station theCassiopeia'
# sqlite database name

# credentials_file = os.path.join(os.path.dirname(__file__), "credentials.oracle")
# if os.path.isfile(credentials_file):
#     lock_file = "/var/lock/oracle.lock"
#     f = open(lock_file, 'w')
#     try:
#         fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
#         print("No other uploads in progress, proceeding...")
#         import database # requires MySQLdb python 2 library which is not ported to python 3 yet
#         db = database.weather_database()
#         db.upload()
#     except IOError:
#         print("Another upload is running exiting now")
#     finally:
#         f.close()
# else:
#     print("Credentials file not found")

temp_DS18B20 = 0.0
temp_BMP180 = 0.0
pressure_BMP180 = 0.0
uv_index = 0.0
ambient_light = 0
IR_light = 0

db = database.WeatherDatabase()


def login_open_sheet(spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        gc = gspread.oauth()
        ws = gc.open(spreadsheet).sheet1
        return ws
    except:
        print('Unable to login and get spreadsheet.  Check spreadsheet name.')
        sys.exit(1)


# TODO Get all rows from Sqlite/weather.db which have not been uploaded yet
def getrows():

    """
    conn = None
    try:
        conn = sqlite3.connect(sqlite_weather)
    except ConnectionError as e:
        print(e)

    cur = conn.cursor()
    cur.execute("SELECT * FROM WEATHER_MEASUREMENT WHERE GOOGLE_UPLOADED = 0")

    rows = cur.fetchall()
    """
    rows = db.upload_google()

    if debug:
        for row in rows:
            print(row)

    return rows


# TODO make a config file identifying which uploads need to happen (Google, Wunderground, ...)

rowstoBeUploaded = getrows()

print("Number of items to be uploaded : %d" % len(rowstoBeUploaded))

if rowstoBeUploaded != None :
    ws = None
    # Login if necessary.
    if ws is None:
        ws = login_open_sheet(GDOCS_SPREADSHEET_NAME)
    
    print("Inserting into Google Spreadsheet...", ws)
#    ws.append_rows(rowstoBeUploaded)

    for rows in rowstoBeUploaded:
        # print("Row to be uploaded : ", rows)
        # print("Values", rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8], rows[9],
        #      rows[10], rows[11], rows[12], rows[13], rows[14], rows[15])
        # ws.append_row((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8], rows[9],
        #             rows[10], rows[11], rows[12], rows[13], rows[14], rows[15]))
        try:
            ws.append_row(rows, table_range='A1')
            # table_range parameter to be added - otherwise the new row starts at the last column of the previous row
            db.update_google(int(rows[0]))
            print('Wrote row {} to {}'.format(int(rows[0]), GDOCS_SPREADSHEET_NAME))
            time.sleep(1)
        except:
            print('Problem appending row or updating database')

