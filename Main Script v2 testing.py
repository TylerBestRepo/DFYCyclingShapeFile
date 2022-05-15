import csv
import os

import osgeo.ogr as ogr
import osgeo.osr as osr
from datetime import datetime, timedelta
import time
import json
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
    'sessionID': 'Tyler 5th May',  #
    'gps': "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/Tyler May 5th.csv",  
    #'gps': r"E:\UNI\Research_assistant\My test data\May 5th\Tyler May 5th.csv",

    'txt_file': "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/Ben 14-05-2022.csv",




    'emotions':  "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/emotions may 5th.txt",
    #'emotions': r"E:\UNI\Research_assistant\My test data\May 5th\emotions may 5th.txt",

    'audio_sentences': "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/audio-20220505-175454.csv",
    'audio_words': "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/Tyler Words.csv",

    #'audio_sentences': r"E:\UNI\Research_assistant\My test data\May 5th\audio-20220505-175454.csv",
    #'audio_words': r"E:\UNI\Research_assistant\My test data\May 5th\word.csv",

    'dictionary_path': r'Dictionary.txt',  # This path will be a constant #
    'HRV_path': "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/heart rate data Tyler.csv",
    'empatica_EDA': "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/EDA.csv",
    'empatica_TEMP': "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/TEMP.csv", 
    # check code and debug/read through to determine
}

