import csv
import os

import osgeo
import osgeo.ogr as ogr
import osgeo.osr as osr
from datetime import datetime, timedelta
import time
import sys
import json
import string
from dataclasses import dataclass, field


@dataclass
class gps:
    gps_path: str
    gps_times: list[str] = field(default_factory=list)

    def gps_time_retrieval(self) -> None:
        # gps_times = []
        with open(self.gps_path) as bike_gps:
            gps_reader = csv.reader(bike_gps, delimiter=',')
            first_time_index_bool = True
            counter = 0
            for row in gps_reader:
                # if i[2] == 'record' and i[0] == 'Data' and len(i) > 20:
                if row[2] == 'record' and row[0] == 'Data' and len(row) > 20 and row[10] != '' and row[21] and row[
                    27] == "temperature" and row[26] == "m/s":
                    if first_time_index_bool:
                        first_time_index = counter
                        first_time_index_bool = False
                    time_temp = float(row[4])  # -55
                    time_temp = datetime.fromtimestamp(time_temp)
                    time_temp = str(time_temp.strftime('%H:%M:%S'))
                    self.gps_times.append(time_temp)
                counter = counter + 1
        self.first_time_index = first_time_index
        # return gps_times, first_time_index

    def matching_indexes(self, comparing_times_list) -> tuple[int, int]:
        other_index_match = None
        gps_index_match = None
        match_found = False
        for gps_time, y in enumerate(self.gps_times):
            for other_index, z in enumerate(comparing_times_list):
                if y == z:
                    gps_index_match = gps_time
                    other_index_match = other_index
                    match_found = True
                    break
            if match_found:
                break
        return gps_index_match, other_index_match


path = r"E:\UNI\Research_assistant\My test data\May 5th\2022-05-05-075456-ELEMNT BOLT 28D4-6-0.csv"


def main() -> None:
    GPS = gps(gps_path=path)
    GPS.gps_time_retrieval()
    gps_times = GPS.gps_times
    print(f"The first time is: {gps_times[0]}")


main()
