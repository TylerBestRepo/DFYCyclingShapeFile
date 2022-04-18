import csv
import os

import osgeo
import osgeo.ogr as ogr
import osgeo.osr as osr
from datetime import datetime, timedelta
import time
import sys
import json


def temperature_extraction_empatica(temperature_path):
    temperature_data = []
    skip_first = True
    counter = 0
    with open(temperature_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if (counter > 2):
                temperature_data.append(float(row[0]))
            counter = counter + 1
    return temperature_data

def eda_extraction_empatica(eda_file):
        eda_data = []
        skip_first = True
        with open(eda_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            counter = 0
            for row in csv_reader:
                if (counter == 0):
                    empatica_start_time = row[0]
                    empatica_start_time = float(empatica_start_time)
                    timestamp = datetime.fromtimestamp(empatica_start_time)
                    converted_time = timestamp.strftime('%H:%M:%S')
                    print(f"Converted start time = {converted_time}")
                    #greater than 1 because first data point is the time and second is the sampling rate then a 0 measurement
                if (counter > 2):
                    eda_data.append(row[0])
                    #skip_first = False

                if counter == 1:
                    dividing_number_empatica = row[0]

                counter = counter + 1
        return eda_data, empatica_start_time, float(dividing_number_empatica)

temp_path = '/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/TEMP.csv'
eda_path = '/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/EDA.csv'



temp_data = temperature_extraction_empatica(temp_path)
eda_data, empatica_start_time,dividing_number = eda_extraction_empatica(eda_path)

def empatica_data_averager(temp_data,eda_data):
    counter = 0
    averager_temp = 0
    averager_eda = 0
    mini_counter = 0
    new_temp_data = []
    new_eda_data = []
    while (counter < len(temp_data)):
        averager_temp = float(temp_data[counter]) + averager_temp
        averager_eda = float(eda_data[counter]) + averager_eda
        mini_counter = mini_counter + 1
        if (mini_counter == dividing_number):
            averager_temp = averager_temp/dividing_number
            averager_eda = averager_eda/dividing_number
            new_temp_data.append(averager_temp)
            new_eda_data.append(averager_eda)
            averager_temp = 0
            averager_eda = 0
            mini_counter = 0
        elif(counter == len(temp_data)-1):
            averager_temp = averager_temp / mini_counter
            averager_eda = averager_eda / mini_counter
            new_temp_data.append(averager_temp)
            new_eda_data.append(averager_eda)
        counter = counter + 1



    return new_temp_data, new_eda_data

def time_list_for_empatica(empatica_starting_time_string, eda):
        second = 1
        plus_time = timedelta(seconds=second)
        empatica_time_list = []
        time_temp = datetime.fromtimestamp(empatica_starting_time_string)
        start_time_from_string = str(time_temp.strftime('%H:%M:%S'))

        date_time_starting = datetime.strptime(start_time_from_string, '%H:%M:%S')
        new_time = date_time_starting
        empatica_time_list.append(start_time_from_string)
        skip_first = False
        for y in eda:
            if skip_first:
                new_time = (new_time + plus_time)
                converted_new_time = new_time.strftime('%H:%M:%S')
                empatica_time_list.append(converted_new_time)
            skip_first = True

        return empatica_time_list

temp_data_new, eda_data_new = empatica_data_averager(temp_data,eda_data)

time_list = time_list_for_empatica(empatica_start_time, temp_data_new)

print(f"debug placeholder")
i = 0
data_writer = open(r'/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/ + ' + 'tempNewVsunaveraged' + '.csv', 'w',newline='')
writer = csv.writer(data_writer)
writer.writerow(time_list)
writer.writerow(temp_data_new)
writer.writerow(temp_data)