@dataclass
class textFile:
    path: str
    gps_start: str = field(default_factory=str)
    audio_start: datetime = None
    time_difference: int = 0

    def get_gps_time_sync(self) -> None:
        with open(self.path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[0] == 'GPS started at':
                    print(f"GPS recording started at: {row[1]}")
                    self.gps_start = row[1]
    
    def get_audio_time_sync(self) -> datetime:
        datetime_object = None
        with open(self.path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[0] == 'Date of ride':
                    type_test = row[1]
                    print(f"Date found at: {row[1]} and the type is: {type(type_test)}")
                    date_of_ride = str(row[1])
                    date_of_ride = date_of_ride.strip()

                if row[0] == 'Audio started at':
                    print(f"Audio start time is: {row[1]}")
                    time_string = str(row[1])
                    datetime_object = datetime.strptime(date_of_ride + ' ' + time_string, '%d-%m-%Y %H:%M:%S')

                    #self.audio_start = datetime_object
        
        return datetime_object

    
        

    # Function to find the difference (likely in seconds) between the date created value on the GPS vs the time sync on phone app
    def get_time_difference(self, gps_time_created):
        gps_lies_unix = time.mktime(datetime.strptime(gps_time_created, "%H:%M:%S").timetuple())
        sync_unix = time.mktime(datetime.strptime(self.gps_start, "%H:%M:%S").timetuple())
        self.time_difference = sync_unix - gps_lies_unix

@dataclass
class gps:
    gps_path: str
    gps_times: list[str] = field(default_factory=list)
    time_created: str = field(default_factory=str)
    time_difference: int = field(default_factory=int)

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
                    time_temp = float(row[4])  + self.time_difference
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
        return other_index_match

    def get_time_created(self) -> None:
        with open(self.gps_path) as bike_gps:
            gps_reader = csv.reader(bike_gps, delimiter=',')
            for row in gps_reader:
                if (row[0] == 'Data' and row[3] == 'time_created'):
                    unix_time_created = int(row[4])
                    time_temp = datetime.fromtimestamp(unix_time_created)
                    self.time_created = str(time_temp.strftime('%H:%M:%S')) 

@dataclass
class sentences:
    sentence_path: str
    individual_words_path: str
    list_length: int = 0
    end_of_list: bool = False
    sentence_audio_start: str = field(default_factory=str)
    sentence_start: list[str] = field(default_factory=list)
    sentence_end: list[str] = field(default_factory=list)
    sentences: list[str] = field(default_factory=list)
    sentence_confidence: list[str] = field(default_factory=list)
    audio_start_time: datetime = None
    sentence_start_time: list[str] = field(default_factory=list)
    sentence_end_time: list[str] = field(default_factory=list)

    def saving_sentence_data(self) -> None:
        with open(self.sentence_path) as audio:
            sentence_reader = csv.reader(audio, delimiter=",")
            for row in sentence_reader:
                if (row[0] != "start_time"):
                    self.sentence_start.append(float(row[0]))
                    self.sentence_end.append(float(row[1]))
                    self.sentences.append(row[2])
                    # In case confidences are not contained the in csv input file
                    if len(row) > 3:
                        self.sentence_confidence.append(float(row[3]))
        self.list_length = len(self.sentences)

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

    def save_sentences_csv_shape(self, csv_data, feature, sentence_gps_match_index) -> tuple[list, int]:
        csv_data.append(self.sentences[sentence_gps_match_index])
        feature.SetField("Sentence", self.sentences[sentence_gps_match_index])
        feature.SetField("BinSent", 1)
        sentence_gps_match_index += 1
        return csv_data, feature, sentence_gps_match_index

    def no_sentence_to_save(self, csv_data, feature) -> list:
        csv_data.append("N/A")
        feature.SetField("Sentence", "N/A")
        feature.SetField("BinSent", 0)
        return csv_data

    def end_of_list_check(self, sentence_gps_match_index) -> None:
        if sentence_gps_match_index != None:
            if ((sentence_gps_match_index + 1) == self.list_length):
                self.end_of_list = True



@dataclass
class emotions:
    """Data class that stores the data from the emotions txt file and contains methods to retrieve it"""
    file_path: str
    list_length: int = 0
    end_of_list: bool = False
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
                    counter = counter + 1
                elif counter == 1:
                    self.valence = x
                    counter = counter + 1
                elif counter == 2:
                    self.arousal = x
                    counter = counter + 1
                else:
                    self.times = x
        self.list_length = len(self.emotions)

    def write_available_emotions(self, csv_data, feature, emotions_gps_match_index) -> tuple[list, int]:
        csv_data.append(self.emotions[emotions_gps_match_index])
        csv_data.append(self.valence[emotions_gps_match_index])
        csv_data.append(self.arousal[emotions_gps_match_index])
        feature.SetField("Emotion", self.emotions[emotions_gps_match_index])
        feature.SetField("Valence", self.valence[emotions_gps_match_index])
        feature.SetField("Arousal", self.arousal[emotions_gps_match_index])
        emotions_gps_match_index += 1
        return csv_data, feature, emotions_gps_match_index

    def write_unavailable_emotions(self, csv_data, feature) -> list:
        csv_data.append('N/A')
        csv_data.append('N/A')
        csv_data.append('N/A')
        feature.SetField("Emotion", None)
        feature.SetField("Valence", None)
        feature.SetField("Arousal", None)
        return csv_data

    def end_of_list_check(self, emotions_gps_match_index) -> None:
        if ((emotions_gps_match_index + 1) == self.list_length):
            self.end_of_list = True


@dataclass
class Temporary_data:
    """This class temporarily stores all data that will be written into the CSV and the shape file"""
    speed: float = None
    time: str = None
    altitude: float = None
    position_lat_deg: float = None
    position_long_deg: float = None
    time_difference: int = field(default_factory=int)

    def get_row_data_and_convert(self, row) -> None:
        # x3.6 is to convert from m/s to km/h
        speed = (float(row[25])) * 3.6
        self.speed = round(speed, 2)
        altitude = float(row[16])
        self.altitude = (round(altitude))
        time = float(row[4])  + self.time_difference
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


@dataclass
class individual_words:
    """This class stores the individually spoken words as well as the functions to retrieve them"""
    audio_start_time: str
    file_path: str
    dict_path: str
    list_length: int = 0
    end_of_list: bool = False
    times_and_words: list[str] = field(default_factory=list)
    times: list[str] = field(default_factory=list)
    word_dictionary: list[str] = field(default_factory=list)
    dict_words_used_and_times: list[str] = field(default_factory=list)

    def storing_individual_transcribed_words_get_dictionary(self):
        with open(self.dict_path) as dict:
            dict_reader = csv.reader(dict)
            for list_of_words in dict_reader:
                word_dictionary = list_of_words
        times_words = []
        with open(self.file_path) as transcribed_words:
            word_reader = csv.reader(transcribed_words)
            for individual_words in word_reader:
                if not individual_words[0].isalnum() and not individual_words[2] == 'alternatives':
                    if not individual_words[3] == 'punctuation':
                        word_time = float(individual_words[0])
                        plus_start = timedelta(seconds=word_time)
                        word_time = (self.audio_start_time + plus_start).strftime('%H:%M:%S')
                        json_style = individual_words[2]
                        # a lot of hard coding to get it to format the string to json style right but it looks like it works
                        json_style = json_style.replace('[', '')
                        json_style = json_style.replace(']', '')
                        json_style = json_style.replace("': '", '": "')
                        json_style = json_style.replace("{'", '{"')
                        json_style = json_style.replace("'}", '"}')
                        json_style = json_style.replace("', '", '", "')
                        json_style = json_style.replace("': ", '": ')
                        parsed = json.loads(json_style)
                        time_and_word_temp = [word_time, parsed["content"]]
                        times_words.append(time_and_word_temp)

        self.times_and_words = times_words
        self.word_dictionary = word_dictionary

    def dictionary_words_used(self):
        words_used_with_times = []
        index = 0
        dict_length = len(self.word_dictionary)
        dict_index = 0
        for words in self.times_and_words:
            current_word = words[1]
            while dict_index < dict_length:
                dict_word_length = str(self.word_dictionary[dict_index])
                dict_word_length = len(dict_word_length)
                current_word_length = len(current_word)
                current_word = current_word.lower()
                # checking to see if the words are the same length alleviates the correct word within a longer word issue
                if current_word in self.word_dictionary[dict_index] and current_word_length == dict_word_length:
                    info_saving = [self.times_and_words[index][0], self.word_dictionary[dict_index], dict_index]
                    words_used_with_times.append(info_saving)
                    self.times.append(self.times_and_words[index][0])
                dict_index = dict_index + 1
            dict_index = 0
            index = index + 1

        self.dict_words_used_and_times = words_used_with_times
        self.list_length = len(self.times)

    def save_dictWords_csv_shape(self, csv_data, feature, words_gps_match_index) -> tuple[list, int]:
        csv_data.append(self.times_and_words[words_gps_match_index][1])
        feature.SetField("Dictionary", self.times_and_words[words_gps_match_index][1])
        feature.SetField("DictBinary", 1)
        words_gps_match_index += 1
        return csv_data, feature, words_gps_match_index

    def no_sentence_to_save(self, csv_data, feature) -> list:
        csv_data.append("N/A")
        feature.SetField("Dictionary", "N/A")
        feature.SetField("DictBinary", 0)
        return csv_data

    def end_of_list_check(self, words_gps_match_index) -> None:
        if (words_gps_match_index != None):
            if ((words_gps_match_index + 1) == self.list_length):
                self.end_of_list = True
        #since this one is guaranteed to be called after the other two possibilities im checking for duplicate entries here

        return words_gps_match_index


@dataclass
class hrv:
    path: str
    list_length: int = 0
    missing_time_counter: int = 0
    end_of_list: bool = False
    heart_rate: list[float] = field(default_factory=list)
    rr_interval: list[float] = field(default_factory=list)
    times: list[str] = field(default_factory=list)

    def get_hrv_data(self):
        with open(self.path) as hrv:
            hrv_reader = csv.reader(hrv, delimiter=";")
            first_value = False
            for row in hrv_reader:
                if not row[0].isalnum():
                    if not row[0] == '':
                        row_test = row[0][0]
                        if not row_test.isalpha():
                            time_elapsed = float(row[0])
                            heart_rate = float(row[1])
                            rr_interval = float(row[2])
                            # hrv_amplitude = float(row[3])
                            # regularity = float(row[4])
                            timestamp = row[5]
                            hours = int(timestamp[0:2])
                            minutes = int(timestamp[3:5])
                            seconds = int(timestamp[6:8])
                            annoying = [2021, 1, 5]
                            timestamp = datetime(annoying[0], annoying[1], annoying[2], hours, minutes,
                                                 seconds).strftime('%H:%M:%S')

                            #Need to check if there are 2 values for 1 time value                            
                            if (len(self.times) > 0):
                                if (self.times[-1] != timestamp):
                                    self.times.append(timestamp)
                                    self.heart_rate.append(heart_rate)
                                    self.rr_interval.append(rr_interval)
                            else:
                                self.times.append(timestamp)
                                self.heart_rate.append(heart_rate)
                                self.rr_interval.append(rr_interval)

                            

    def list_length_get(self) -> None:
        self.list_length = len(self.times)                          
                            
    def write_available_HRV(self, csv_data, feature, hrv_gps_match_index) -> tuple[list, int]:
        csv_data.append(self.heart_rate[hrv_gps_match_index])
        csv_data.append(self.rr_interval[hrv_gps_match_index])

        feature.SetField("Heart Rate", self.heart_rate[hrv_gps_match_index])
        feature.SetField("RRInterval", self.rr_interval[hrv_gps_match_index])

        # Checking if the next time value is more than 1 second greater than the current one
        if hrv_gps_match_index != None:
            if (hrv_gps_match_index < (self.list_length - 1)):
                nextTime = self.times[hrv_gps_match_index + 1]
                nextTimeUnix = time.mktime(datetime.strptime(nextTime, "%H:%M:%S").timetuple())
                currentTime = self.times[hrv_gps_match_index]
                currentTimeUnix = time.mktime(datetime.strptime(currentTime, "%H:%M:%S").timetuple())

                if (nextTimeUnix - currentTimeUnix) > 1:
                    self.missing_time_counter += 1
                else:
                    hrv_gps_match_index += 1
            else:
                hrv_gps_match_index += 1

        return csv_data, feature, hrv_gps_match_index

    def no_hrv_to_write(self, csv_data, hrv_gps_match_index) -> tuple[list, int]:
        csv_data.append("N/A")
        csv_data.append("N/A")

        hrv_gps_match_index += 1
        return csv_data, hrv_gps_match_index

    def end_of_list_check(self, hrv_gps_match_index) -> None:
        if hrv_gps_match_index != None:
            if (hrv_gps_match_index + 1) == self.list_length:
                self.end_of_list = True

@dataclass
class empatica:
    path_temp: str
    path_eda: str
    starting_time: str = ''
    start_time_unix: float = 0
    list_length: int = 0
    dividing_number: int = 0
    end_of_list: bool = False
    eda: list[float] = field(default_factory=list)
    temp: list[float] = field(default_factory=list)
    times: list[str] = field(default_factory=list)
    # Averaged from 4/sec to 1/sec
    eda_avg: list[float] = field(default_factory=list)
    temp_avg: list[float] = field(default_factory=list)

    def eda_extraction(self):
        eda_data = []
        skip_first = True
        with open(self.path_eda) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            counter = 0
            for row in csv_reader:
                if (counter == 0):
                    empatica_start_time = row[0]
                    empatica_start_time = float(empatica_start_time)
                    self.start_time_unix = empatica_start_time
                    timestamp = datetime.fromtimestamp(empatica_start_time)
                    converted_time = timestamp.strftime('%H:%M:%S')
                    self.starting_time = converted_time
                    #print(f"Converted start time = {converted_time}")
                    #greater than 1 because first data point is the time and second is the sampling rate then a 0 measurement
                if (counter > 2):
                    self.eda.append(float(row[0]))

                if counter == 1:
                    self.dividing_number = float(row[0])
                counter = counter + 1

    def temperature_extraction(self):
        counter = 0
        with open(self.path_temp) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if (counter > 2):
                    self.temp.append(float(row[0]))
                counter = counter + 1

    def time_list_get(self):
        second = 1
        plus_time = timedelta(seconds=second)
        time_temp = datetime.fromtimestamp(self.start_time_unix)
        
        start_time_from_string = str(time_temp.strftime('%H:%M:%S'))

        date_time_starting = datetime.strptime(start_time_from_string, '%H:%M:%S')
        new_time = date_time_starting

        self.times.append(self.starting_time)
        skip_first = False
        for y in self.eda_avg:
            if skip_first:
                new_time = (new_time + plus_time)
                converted_new_time = new_time.strftime('%H:%M:%S')
                self.times.append(converted_new_time)
            skip_first = True
        self.list_length = len(self.times)

    def data_averager(self):
        counter = 0
        averager_temp = 0
        averager_eda = 0
        mini_counter = 0
        while (counter < len(self.temp)):
            averager_temp = float(self.temp[counter]) + averager_temp
            averager_eda = float(self.eda[counter]) + averager_eda
            mini_counter = mini_counter + 1
            if (mini_counter == self.dividing_number):
                averager_temp = averager_temp / self.dividing_number
                averager_eda = averager_eda / self.dividing_number
                self.temp_avg.append(averager_temp)
                self.eda_avg.append(averager_eda)
                averager_temp = 0
                averager_eda = 0
                mini_counter = 0
            elif (counter == len(self.temp) - 1):
                averager_temp = averager_temp / mini_counter
                averager_eda = averager_eda / mini_counter
                self.temp_avg.append(averager_temp)
                self.eda_avg.append(averager_eda)
            counter = counter + 1

    def end_of_list_check(self, empatica_gps_match_index) -> None:
        if empatica_gps_match_index != None:
            if (empatica_gps_match_index + 1) == self.list_length:
                self.end_of_list = True


    def write_available_Empatica(self, csv_data, feature, empatica_gps_match_index) -> tuple[list, int]:

        csv_data.append(self.eda_avg[empatica_gps_match_index])
        csv_data.append(self.temp_avg[empatica_gps_match_index])

        feature.SetField("EDA (us)", self.eda_avg[empatica_gps_match_index])
        feature.SetField("Temp (C)", self.temp_avg[empatica_gps_match_index])

        empatica_gps_match_index += 1  
        
        return csv_data, feature, empatica_gps_match_index

    def no_empatica_to_save(self, csv_data) -> list:
        csv_data.append("N/A")
        csv_data.append("N/A")
        return csv_data


def analysis(inputFile, outputFile) -> None:
    """Main function here"""

    """Initialising all of the mapping necessities here"""
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(outputFile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # This name will change and be dependant on input files
    layer = data_source.CreateLayer(inputFile["sessionID"], srs, ogr.wkbPoint)
    # field_name = ogr.FieldDefn("Speed", ogr.OFTReal)
    # field_name.SetWidth(24)
    # layer.CreateField(field_name)
    # Defining all fields that are values in the shape file
    layer.CreateField(ogr.FieldDefn("Speed", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Time", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Altitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Sentence", ogr.OFTString))

    layer.CreateField(ogr.FieldDefn("Dictionary", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("DictBinary", ogr.OFTReal))

    layer.CreateField(ogr.FieldDefn("BinSent", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Emotion", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Valence", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Arousal", ogr.OFTReal))

    layer.CreateField(ogr.FieldDefn("Heart Rate", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("RRInterval", ogr.OFTReal))

    layer.CreateField(ogr.FieldDefn("EDA (us)", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Temp (C)", ogr.OFTReal))

    sentences_exist = False
    words_exist = False
    emotions_exists = False
    hrv_exists = False
    empatica_exists = False

    # 1. Initialising GPS data

    # Initiating the GPS class
    GPS = gps(gps_path=inputFile['gps'])
    # Calling method in class to extract times from the csv
    
    GPS.get_time_created()
    if (inputFile['txt_file'] != ''):
        TextFile = textFile(path=inputFile['txt_file'])
        TextFile.get_gps_time_sync()
        TextFile.get_time_difference(GPS.time_created)
        GPS.time_difference = TextFile.time_difference

    GPS.gps_time_retrieval()
    # 2. Initialising audio sentence data

    Sentences = sentences(sentence_path=inputFile['audio_sentences'], individual_words_path=inputFile['audio_words'])
    # Call method to extract first round of sentence data and the start time retrieving method
    if inputFile['audio_sentences'] != '':
        sentences_exist = True
        Sentences.saving_sentence_data()
        Sentences.audio_start_time_from_path()
        #using alternative method of getting the time from the txt, same way the gps does
        """Uncomment this one when the participants are guaranteed to have the phone update that outputs 24 hour time"""
        #Sentences.audio_start_time = TextFile.get_audio_time_sync()
        Sentences.sentences_start_time_conversion()
        # Getting the indexes for where the sentences and gps times line up
        sentence_gps_match_index = GPS.matching_indexes(Sentences.sentence_start_time)



        if inputFile['audio_words'] != '':
            words_exist = True
            start_time = Sentences.audio_start_time
            Words = individual_words(audio_start_time=start_time, file_path=inputFile['audio_words'],
                                     dict_path=inputFile['dictionary_path'])
            Words.storing_individual_transcribed_words_get_dictionary()
            # Run through function to check if any dictionary words were used
            Words.dictionary_words_used()
            # Function to check if the first dictionary words used falls within the gps frame
            words_gps_match_index = GPS.matching_indexes(Words.times)

    # 3. Initialising the emotions data
    # Check if emotions txt file exists
    Emotions = emotions(file_path=inputFile['emotions'])
    if inputFile['emotions'] != '':
        emotions_exists = True
        # Calling method to store all data from the text file
        Emotions.store_dominant_emotions()
        # Getting indexes to see the time that emotions and gps times overlap
        emotions_gps_match_index = GPS.matching_indexes(Emotions.times)
        # check if the indexes exist
        if emotions_gps_match_index is None:
            print(f"GPS times and emotions times have no overlaps. Must have input wrong files")
            exit()
    else:
        emotions_gps_match_index = 0

    # 4. HRV retrieving
    if (inputFile['HRV_path'] != ''):
        hrv_exists = True
        HRV = hrv(path=inputFile['HRV_path'])
        HRV.get_hrv_data()
        HRV.list_length_get()
        hrv_gps_match_index = GPS.matching_indexes(HRV.times)
        # check if the indexes exist
        if hrv_gps_match_index is None:
            print(f"GPS times and HRV times have no overlaps. Must have input wrong files")
            exit()
    else:
        hrv_gps_match_index = 0

    # 5. Empatica data extraction
    if (inputFile['empatica_EDA'] != ''):
        empatica_exists = True
        Empatica = empatica(path_temp=inputFile['empatica_TEMP'], path_eda=inputFile['empatica_EDA'])
        Empatica.eda_extraction()
        Empatica.temperature_extraction()
        Empatica.data_averager()
        Empatica.time_list_get()

        empatica_gps_match_index = GPS.matching_indexes(Empatica.times)


    data_writer = open(outputFile + '/' + inputFile['sessionID'] + '.csv', 'w', newline='')
    writer = csv.writer(data_writer)
    # csv_titles = ["Time", "Speed(km/h)", "Altitude(m)", "Distance(m)", "Heart Rate(BPM)", "RR Interval(ms)", "Emotions"
    # ,"Valence", "Arousal", "Dictionary Word", "Sentence", "EDA(uS)", "Temperature(Deg C)"]
    csv_titles = ["Time", "speed (km/h)", "Altitude (m)", "Sentence", "Dictionary Word", "Emotion", "Valence",
                  "Arousal", "Heart Rate", "RR Interval", "EDA (us)", "Temp (Deg C)"]
    writer.writerow(csv_titles)

    # Temporary row data class initialisation
    row_data = Temporary_data()
    row_data.time_difference = GPS.time_difference
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
                if sentences_exist and Sentences.end_of_list == False and sentence_gps_match_index != None:
                    if row_data.time == Sentences.sentence_start_time[sentence_gps_match_index]:
                        csv_data, feature, sentence_gps_match_index = Sentences.save_sentences_csv_shape(csv_data, feature,
                                                                                                sentence_gps_match_index)
                    else:
                        # If there is no sentence to write
                        csv_data = Sentences.no_sentence_to_save(csv_data, feature)
                else:
                    csv_data = Sentences.no_sentence_to_save(csv_data, feature)

                # GOTTA FINISH WRITING IN THIS ONE, PROLLY ONLY 60% DONE
                if words_exist and words_gps_match_index != None and words_gps_match_index != None:
                    if row_data.time == Words.times[words_gps_match_index]:
                        csv_data, feature, words_gps_match_index = Words.save_dictWords_csv_shape(csv_data, feature,
                                                                                         words_gps_match_index)
                    else:
                        csv_data, feature = Words.no_sentence_to_save(csv_data, feature)
                else:
                    # Would call same method from words class but that classes creation is dependant on the words file existing
                    csv_data.append("N/A")
                    feature.SetField("Dictionary", "N/A")
                    feature.SetField("DictBinary", 0)

                # Writing in emotion data
                # In case a file isn't provided this check is created to prevent bugs
                if emotions_exists and Emotions.end_of_list == False and emotions_gps_match_index != None:
                    if row_data.time == Emotions.times[emotions_gps_match_index]:
                        csv_data, feature, emotions_gps_match_index = Emotions.write_available_emotions(csv_data, feature,
                                                                                               emotions_gps_match_index)
                    else:
                        # might not need this else at all now
                        csv_data = Emotions.write_unavailable_emotions(csv_data, feature)
                else:
                    csv_data = Emotions.write_unavailable_emotions(csv_data, feature)

                if hrv_exists and HRV.end_of_list == False  and hrv_gps_match_index != None:
                    if row_data.time == HRV.times[hrv_gps_match_index]:
                        csv_data, feature, hrv_gps_match_index = HRV.write_available_HRV(csv_data, feature, hrv_gps_match_index)
                    else:
                        # might not need this else at all now
                        csv_data, hrv_gps_match_index = HRV.no_hrv_to_write(csv_data, hrv_gps_match_index)
                else:
                    # HRV file doesnt exist if this is entered
                    csv_data.append("N/A")
                    csv_data.append("N/A")

                if empatica_exists and Empatica.end_of_list == False and empatica_gps_match_index != None:
                    if row_data.time == Empatica.times[empatica_gps_match_index]:
                        csv_data, feature, empatica_gps_match_index = Empatica.write_available_Empatica(csv_data, feature, empatica_gps_match_index)
                    else:
                        csv_data = Empatica.no_empatica_to_save(csv_data)
                else:
                    csv_data.append("N/A")
                    csv_data.append("N/A")

                # Need to check if the emotion just written in is the last one in the list same as sentences
                if emotions_exists:
                    Emotions.end_of_list_check(emotions_gps_match_index)
                if sentences_exist:
                    Sentences.end_of_list_check(sentence_gps_match_index)
                if words_exist:
                    Words.end_of_list_check(words_gps_match_index)
                if hrv_exists:
                    HRV.end_of_list_check(hrv_gps_match_index)
                if empatica_exists:
                    Empatica.end_of_list_check(empatica_gps_match_index)

                # Writing info to the CSV file and writing the coordinates to the shape file
                writer.writerow(csv_data)

                # do shapefile positional things
                shape_file.positonal_method(feature, layer, row_data)


#outputFile = r"E:\UNI\Research_assistant\My test data\May 5th\output"  # windows path

# My data path
# outputFile = "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/output" # MAC pathname
# Tommy data path
outputFile = "/Users/tylerbest/Desktop/Research Assistant/Test data/May 5th Tyler/output"
analysis(inputFile, outputFile)
