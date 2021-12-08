import csv
import datetime


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
    return gps_index, video_index


# Best to turn both of these csv reading code blocks into functions
with open(r"face_video_frames_dominant_emotions.txt") as emotions:
    emotions_reader = csv.reader(emotions, delimiter=",")
    counter = 0
    for row in emotions_reader:
        if counter == 0:
            emotions_list = row
            counter = counter + 1
        else:
            emotions_time = row

print(f"List of emotions: {emotions_list}\nTime of emotions: {emotions_time}\n")
gps_times = []
with open(r"video timing test (29-11-2021).csv") as bike_gps:
    gps_reader = csv.reader(bike_gps, delimiter=',')
    for i in gps_reader:
        if i[2] == 'record' and i[0] == 'Data' and len(i) > 20:
            gps_rows = i
            time = float(i[4])
            time = datetime.datetime.fromtimestamp(time)
            time = str(time.strftime('%H:%M:%S'))
            gps_times.append(time)
print(gps_times)

gps_index, video_index = time_index_matching_function(gps_times,emotions_time)

print(f"The GPS index is: {gps_index} The video index is: {video_index}\n")
print(f"To prove these numbers a test shall be performed. GPS:{gps_times[32]} and video: {emotions_time[10]}")


