import csv
import os

import osgeo
import osgeo.ogr as ogr
import osgeo.osr as osr
from datetime import datetime, timedelta
import time
import sys
import json

# examples of inputfile
# inputFile= {
#     'sessionID' : '12',
#     'gps' : 'Nov-7-wSpeedCadence.csv',
#     'emotions' : 'face_video_frames_dominant_emotions.txt',
#     'audio_sentences' : "audio-20211203-153515.csv",
#     'audio_words' : 'audio-202111203-individual-words.csv',
#     'dictionary_path' : 'Dictionary.txt' # This path will be a constant
#     'hrv_path' : 'eSense Pulse data from 09.02.22 13_22_59.csv'
#     'empatica_EDA' : 'location'
#     'empatica_TEMP' : 'location'
# }
# My mac directories
inputFile = {
    'sessionID': 'Tommy 27th with subtract',  #
    'gps': r"E:\UNI\Research_assistant\My test data\Tommy 27th\April-27.csv",  #

  #  'emotions': r"E:\UNI\Research_assistant\My test data\Tommy 27th\emotion_data.txt",
    #

    'audio_sentences': r"E:\UNI\Research_assistant\My test data\Tommy 27th\audio-20220427-073816.csv",
    'audio_words': r"E:\UNI\Research_assistant\My test data\Tommy 27th\2704 individual words.csv",

    #'dictionary_path': r'Dictionary.txt',  # This path will be a constant #
    #'HRV_path': r'/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/eSense Pulse data from 14.04.22 17_59_22.csv',
    #'empatica_EDA': '/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/EDA.csv',
    # Have I written these two empatica things in to be written?
   # 'empatica_TEMP': '/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/TEMP.csv'
    # check code and debug/read through to determine

#}

#inputFile = {
   # 'sessionID': 'Tyler quick ride on the 24th of April',  #
   # 'gps': r"E:\UNI\Research_assistant\My test data\April 26th\GPS 24th April.csv",  #

#    'emotions': r"E:\UNI\Research_assistant\My test data\April 26th\emotion_data.txt",
    #

   # 'audio_sentences': r"E:\UNI\Research_assistant\My test data\April 26th\audio-20220426-174551.csv",
   # 'audio_words': r"E:\UNI\Research_assistant\My test data\April 26th\2604 Individual words.csv",

#    'dictionary_path': r'Dictionary.txt',  # This path will be a constant #
#    'HRV_path': r"E:\UNI\Research_assistant\My test data\April 26th\eSense Pulse data from 26.04.22 17_45_15.csv",
#    'empatica_EDA': r"E:\UNI\Research_assistant\My test data\April 26th\EDA.csv",
    # Have I written these two empatica things in to be written?
#    'empatica_TEMP': r"E:\UNI\Research_assistant\My test data\April 26th\TEMP.csv"
    # check code and debug/read through to determine

}


# Getting the time variable data from the file name (audio sentence transcription)
def audio_start_time_from_path(file_name_path):
    file_name = os.path.basename(file_name_path)
    day = int(file_name[12:14])
    month = int(file_name[10:12])
    year = int(file_name[6:10])
    hours = int(file_name[15:17])
    minutes = int(file_name[17:19])
    seconds = int(file_name[19:21])
    combined = datetime(year, month, day, hours, minutes, seconds)
    return combined


# Go through GPS csv just to get times
def gps_time_retrieval(gps_path):
    gps_times = []
    with open(gps_path) as bike_gps:
        gps_reader = csv.reader(bike_gps, delimiter=',')
        first_time_index_bool = True
        counter = 0
        for row in gps_reader:
            # if i[2] == 'record' and i[0] == 'Data' and len(i) > 20:
            if row[2] == 'record' and row[0] == 'Data' and len(row) > 20 and row[10] != '' and row[21] and row[
                27] == "temperature" and row[26] == "m/s":
                if first_time_index_bool == True:
                    first_time_index = counter
                    first_time_index_bool = False
                time_temp = float(row[4]) -55
                time_temp = datetime.fromtimestamp(time_temp)
                time_temp = str(time_temp.strftime('%H:%M:%S'))
                gps_times.append(time_temp)
            counter = counter + 1
    return gps_times, first_time_index


def saving_sentence_data(audio_path):
    start_time = []
    end_time = []
    sentence = []
    confidence = []
    with open(audio_path) as audio:
        emotions_reader = csv.reader(audio, delimiter=",")
        for row in emotions_reader:
            start_time.append(float(row[0]))
            end_time.append(float(row[1]))
            sentence.append(row[2])
            if len(row) > 3:
                confidence.append(float(row[3]))
    return start_time, end_time, confidence, sentence


