import os
import platform
from datetime import datetime

def creation_date(path_to_file):
    return os.path.getmtime(path_to_file)


print("ahoy there")

creation = creation_date(r"20211128_153515.mp4")
#creation = float(creation)
timestamp = datetime.fromtimestamp(creation).strftime('%H:%M:%S')

#time_variable = creation.strftime('%H:%M:%S')
print(f"Creation = {timestamp}\n")
#print(f"The file type is: {type(timestamp)}\n")

#converting it to a string now as QGIS cant interpret datetime variable types
strTimeStamp = str(timestamp)


#To compare different times could test if the minutes align and then test if the seconds are within a ranger after that if successful
tester = '15:35:11'

hour_comp_1 = strTimeStamp[3:4]
hour_comp_2 = tester[3:4]

if hour_comp_1 == hour_comp_2:
    print("Hours are the same")
    min_comp_1 = float(strTimeStamp[6:7])
    min_comp_2 = float(tester[6:7])
    if abs(min_comp_1 - min_comp_2) < 2:
        print("Seconds are also within the range")


