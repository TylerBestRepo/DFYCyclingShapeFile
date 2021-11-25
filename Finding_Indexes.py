import csv
import osgeo.ogr as ogr
import osgeo.osr as osr

# Save and close the data source

with open(r"E:\UNI\Research_assistant\WAHOO files\Oct-31.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    y = 0
    for row in csv_reader:
        for idx, x in enumerate(row):
            if x == 'speed':
                speed_index = idx + 1
            if x == 'cadence':
                cadence_index = idx + 1
            if x == 'distance':
                distance_index = idx + 1
            if x == 'altitude':
                altitude_index = idx + 1
            if x == 'timestamp':
                time_index = idx+1

    y = y+1
    print(f"Time index: {time_index}\nSpeed index: {speed_index}\nCadence index: {cadence_index}\nDistance index: {distance_index}\nAltitude index: {altitude_index}\n")