def sentences_proper_time_value(start_or_end, audio_start):
    sentence_time_fixed = []
    for x in start_or_end:
        word_time = float(x)
        word_time = round(word_time)
        plus_start = timedelta(seconds=word_time)
        word_time = (audio_start + plus_start).strftime('%H:%M:%S')
        sentence_time_fixed.append(word_time)
    return sentence_time_fixed


def matching_indexes(gps_times, other_times):
    match_found = False
    for gps_time, y in enumerate(gps_times):
        for other_index, z in enumerate(other_times):
            if y == z:
                gps_index_match = gps_time
                other_index_match = other_index
                match_found = True
                break
        if match_found:
            break
    return gps_index_match, other_index_match


def analysis(inputFile, outputFile):
    # input File (dict):
    # must include sessionID (str), transcript file location (str), video emotion file location (str), audio words location (str)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(outputFile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # This name will change and be dependant on input files
    layer = data_source.CreateLayer(inputFile["sessionID"], srs, ogr.wkbPoint)
    # Add the fields we're interested in
    field_name = ogr.FieldDefn("Speed", ogr.OFTReal)
    field_name.SetWidth(24)
    layer.CreateField(field_name)
    layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Time", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Sentence", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("BinSent", ogr.OFTReal))

    # 1. GPS Time list
    gps_times, first_time_index = gps_time_retrieval(inputFile['gps'])
    # 2. Want to connect it to the sentences first
    sentence_start, sentence_end, sentence_confidence, sentences = saving_sentence_data(inputFile['audio_sentences'])
    audio_start_time = audio_start_time_from_path(inputFile['audio_sentences'])
    # need the sentences start and end to be in datetime format
    sentences_start_time = sentences_proper_time_value(sentence_start, audio_start_time)
    # Index to find which sentences are cut off by the beginning of the ride
    gps_sentence_match_index, sentence_gps_match_index = matching_indexes(gps_times, sentences_start_time)

    # Opening up csv file to write data into
    # Gonna need to change output location and naming and all of that good stuff
    # mac directory
    # data_writer = open(r'/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/output/collated + ' + inputFile['sessionID'] + '.csv', 'w',newline='')
    data_writer = open(r"E:\UNI\Research_assistant\My test data\April 26th\output2\ " + inputFile['sessionID'] + '.csv',
                       'w', newline='')
    writer = csv.writer(data_writer)
    # csv_titles = ["Time", "Speed(m/s)", "Altitude(m)", "Distance(m)", "Heart Rate(BPM)", "RR Interval(ms)", "Emotions","Valence", "Arousal", "Dictionary Word", "Sentence", "EDA(uS)", "Temperature(Deg C)"]
    csv_titles = ["Time"]
    writer.writerow(csv_titles)
    # writer.writerow(sentences_start_time)
    # writer.writerow(sentences)
    with open(inputFile['gps']) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[2] == 'record' and row[0] == 'Data' and len(row) > 20 and row[10] != '' and row[21] and row[27] == "temperature" and row[26] == "m/s":  # and float(row[25]) > 0: #and row[3] != "time_created"
                speed = float(row[25])
                time = float(row[4]) - 55
                timestamp = datetime.fromtimestamp(time)
                time_variable = timestamp.strftime('%H:%M:%S')
                #long and lat
                position_lat_semi_circles = row[7]
                position_long_semi_circles = row[10]
                #Conversions
                position_lat_degrees = float(position_lat_semi_circles) * (180 / 2 ** 31)
                position_long_degrees = float(position_long_semi_circles) * (180 / 2 ** 31)

                feature = ogr.Feature(layer.GetLayerDefn())
                feature.SetField("Speed", speed)
                feature.SetField("Latitude", position_lat_degrees)
                feature.SetField("Longitude", position_long_degrees)
                feature.SetField("Time", str(time_variable))

                csv_data = [time_variable, float(row[25])]

                if time_variable == sentences_start_time[sentence_gps_match_index]:
                    csv_data.append(sentences[sentence_gps_match_index])
                    feature.SetField("Sentence",sentences[sentence_gps_match_index])
                    feature.SetField("BinSent", 1)
                    sentence_gps_match_index = sentence_gps_match_index + 1
                else:
                    # If there is no sentence to write
                    csv_data.append("N/A")
                    feature.SetField("Sentence", "N/A")
                    feature.SetField("BinSent", 0)
                # Writing info to the CSV file and writing the coordinates to the shape file
                writer.writerow(csv_data)
                wkt = f"POINT({position_long_degrees} {position_lat_degrees})"
                # Create the point from the Well Known Txt
                point = ogr.CreateGeometryFromWkt(wkt)
                feature.SetGeometry(point)
                layer.CreateFeature(feature)






#if __name__ == "__main__":
# analysis()

outputFile = r"E:\UNI\Research_assistant\My test data\Tommy 27th\output2withplustime"
analysis(inputFile, outputFile)
