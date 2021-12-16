import csv
import json
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

# Pulling audio transcription
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
# Loops through and gets a proper timestamp for each of the sentences in the file
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
#print(f"Start times: {adjusted_start_times}\nEnd times: {adjusted_end_times}")
#print(f"Sentences: {sentences}")

#probably gonna need this dictionary to have upper and lower case variants because of how coding works


with open('Dictionary.txt') as dict:
    dict_reader = csv.reader(dict)
    for row in dict_reader:
        dictionary = row


sentences_length = len(sentences)
individual_words_path = 'audio-202111203-individual-words.csv'
times_and_words = []

# audio_start from the sentences file will be used to convert individual words time elapsed to time variable
with open(individual_words_path) as transcribed_words:
    word_reader = csv.reader(transcribed_words)
    for row in word_reader:
        if not row[0].isalnum() and not row[2] == 'alternatives':
            if not row[3] == 'punctuation':
                word_time = float(row[0])
                plus_start = timedelta(seconds = word_time)
                word_time = (audio_start + plus_start).strftime('%H:%M:%S')
                # At the moment the transcript output the words a little annoying in a JSON format: [{'confidence': '0.9677', 'content': 'check'}]
                # i want to have a list with the word and time combined, better than having two separate lists
                json_style = row[2]
                # a lot of hard coding to get it to format the string to json style right but it looks like it works
                json_style = json_style.replace('[', '')
                json_style = json_style.replace(']', '')
                json_style = json_style.replace("': '", '": "')
                json_style = json_style.replace("{'", '{"')
                json_style = json_style.replace("'}", '"}')
                json_style = json_style.replace("', '",'", "')
                json_style = json_style.replace("': ", '": ')
                parsed = json.loads(json_style)
                time_and_word_temp = [word_time, parsed["content"]]
                times_and_words.append(time_and_word_temp)



# Now want to loop through all of the dictionary words as well as the words individual words to find the exact time they occur at
# Cycle through all words as main loop and then dictionary as secondary
#probably going to need a counter for indexing
dict_words_used_with_times = []
index = 0
dict_length = len(dictionary)
dict_index = 0 # Dict index is a reference to which dictionary word is found for categorisation in the shape file
for words in times_and_words:
    current_word = words[1]
    while dict_index < dict_length: #might need to turn this into a for loop for iterational index counting
        dict_word_length = str(dictionary[dict_index])
        dict_word_length = len(dict_word_length)
        current_word_length = len(current_word)
        # checking to see if the words are the same length alleviates the correct word within a longer word issue
        if current_word in dictionary[dict_index] and current_word_length == dict_word_length:
            info_saving = [times_and_words[index][0],dictionary[dict_index], dict_index]
            dict_words_used_with_times.append(info_saving)
        dict_index = dict_index + 1
    dict_index = 0
    index = index + 1

print(f"Dictionary words used and when + number index representation:\n{dict_words_used_with_times}")


