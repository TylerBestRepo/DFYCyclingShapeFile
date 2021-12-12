import csv
import osgeo.ogr as ogr
import osgeo.osr as osr
from datetime import datetime, timedelta
import time
import sys

driver = ogr.GetDriverByName("ESRI Shapefile")
data_source = driver.CreateDataSource(r"E:\UNI\Research_assistant\Shape files\Ride 3\Ride_3.shp")
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

# create the layer
layer = data_source.CreateLayer("Ride_3", srs, ogr.wkbPoint)

# Add the fields we're interested in
field_name = ogr.FieldDefn("Speed", ogr.OFTReal)
field_name.SetWidth(24)
layer.CreateField(field_name)
layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Distance", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Cadence", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Altitude", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Time", ogr.OFTReal))

# Incorporating functions and data from additional sources


# Index matching for video and GPS
def time_index_matching_function(gps_times,video_times):
    counter = 0
    for y in gps_times:
        counter_2 = 0
        for z in video_times:
            if y == z:
                print("we have a match")
                gps_index = counter
                video_index = counter_2
            counter_2 = counter_2 + 1
        counter = counter + 1
        #Need a failsafe incase the data sets dont match up whatsoever
    return gps_index, video_index


# For dominant emotions
def store_dominant_emotions(file_path):
    with open(file_path) as emotions:
        emotions_reader = csv.reader(emotions, delimiter=",")
        counter = 0
        for x in emotions_reader:
            if counter == 0:
                emotions_list = x
                counter = counter + 1
            else:
                emotions_time = x
    return emotions_list, emotions_time


# For time subtraction
def time_delta_conversion_for_subtraction(time_string):
    subtract_time = timedelta(hours=float(time_string[0:2]),
                              minutes=float(time_string[3:5]),
                              seconds=float(time_string[6:8]))
    return subtract_time


# Go through GPS csv just to get times
def gps_time_retrieval(gps_path):
    gps_times = []
    with open(gps_path) as bike_gps:
        gps_reader = csv.reader(bike_gps, delimiter=',')
        for i in gps_reader:
            if i[2] == 'record' and i[0] == 'Data' and len(i) > 20:
                time_temp = float(i[4])
                time_temp = datetime.fromtimestamp(time_temp)
                time_temp = str(time_temp.strftime('%H:%M:%S'))
                gps_times.append(time_temp)
    return gps_times


gps = 'video timing test (29-11-2021).csv'
emotions = 'face_video_frames_dominant_emotions.txt'
# get times for GPS first
gps_times = gps_time_retrieval(gps)
# Get dominant emotions and their times
emotions_list, emotions_time = store_dominant_emotions(emotions)
# Get time indexes for when these two data sets match up
gps_index, time_index = time_index_matching_function(gps_times,emotions_time)

# probably going to need some sort of i = 0 counter for tracking loops and times
i = 0
with open(gps) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        if row[2] == 'record' and row[0] == 'Data' and len(row) > 20:
            #indexes found manually or by using Finding_indexes.py
            position_lat_semi_circles = row[7]
            position_long_semi_circles = row[10]
            speed = row[28]
            #cadence = row[25]
            distance = row[22]
            altitude = row[16]
            time = row[4]

            if len(position_lat_semi_circles) > 1:  # This is needed because the first measurement i pulled contained no values so I'm essentially doing all this to ignore the first reading or any null readings
                position_lat_degrees = float(position_lat_semi_circles) * (180 / 2**31)
                position_long_degrees = float(position_long_semi_circles) * (180 / 2 ** 31)
                # Prints give visual feedback to know everything is being retrieved as we desire
                print(f"position_lat_degrees: {position_lat_degrees}")
                print(f"position_long_degrees: {position_long_degrees}\n")
                print(f"Speed: {speed}\n")
                # We want to convert speed from a string to a number value
                if len(speed) < 1: # Some data points fall under the same two categories for pulling data but only output location data with no other parameters so the speed is manually set to 0
                    speed = "0"
                speed = float(speed)
                time = float(time)
                timestamp = datetime.fromtimestamp(time) # This can output up to date time and year but for this we probably only need hours minutes seconds
                # print(timestamp.strftime('%M:%S')) #This timestamp comes out as a string, before this conversion it is some sort of time object
                time_variable = timestamp.strftime('%H:%M:%S')

                print(f"The file types is: {type(time_variable)}\n")


                # create the feature
                feature = ogr.Feature(layer.GetLayerDefn())
                # Set the attributes using the values from the delimited text file
                feature.SetField("Speed", speed)
                feature.SetField("Latitude", position_lat_degrees)
                feature.SetField("Longitude", position_long_degrees)
                # feature.SetField("Cadence", cadence) # Cadence measurements probably wont be used as the measurement devices are too annoying to attach to the users bike
                feature.SetField("Distance", distance)
                feature.SetField("Altitude", altitude)
                feature.SetField("Time", time_variable)

                # create the WKT for the feature using Python string formatting
                wkt = f"POINT({position_long_degrees} {position_lat_degrees})"
                #print("wkt: {}".format(wkt))

                # Create the point from the Well Known Txt
                point = ogr.CreateGeometryFromWkt(wkt)
                feature.SetGeometry(point)
                layer.CreateFeature(feature)

                feature = None
            i = i + 1
    data_source = None