import csv
from datetime import datetime, timedelta
import time
import sys


def start_time_from_path(file_name):
    day = int(file_name[12:14])
    month = int(file_name[10:12])
    year = int(file_name[6:10])
    hours = int(file_name[15:17])
    minutes = int(file_name[17:19])
    seconds = int(file_name[19:21])
    combined = datetime(year, month, day, hours, minutes, seconds)
    return combined


def time_delta_conversion_for_subtraction(time_string):
    subtract_time = timedelta(hours=float(time_string[0:2]),
                              minutes=float(time_string[3:5]),
                              seconds=float(time_string[6:8]))
    return subtract_time


path = "audio-20211203-153515.csv"

start_time = []
end_time = []
sentences = []
confidence = []

with open(path) as audio:
    emotions_reader = csv.reader(audio, delimiter=",")
    for row in emotions_reader:
        start_time.append(float(row[0]))
        end_time.append(float(row[1]))
        sentences.append(row[2])
        if len(row) > 3:
            confidence.append(float(row[3]))
# Calling function to retrieve the time data from the file name
audio_start = start_time_from_path(path)
# Creating lists for the times
adjusted_start_times = []
adjusted_end_times = []
length = len(start_time)
i = 0
while i < length:
    plus_start = timedelta(seconds = start_time[i])
    plus_end = timedelta(seconds= end_time[i])
    adjusted_start_times.append((audio_start + plus_start).strftime('%H:%M:%S'))
    adjusted_end_times.append((audio_start + plus_end).strftime('%H:%M:%S'))
    i = i + 1
# these are now in the format that i want them in
# String to time variable conversion so maths can be performed
time_test_1 = time_delta_conversion_for_subtraction(adjusted_start_times[0])
time_test_2 = datetime.strptime(adjusted_end_times[0], '%H:%M:%S')
print(f"Subtraction test 1: {(time_test_2 - time_test_1).strftime('%H:%M:%S')}")