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
    'sessionID': 'Tyler 1st May',  #
    'gps': r"E:\UNI\Research_assistant\My test data\May 1st\May 1 Ride.csv",  #

    'emotions': r"",
    #

    'audio_sentences': r"E:\UNI\Research_assistant\My test data\May 1st\audio-20220501-154437.csv",
    'audio_words': r"E:\UNI\Research_assistant\My test data\May 1st\0105-Individual words.csv",

    # 'dictionary_path': r'Dictionary.txt',  # This path will be a constant #
    # 'HRV_path': r'/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/eSense Pulse data from 14.04.22 17_59_22.csv',
    # 'empatica_EDA': '/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/EDA.csv',
    # Have I written these two empatica things in to be written?
    # 'empatica_TEMP': '/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/TEMP.csv'
    # check code and debug/read through to determine

}


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


@dataclass
class sentences:
    sentence_path: str
    individual_words_path: str
    sentence_start: list[str] = field(default_factory=list)
    sentence_end: list[str] = field(default_factory=list)
    sentences: list[str] = field(default_factory=list)
    sentence_confidence: list[str] = field(default_factory=list)
    audio_start_time: datetime = None
    sentence_start_time: list[str] = field(default_factory=list)
    sentence_end_time: list[str] = field(default_factory=list)

    def saving_sentence_data(self) -> None:
        with open(self.sentence_path) as audio:
            emotions_reader = csv.reader(audio, delimiter=",")
            for row in emotions_reader:
                self.sentence_start.append(float(row[0]))
                self.sentence_end.append(float(row[1]))
                self.sentences.append(row[2])
                if len(row) > 3:
                    self.sentence_confidence.append(float(row[3]))

    def audio_start_time_from_path(self) -> None:
        file_name = os.path.basename(self.sentence_path)
        day = int(file_name[12:14])
        month = int(file_name[10:12])
        year = int(file_name[6:10])
        hours = int(file_name[15:17])
        minutes = int(file_name[17:19])
        seconds = int(file_name[19:21])
        combined = datetime(year, month, day, hours, minutes, seconds)
        self.audio_start_time = combined

    def sentences_start_time_conversion(self) -> None:
        previous_time = 0
        plus_one = timedelta(seconds=1)
        for x in self.sentence_start:
            word_time = float(x)
            word_time = round(word_time)
            plus_start = timedelta(seconds=word_time)
            word_time = (self.audio_start_time + plus_start)
            if (word_time == previous_time):
                # this will prevent the instance of one number rounding up to a number and the next getting rounded down to the same number
                word_time = word_time + plus_one

            self.sentence_start_time.append(word_time.strftime('%H:%M:%S'))
            previous_time = word_time

    def save_sentences_csv_shape(self,csv_data,feature,sentence_gps_match_index) -> tuple[list, int]:
        csv_data.append(self.sentences[sentence_gps_match_index])
        feature.SetField("Sentence", self.sentences[sentence_gps_match_index])
        feature.SetField("BinSent", 1)
        sentence_gps_match_index += 1
        return csv_data, sentence_gps_match_index

    def no_sentence_to_save(self, csv_data, feature) -> list:
        csv_data.append("N/A")
        feature.SetField("Sentence", "N/A")
        feature.SetField("BinSent", 0)
        return csv_data

@dataclass
class emotions:
    """Data class that stores the data from the emotions txt file and contains methods to retrieve it"""
    file_path: str
    emotion_data_exists: bool = False
    emotions: list[str] = field(default_factory=list)
    valence: list[str] = field(default_factory=list)
    arousal: list[str] = field(default_factory=list)
    times: list[str] = field(default_factory=list)


    # Lists are done slightly differently so need to test this assigning out
    def store_dominant_emotions(self) -> None:
        with open(self.file_path) as emotion_data:
            emotions_reader = csv.reader(emotion_data, delimiter=",")
            counter = 0
            for x in emotions_reader:
                if counter == 0:
                    self.emotions = x
                    self.emotion_data_exists = True
                    counter = counter + 1
                elif counter == 1:
                    self.valence = x
                    counter = counter + 1
                elif counter == 2:
                    self.arousal = x
                    counter = counter + 1
                else:
                    self.times = x

    def write_available_emotions(self, csv_data, feature, emotions_gps_match_index) -> tuple[list, int]:
        csv_data.append(self.emotions[emotions_gps_match_index])
        csv_data.append(self.valence[emotions_gps_match_index])
        csv_data.append(self.arousal[emotions_gps_match_index])
        feature.SetField("Emotion", self.emotions[emotions_gps_match_index])
        feature.SetField("Valence", self.valence[emotions_gps_match_index])
        feature.SetField("Arousal", self.arousal[emotions_gps_match_index])
        emotions_gps_match_index += 1
        return csv_data, emotions_gps_match_index

    def write_unavailable_emotions(self, csv_data, feature) -> list:
        csv_data.append('N/A')
        csv_data.append('N/A')
        csv_data.append('N/A')
        feature.SetField("Emotion", 'N/A')
        feature.SetField("Valence", 'N/A')
        feature.SetField("Arousal", 'N/A')
        return csv_data


@dataclass
class Temporary_data:
    """This class temporarily stores all data that will be written into the CSV and the shape file"""
    speed: float = None
    time: str = None
    altitude: float = None
    position_lat_deg: float = None
    position_long_deg: float = None

    def get_row_data_and_convert(self, row) -> None:
        # x3.6 is to convert from m/s to km/h
        self.speed = (float(row[25]))*3.6
        self.altitude = (float(row[16]))
        time = float(row[4])  # - 55
        timestamp = datetime.fromtimestamp(time)
        time_variable = timestamp.strftime('%H:%M:%S')
        self.time = time_variable

        # Positional
        position_lat_semi_circles = row[7]
        position_long_semi_circles = row[10]
        # Conversions
        self.position_lat_deg = float(position_lat_semi_circles) * (180 / 2 ** 31)
        self.position_long_deg = float(position_long_semi_circles) * (180 / 2 ** 31)


