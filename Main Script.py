import csv
import os

import osgeo
import osgeo.ogr as ogr
import osgeo.osr as osr
from datetime import datetime, timedelta
import time
import sys
import json
 
 #examples of inputfile
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

inputFile = {
    'sessionID' : 'Tyler quick ride on the 14th of April', #
    'gps' : r"/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/April-14.csv", #
    
    'emotions' : r"/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/1404 dominant emotions.txt", #

    'audio_sentences' : r"/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/audio-20220414-180037.csv",
    'audio_words' : r"/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/1404 individual words.csv",

    'dictionary_path' : r'Dictionary.txt',# This path will be a constant #
    'HRV_path' : r'/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/eSense Pulse data from 14.04.22 17_59_22.csv',
    'empatica_EDA' : '/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/EDA.csv', # Have I written these two empatica things in to be written?
    'empatica_TEMP' : '/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/TEMP.csv' #check code and debug/read through to determine

}


def analysis(inputFile, outputFile):
    #input File (dict):
    #must include sessionID (str), transcript file location (str), video emotion file location (str), audio words location (str)

    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(outputFile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # create the layer
    # This name will change and be dependant on input files
    layer = data_source.CreateLayer(inputFile["sessionID"], srs, ogr.wkbPoint)

    # Add the fields we're interested in
    field_name = ogr.FieldDefn("Speed", ogr.OFTReal)
    field_name.SetWidth(24)
    layer.CreateField(field_name)
    layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Distance", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Altitude", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Time", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("HeartRate", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("RRInterval", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Sentence", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("BinSent", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Emotion", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Valence", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Arousal", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("EDA"), ogr.OFTReal)
    layer.CreateField(ogr.FieldDefn("TEMP"), ogr.OFTReal)
    layer.CreateField(ogr.FieldDefn("DictionaryWords", ogr.OFTReal))


    # Incorporating functions and data from additional sources

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

    # Index matching for video and GPS
    def time_index_matching_function(gps_times,video_times):
        counter = 0
        match_found = False
        gps_index_find = None
        video_index_find = None
        for gps_index, y in enumerate(gps_times):
            #counter_2 = 0
            for video_index,  z in enumerate(video_times):
                if y == z:
                    print("we have a match")
                    gps_index_find = gps_index
                    video_index_find = video_index
                    match_found = True
                    break

            if match_found:
                break
        return gps_index_find, video_index_find


    # For dominant emotions
    def store_dominant_emotions(file_path):
        with open(file_path) as emotions:
            emotions_reader = csv.reader(emotions, delimiter=",")
            counter = 0
            for x in emotions_reader:
                if counter == 0:
                    emotions_list = x
                    counter = counter + 1
                elif counter == 1:
                    valence = x
                    counter = counter + 1
                elif counter == 2:
                    arousal = x
                    counter = counter + 1
                else:
                    emotions_time = x
        return emotions_list, valence, arousal, emotions_time


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
            for row in gps_reader:
                #if i[2] == 'record' and i[0] == 'Data' and len(i) > 20:
                if row[2] == 'record' and row[0] == 'Data' and len(row) > 20 and row[10] != '' and row[21]:
                    time_temp = float(row[4])
                    time_temp = datetime.fromtimestamp(time_temp)
                    time_temp = str(time_temp.strftime('%H:%M:%S'))
                    gps_times.append(time_temp)
        return gps_times


    def start_time_from_path(file_name):
        day = int(file_name[12:14])
        month = int(file_name[10:12])
        year = int(file_name[6:10])
        hours = int(file_name[15:17])
        minutes = int(file_name[17:19])
        seconds = int(file_name[19:21])
        combined = datetime(year, month, day, hours, minutes, seconds)
        return combined


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


    def storing_individual_transcribed_words_get_dictionary(audio_words_path,dict_path, audio_starting_time):
        with open(dict_path) as dict:
            dict_reader = csv.reader(dict)
            for list_of_words in dict_reader:
                word_dictionary = list_of_words
        times_words = []
        with open(audio_words_path) as transcribed_words:
            word_reader = csv.reader(transcribed_words)
            for individual_words in word_reader:
                if not individual_words[0].isalnum() and not individual_words[2] == 'alternatives':
                    if not individual_words[3] == 'punctuation':
                        word_time = float(individual_words[0])
                        plus_start = timedelta(seconds=word_time)
                        word_time = (audio_starting_time + plus_start).strftime('%H:%M:%S')
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
        return times_words, word_dictionary


    def dictionary_words_used(word_dictionary, time_and_words):
        words_used_with_times = []
        index = 0
        dict_length = len(word_dictionary)
        dict_index = 0
        for words in time_and_words:
            current_word = words[1]
            while dict_index < dict_length:
                dict_word_length = str(dictionary[dict_index])
                dict_word_length = len(dict_word_length)
                current_word_length = len(current_word)
                current_word = current_word.lower()
                # checking to see if the words are the same length alleviates the correct word within a longer word issue
                if current_word in dictionary[dict_index] and current_word_length == dict_word_length:
                    info_saving = [times_and_words[index][0], dictionary[dict_index], dict_index]
                    words_used_with_times.append(info_saving)
                dict_index = dict_index + 1
            dict_index = 0
            index = index + 1
        return words_used_with_times

    def sentences_proper_time_value(start_or_end, audio_start):
        sentence_time_fixed = []
        for x in start_or_end:
            word_time = float(x)
            plus_start = timedelta(seconds=word_time)
            word_time = (audio_start + plus_start).strftime('%H:%M:%S')
            sentence_time_fixed.append(word_time)
        return sentence_time_fixed

    def get_hrv_data(hrv_path):
        hrv_data = []
        hrv_times = []
        with open(hrv_path) as hrv:
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
                            timestamp = datetime(annoying[0], annoying[1], annoying[2], hours, minutes,
                                                 seconds).strftime('%H:%M:%S')
                            combined = [time_elapsed, heart_rate, rr_interval, hrv_amplitude, regularity, timestamp]
                            hrv_times.append(timestamp)
                            hrv_data.append(combined)
                            print(
                                f"Heart Rate: {heart_rate}\tHRV amplitude: {hrv_amplitude}\tTime of measurement: {timestamp}\n")

        return hrv_data, hrv_times

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
                    eda_data.append(float(row[0]))
                    #skip_first = False

                if counter == 1:
                    dividing_number_empatica = row[0]
                counter = counter + 1
        return eda_data, empatica_start_time, float(dividing_number_empatica)

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

    def empatica_data_averager(temp_data, eda_data):
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
                averager_temp = averager_temp / dividing_number
                averager_eda = averager_eda / dividing_number
                new_temp_data.append(averager_temp)
                new_eda_data.append(averager_eda)
                averager_temp = 0
                averager_eda = 0
                mini_counter = 0
            elif (counter == len(temp_data) - 1):
                averager_temp = averager_temp / mini_counter
                averager_eda = averager_eda / mini_counter
                new_temp_data.append(averager_temp)
                new_eda_data.append(averager_eda)
            counter = counter + 1

        return new_temp_data, new_eda_data

    # CALLING FUNCTIONS TO TO RETRIEVE CSV DATA AND FIND REQUIRED INDEXES
    # 1. Get times for GPS first
    gps_times = gps_time_retrieval(inputFile['gps'])
    # 2. Get dominant emotions and their times
    emotions_list, valence, arousal, emotions_time = store_dominant_emotions(inputFile['emotions'])
    # 3. Get time indexes for when these two data sets match up
    gps_time_index_emotionCompare, emotion_time_index = time_index_matching_function(gps_times,emotions_time)
    # Stopping the script from running early if there is no time overlap betwen gps and emotions
    if gps_time_index_emotionCompare is None and emotion_time_index is None:
        print(f"GPS times and emotions times have no overlaps. Must have input wrong files")
        exit()
    # 4. Retrieve the transcribed sentences and do minor time calculations on them
    sentence_start, sentence_end, sentence_confidence, sentences = saving_sentence_data(inputFile['audio_sentences'])
    audio_start_time = audio_start_time_from_path(inputFile['audio_sentences'])
    # 5. Retrieve the individual transcribed words and check them against the dictionary to determine their addition to the shapefile
    times_and_words, dictionary = storing_individual_transcribed_words_get_dictionary(inputFile['audio_words'], inputFile['dictionary_path'], audio_start_time)
    # an index in the main writing loop to the shapefile should be used to keep track of which words and times have been added
    dict_words_used_with_times = dictionary_words_used(dictionary, times_and_words)

    # need the sentences start and end to be in datetime format
    sentences_start_time = sentences_proper_time_value(sentence_start, audio_start_time)
    sentences_end_time = sentences_proper_time_value(sentence_end, audio_start_time)

    #6. Retrieving HRV data and then figuring out when it should be written into the main loop
    write_hrv = False
    hrv_file_doesnt_exist = False
    if(inputFile['HRV_path'] == ''):
        print("No HRV file was input")
        hrv_file_doesnt_exist = True
    else:
        hrv_data, hrv_times = get_hrv_data(inputFile['HRV_path'])
        # Time index figuring out now
        gps_hrv_maching_index, hrv_gps_matching_index = time_index_matching_function(gps_times, hrv_times)
        write_hrv = False
        if gps_hrv_maching_index < hrv_gps_matching_index:
            write_hrv = True
        else:
            write_hrv = False
    #7. Pulling the empatica data (EDA and Temperature)
    # Empatica starting time will be used for both
    if (inputFile['empatica_EDA'] == ''):
        print("No Empatica file was input")
        empatica_doesnt_exist = True
    else:
        eda_data, empatica_starting_time, dividing_number = eda_extraction_empatica(inputFile['empatica_EDA'])
        temperature_data = temperature_extraction_empatica(inputFile['empatica_TEMP'])
        # Bit of logic to determine if starting time is before or after GPS (compare indexes function first)
        #pass in the averaged eda data to get a better TIME list length
        temperature_data_averaged, eda_data_averaged = empatica_data_averager(temperature_data, eda_data)
        empatica_time_list = time_list_for_empatica(empatica_starting_time, eda_data_averaged)
        gps_time_index_empaticaCompare, empatica_time_index = time_index_matching_function(gps_times, empatica_time_list)

        print(f"The gps time index is: {gps_times[gps_time_index_empaticaCompare]} and the empatica one is: {empatica_time_list[empatica_time_index]}")

        if gps_time_index_empaticaCompare < empatica_time_index:
            gps_before_empatica = False
            empatica_index = empatica_time_index
        else:
            gps_before_empatica = True
            empatica_index = 0

            #Still gotta code into the main loop to write the empatica datafore_empatica = True


    # Idea is that gps will be device first turned on then emotions will be index 1 and gps will already have written x number of points to shapefile.
    # However, a backup incase audio recording begins first should be coded. Perhaps making it start at the GPS one no matter what.
    if gps_time_index_emotionCompare < emotion_time_index:
        is_GPS_first = False
    else:
        is_GPS_first = True
    # if GPS_first == True, then gps_time_index is x and emotion is 1, so an iterative check should be performed until
    # gps_time_index == x then emotion data starts being written
    # if GPS_first == False then emotion_time_index = x and gps_time_index = 1. Therefore, up until x emotions will be cut
    # off in the shapefile

    # Finding if sentences comes before GPS reading
    gps_sentence_maching_index, sentence_start_gps_matching_index = time_index_matching_function(gps_times, sentences_start_time)
    if gps_sentence_maching_index > sentence_start_gps_matching_index:
        GPS_before_sentence = True
    else:
        GPS_before_sentence = False
    i = 0
    dict_idx = 0
     # This needs to be changed if first time is before GPS starts
    if GPS_before_sentence:
        sentence_idx = 0
    else:
        sentence_idx = sentence_start_gps_matching_index
    hrv_writing_idx = 0
    if write_hrv:
        hrv_writing_idx = hrv_gps_matching_index
    write_sentence = False
    new_sentence = False
    write_emotions = False
    write_empatica = False
    if gps_before_empatica == False:
        write_empatica = True

    # Opening up csv file to write data into
    # Gonna need to change output location and naming and all of that good stuff
    data_writer = open(r'/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/output/collated + ' + inputFile['sessionID'] + '.csv', 'w',newline='')
    writer = csv.writer(data_writer)
    csv_titles = ["Time", "Speed(m/s)", "Altitude(m)", "Distance(m)", "Heart Rate(BPM)", "RR Interval(ms)", "Emotions", "Valence", "Arousal", "Dictionary Word", "Sentence", "EDA(uS)", "Temperature(Deg C)"]
    writer.writerow(csv_titles)
    with open(inputFile['gps']) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        row_counter = 0
        for row in csv_reader:
            if row[2] == 'record' and row[0] == 'Data' and len(row) > 20 and row[10] != '' and row[21]:
                #indexes found manually or by using Finding_indexes.py
                position_lat_semi_circles = row[7]
                position_long_semi_circles = row[10]
                speed = row[25]
                distance = row[22]
                altitude = row[16]
                time = row[4]

                do_write_sentence = 1
                #dont_write_sentence = 0 #Dont think i need this one

                if not is_GPS_first:
                    if i == gps_time_index_emotionCompare:
                        write_emotions = True
                if is_GPS_first:
                    write_emotions = True


                if len(position_lat_semi_circles) > 1:  # This is needed because the first measurement i pulled contained no values so I'm essentially doing all this to ignore the first reading or any null readings
                    position_lat_degrees = float(position_lat_semi_circles) * (180 / 2**31)
                    position_long_degrees = float(position_long_semi_circles) * (180 / 2 ** 31)
                    # We want to convert speed from a string to a number value
                    #if len(speed) < 1: # Some data points fall under the same two categories for pulling data but only output location data with no other parameters so the speed is manually set to 0
                        #speed = "0"
                    speed = float(speed)
                    time = float(time)
                    altitude = float(altitude)
                    distance = float(distance)
                    timestamp = datetime.fromtimestamp(time) # This can output up to date time and year but for this we probably only need hours minutes seconds
                    # print(timestamp.strftime('%M:%S')) #This timestamp comes out as a string, before this conversion it is some sort of time object
                    time_variable = timestamp.strftime('%H:%M:%S')
                    #This bool check needed to be moved to after the time was converted to a string
                    if hrv_file_doesnt_exist == False:
                        if not write_hrv:
                            if time_variable == hrv_times[i]:
                                write_hrv = True
                            else:
                                write_hrv = False
                    # create the feature
                    feature = ogr.Feature(layer.GetLayerDefn())
                    # Set the attributes using the values from the delimited text file
                    feature.SetField("Speed", speed)
                    feature.SetField("Latitude", position_lat_degrees)
                    feature.SetField("Longitude", position_long_degrees)
                    # feature.SetField("Cadence", cadence) # Cadence measurements probably wont be used as the measurement devices are too annoying to attach to the users bike
                    feature.SetField("Distance", distance)
                    feature.SetField("Altitude", altitude)
                    feature.SetField("Time", str(time_variable))

                    #Initialising a list to store data to the csv
                    #Converting floating numbers to strings to save a specific number of characters to not bloat the txt file
                    speed_save = "{:.4f}".format(speed)
                    altitude_save = "{:.2f}".format(altitude)
                    distance_save = "{:.3f}".format(distance)
                    csv_data_to_write = [str(time_variable), speed_save, altitude_save, distance_save]
                    if write_hrv:
                        csv_data_to_write.append(hrv_data[hrv_writing_idx][1])
                        csv_data_to_write.append(hrv_data[hrv_writing_idx][2])
                        feature.SetField("HeartRate", hrv_data[hrv_writing_idx][1])
                        feature.SetField("RRInterval", hrv_data[hrv_writing_idx][2])

                    if write_emotions:
                        if len(emotions_list) > i:
                            feature.SetField("Emotion", emotions_list[i])  # Not sure this bit right here is correct, indexing could be funky
                            feature.SetField("Valence", valence[i])
                            feature.SetField("Arousal", arousal[i])
                            csv_data_to_write.append(emotions_list[i])
                            csv_data_to_write.append(valence[i])
                            csv_data_to_write.append(arousal[i])
                        else:
                            print("No emotions to write here")
                            csv_data_to_write.append(' ')
                            csv_data_to_write.append(' ')
                            csv_data_to_write.append(' ')
                    #Need a boolean to check if any dictionary words were used to not compare to an empty list if none were used
                    if dict_words_used_with_times:
                        if gps_times[i] == dict_words_used_with_times[dict_idx][1]:
                            feature.SetField("DictionaryWords", dict_words_used_with_times[dict_idx][1])
                            feature.SetField("DictionaryIdx", dict_words_used_with_times[dict_idx][2])
                            csv_data_to_write.append(dict_words_used_with_times[dict_idx][1])
                            dict_idx = dict_idx + 1
                    else:
                        csv_data_to_write.append('N/A')
                        feature.SetField("DictionaryWords", "Not applicable")
                        feature.SetField("DictionaryIdx", "Not applicable")

                        # Write in the sentences here
                        # Sentences can start before the GPS atm and causes no sentence data to get written
                        iWantToUse = False
                        if (iWantToUse == True):
                            if (gps_times[i] == sentences_start_time[sentence_idx]):
                                write_sentence = True
                            if (gps_times[i] == sentences_end_time[sentence_idx]):
                                new_sentence = True
                                write_sentence = False
                            if not write_sentence and not new_sentence:
                                csv_data_to_write.append('N/A')
                            if write_sentence:
                                # csv_data_to_write.append(sentences[sentence_idx])
                                csv_data_to_write.append("No sentence spoken")
                                feature.SetField("Sentence", sentences[sentence_idx])
                                # feature.SetField("BinSent", "Yes")
                            if new_sentence:
                                csv_data_to_write.append(sentences[sentence_idx])
                                feature.SetField("Sentence", sentences[sentence_idx])
                                feature.SetField("BinSent", 1)
                                sentence_idx = sentence_idx + 1
                                new_sentence = False
                            else:
                                feature.SetField("BinSent", 0)
                        #Testing an alternative more simple method of writing in sentences that might be more correct
                        if (gps_times[i] == sentences_start_time[sentence_idx]):
                            csv_data_to_write.append(sentences[sentence_idx])
                            feature.SetField("Sentence", sentences[sentence_idx])
                            feature.SetField("BinSent", 1)
                            sentence_idx = sentence_idx + 1
                        else:
                            csv_data_to_write.append("No sentence spoken")
                            feature.SetField("Sentence", "N/A")
                            feature.SetField("BinSent", 0)

                        if (empatica_index + i <= len(eda_data)):
                            if write_empatica == True:
                                feature.SetField("EDA", eda_data_averaged[empatica_index + i])
                                feature.SetField("TEMP", temperature_data_averaged[empatica_index + i])
                                csv_data_to_write.append(eda_data_averaged[empatica_index + i])
                                csv_data_to_write.append(temperature_data_averaged[empatica_index + i])
                            else:
                                csv_data_to_write.append("EDA data N/A")
                                csv_data_to_write.append("TEMP data N/A")
                        writer.writerow(csv_data_to_write)

                    # create the WKT for the feature using Python string formatting
                    wkt = f"POINT({position_long_degrees} {position_lat_degrees})"
                    #print("wkt: {}".format(wkt))

                    # Create the point from the Well Known Txt
                    point = ogr.CreateGeometryFromWkt(wkt)
                    feature.SetGeometry(point)
                    layer.CreateFeature(feature)

                    feature = None
                    row_counter = row_counter + 1

                i = i + 1
                hrv_writing_idx = hrv_writing_idx + 1
        data_source = None



#if __name__ == "__main__":
   #analysis()

outputFile = r"/Users/tylerbest/Desktop/Research Assistant/Test data/Test data 14th April/output"

analysis(inputFile, outputFile)

