import csv
from datetime import datetime, timedelta
import time

# Best to turn both of these csv reading code blocks into functions
HRV_path = r"E:\UNI\Research_assistant\Device test data\9th march\eSense Pulse data from 09.03.22 16_58_12.csv"


# Format for this CSV is:
#   time elapsed; heart rate measurement; RR interval (dunno what this is); RR interval in ms; HRV amplitude; regularity; timestamp; marker;
# I dont know which data bits we want but ill have some commented stuff in it that can be changed easily

def get_hrv_data(hrv_path):
    hrv_data = []
    just_hear_rate = []
    time_elapsed_only = []
    with open(HRV_path) as hrv:
        hrv_reader = csv.reader(hrv, delimiter=";")
        for row in hrv_reader:

            # print(f"Length = {len(row)}")
            if not row[0].isalnum():
                # print(f"Cool beans man this is the output row: {row}")
                if not row[0] == '':
                    # print(f"is this the row thats gonna fuck it? {row}")
                    row_test = row[0][0]
                    if not row_test.isalpha():
                        time_elapsed = float(row[0])
                        heart_rate = float(row[1])
                        rr_interval = float(row[2])
                        hrv_amplitude = float(row[3])
                        regularity = float(row[4])
                        timestamp = row[5]
                        hours = int(timestamp[0:2])
                        minutes = int(timestamp[3:5])
                        seconds = int(timestamp[6:8])
                        annoying = [2021, 1, 5]
                        timestamp = datetime(annoying[0], annoying[1], annoying[2], hours, minutes, seconds).strftime(
                            '%H:%M:%S')
                        combined = [time_elapsed, heart_rate, rr_interval, hrv_amplitude, regularity, timestamp]
                        hrv_data.append(combined)
                        just_hear_rate.append(heart_rate)
                        time_elapsed_only.append(time_elapsed)
                        # print(f"Heart Rate: {heart_rate}\tHRV amplitude: {hrv_amplitude}\tTime of measurement: {timestamp}\n")
                        print(f"Heart rate: {heart_rate}")

    return hrv_data, just_hear_rate, time_elapsed_only


hrv_data, just_heart_rate, time_elapsed_only = get_hrv_data(HRV_path)
# print(f"all the data saved that we want: {hrv_data[3][1]}")


data_writer = open(r'E:\UNI\Research_assistant\Device test data\9th march\just_heart_rate.csv', 'w', newline='')
writer = csv.writer(data_writer)
writer.writerow(map(lambda x: x, just_heart_rate))
data_writer.close()

data_writer = open(r'E:\UNI\Research_assistant\Device test data\9th march\just_time_data.csv', 'w', newline='')
writer = csv.writer(data_writer)
writer.writerow(map(lambda x: x, time_elapsed_only))
data_writer.close()