class shape_file_methods:
    """Class to group the methods that are used to write data to the shape file"""

    def store_mapping_data(self, feature, row_data) -> None:
        feature.SetField("Speed", row_data.speed)
        feature.SetField("Time", row_data.time)
        feature.SetField("Altitude", row_data.altitude)

    def positonal_method(self, feature, layer, row_data) -> None:
        wkt = f"POINT({row_data.position_long_deg} {row_data.position_lat_deg})"
        # Create the point from the Well Known Txt
        point = ogr.CreateGeometryFromWkt(wkt)
        feature.SetGeometry(point)
        layer.CreateFeature(feature)



def analysis(inputFile, outputFile) -> None:
    """Main function here"""

    """Initialising all of the mapping necessities here"""
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(outputFile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # This name will change and be dependant on input files
    layer = data_source.CreateLayer(inputFile["sessionID"], srs, ogr.wkbPoint)
    field_name = ogr.FieldDefn("Speed", ogr.OFTReal)
    field_name.SetWidth(24)
    layer.CreateField(field_name)
    # Defining all fields that are values in the shape file
    layer.CreateField(ogr.FieldDefn("Time", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Altitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Sentence", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("BinSent", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Emotion", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Valence", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Arousal", ogr.OFTReal))

    # 1. Initialising GPS data

    # Initiating the GPS class
    GPS = gps(gps_path=inputFile['gps'])
    # Calling method in class to extract times from the csv
    GPS.gps_time_retrieval()
    # 2. Initialising audio sentence data

    Sentences = sentences(sentence_path=inputFile['audio_sentences'], individual_words_path=inputFile['audio_words'])
    # Call method to extract first round of sentence data and the start time retrieving method
    Sentences.saving_sentence_data()
    Sentences.audio_start_time_from_path()
    Sentences.sentences_start_time_conversion()
    # Getting the indexes for where the sentences and gps times line up
    gps_sentence_match_index, sentence_gps_match_index = GPS.matching_indexes(Sentences.sentence_start_time)

    # 3. Initialising the emotions data
    # Check if emotions txt file exists
    Emotions = emotions(file_path=inputFile['emotions'])
    if inputFile['emotions'] != '':
        # Calling method to store all data from the text file
        Emotions.store_dominant_emotions()
        # Getting indexes to see the time that emotions and gps times overlap
        gps_emotions_match_index, emotions_gps_match_index = GPS.matching_indexes(Emotions.times)
        # check if the indexes exist
        if gps_emotions_match_index is None and emotions_gps_match_index is None:
            print(f"GPS times and emotions times have no overlaps. Must have input wrong files")
            exit()
    else:
        emotions_gps_match_index = 0


    # 4. HRV retrieving

    data_writer = open(outputFile + r"\ " + inputFile['sessionID'] + '.csv', 'w', newline='')
    writer = csv.writer(data_writer)
    # csv_titles = ["Time", "Speed(km/h)", "Altitude(m)", "Distance(m)", "Heart Rate(BPM)", "RR Interval(ms)", "Emotions"
    # ,"Valence", "Arousal", "Dictionary Word", "Sentence", "EDA(uS)", "Temperature(Deg C)"]
    csv_titles = ["Time", "speed (km/h)", "Altitude (m)", "Sentence", "Emotion", "Valence", "Arousal"]
    writer.writerow(csv_titles)

    # Temporary row data class initialisation
    row_data = Temporary_data()
    shape_file = shape_file_methods()

    with open(inputFile['gps']) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[2] == 'record' and row[0] == 'Data' and len(row) > 20 and row[10] != '' and row[21] and row[
                27] == "temperature" and row[26] == "m/s":  # and float(row[25]) > 0: #and row[3] != "time_created"
                # Methods saving necessary data and also making conversions where necessary
                row_data.get_row_data_and_convert(row)

                feature = ogr.Feature(layer.GetLayerDefn())

                # Method to store the speed and time
                shape_file.store_mapping_data(feature, row_data)
                # adding time and speed to the csv appending list
                csv_data = [row_data.time, row_data.speed, row_data.altitude]
                # Writing in sentence data
                if row_data.time == Sentences.sentence_start_time[sentence_gps_match_index]:
                    csv_data, sentence_gps_match_index = Sentences.save_sentences_csv_shape(csv_data, feature, sentence_gps_match_index)
                else:
                    # If there is no sentence to write
                    csv_data = Sentences.no_sentence_to_save(csv_data, feature)

                # Writing in emotion data
                # In case a file isn't provided this check is created to prevent bugs
                if Emotions.emotion_data_exists:
                    if row_data.time == Emotions.times[emotions_gps_match_index]:
                        csv_data, emotions_gps_match_index = Emotions.write_available_emotions(csv_data, feature, emotions_gps_match_index)
                    else:
                        csv_data = Emotions.write_unavailable_emotions(csv_data, feature)


                # Writing info to the CSV file and writing the coordinates to the shape file
                writer.writerow(csv_data)

                # do shapefile positional things
                shape_file.positonal_method(feature, layer, row_data)


outputFile = r"E:\UNI\Research_assistant\My test data\May 1st\output"
analysis(inputFile, outputFile)
