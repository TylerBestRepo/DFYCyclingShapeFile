import csv
import osgeo.ogr as ogr
import osgeo.osr as osr
from datetime import datetime, timedelta
import time
import sys
import json

time = 1013375244



timestamp = datetime.fromtimestamp(time)
time_variable = timestamp.strftime('%H:%M:%S')

print(f"Time variable conversion = {timestamp}")