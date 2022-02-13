import csv
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
# }

inputFile = {
    'sessionID' : 'Test data from 3rd Feb', #
    'gps' : 'Feb-3.csv', #
    'emotions' : '03022022 dominant emotions.txt', #
    'audio_sentences' : "audio-20220302-104404.csv",
    'audio_words' : 'audio-20220302-individual-words.csv',
    'dictionary_path' : 'Dictionary.txt', # This path will be a constant #
    'HRV_path' : 'eSense Pulse data from 09.02.22 13_22_59.csv'

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
    layer.CreateField(ogr.FieldDefn("Sentence", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Emotion", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("DictionaryWords", ogr.OFTReal))


    # Incorporating functions and data from additional sources

    # Getting the time variable data from the file name (audio sentence transcription)
    def audio_start_time_from_path(file_name):
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
    

    # CALLING FUNCTIONS TO TO RETRIEVE CSV DATA AND FIND REQUIRED INDEXES
    # 1. Get times for GPS first
    gps_times = gps_time_retrieval(inputFile['gps'])
    # 2. Get dominant emotions and their times
    emotions_list, emotions_time = store_dominant_emotions(inputFile['emotions'])
    # 3. Get time indexes for when these two data sets match up
    gps_time_index, emotion_time_index = time_index_matching_function(gps_times,emotions_time)
    # Stopping the script from running early if there is no time overlap betwen gps and emotions
    if gps_time_index is None and emotion_time_index is None:
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
    hrv_data, hrv_times = get_hrv_data(inputFile['HRV_path'])
    # Time index figuring out now
    gps_hrv_maching_index,hrv_gps_matching_index = time_index_matching_function(gps_times,hrv_times)
    write_hrv = False
    if gps_hrv_maching_index < hrv_gps_matching_index:
        write_hrv = True
    else:
        write_hrv = False

    # Idea is that gps will be device first turned on then emotions will be index 1 and gps will already have written x number of points to shapefile.
    # However, a backup incase audio recording begins first should be coded. Perhaps making it start at the GPS one no matter what.
    if gps_time_index < emotion_time_index:
        is_GPS_first = False
    else:
        is_GPS_first = True
    # if GPS_first == True, then gps_time_index is x and emotion is 1, so an iterative check should be performed until
    # gps_time_index == x then emotion data starts being written
    # if GPS_first == False then emotion_time_index = x and gps_time_index = 1. Therefore, up until x emotions will be cut
    # off in the shapefile

    i = 0
    dict_idx = 0
    sentence_idx = 0

    hrv_writing_idx = hrv_gps_matching_index
    write_sentence = False
    new_sentence = False
    write_emotions = False
    # Opening up csv file to write data into
    # Gonna need to change output location and naming and all of that good stuff
    data_writer = open(r'E:\UNI\Research_assistant\Output results\Shape files\2022 test\collated_data.txt', 'w')
    writer = csv.writer(data_writer)
    with open(inputFile['gps']) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        row_counter = 0
        for row in csv_reader:
            if row[2] == 'record' and row[0] == 'Data' and len(row) > 20:
                #indexes found manually or by using Finding_indexes.py
                position_lat_semi_circles = row[7]
                position_long_semi_circles = row[10]
                speed = row[28]
                distance = row[22]
                altitude = row[16]
                time = row[4]

                if not is_GPS_first:
                    if i == gps_time_index:
                        write_emotions = True
                if is_GPS_first:
                    write_emotions = True

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
                    distance = float(distance)
                    altitude = float(altitude)
                    timestamp = datetime.fromtimestamp(time) # This can output up to date time and year but for this we probably only need hours minutes seconds
                    # print(timestamp.strftime('%M:%S')) #This timestamp comes out as a string, before this conversion it is some sort of time object
                    time_variable = timestamp.strftime('%H:%M:%S')

                    #print(f"The file types is: {type(time_variable)}\n")


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

                    if write_hrv:
                        feature.SetField("HeartRate", hrv_data[hrv_writing_idx][1]) # Probably gonna need some sort of check incase something causes data to end abruptly

                    #Initialising a list to store data to the csv
                    #Converting floating numbers to strings to save a specific number of characters to not bloat the txt file
                    speed_save = "{:.2f}".format(speed)
                    altitude_save = "{:.2f}".format(altitude)
                    distance_save = "{:.3f}".format(distance)
                    csv_data_to_write = [str(time_variable), speed_save, altitude_save, distance_save]

                    if write_emotions:
                        if len(emotions_list) > i:
                            feature.SetField("Emotion", emotions_list[i])  # Not sure this bit right here is correct, indexing could be funky
                            csv_data_to_write.append(emotions_list[i])
                        else:
                            print("No emotions to write here")
                            csv_data_to_write.append(' ')

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
                        if (gps_times[i] == sentences_start_time[sentence_idx]):
                            write_sentence = True
                        if (gps_times[i] == sentences_end_time[sentence_idx]):
                            new_sentence = True
                            write_sentence = False
                        if not write_sentence and not new_sentence:
                            csv_data_to_write.append('N/A')
                        if write_sentence:
                            csv_data_to_write.append(sentences[sentence_idx])
                            feature.SetField("Sentence", sentences[sentence_idx])
                        if new_sentence:
                            csv_data_to_write.append(sentences[sentence_idx])
                            feature.SetField("Sentence", sentences[sentence_idx])
                            sentence_idx = sentence_idx + 1
                            new_sentence = False

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
                    hrv_writing_idx = hrv_writing_idx + 1
                i = i + 1
        data_source = None



#if __name__ == "__main__":
#   analysis()

outputFile = r"E:\UNI\Research_assistant\Output results\Shape files\2022 test"

analysis(inputFile, outputFile)

