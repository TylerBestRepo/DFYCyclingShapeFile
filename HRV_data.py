import csv
import datetime

# Best to turn both of these csv reading code blocks into functions
HRV_path = 'eSense Pulse data from 09.12.21 11_42_14.csv'

#Format for this CSV is:
#   time elapsed; heart rate measurement; RR interval (dunno what this is); RR interval in ms; HRV amplitude; regularity; timestamp; marker;
# I dont know which data bits we want but ill have some commented stuff in it that can be changed easily

def get_hrv_data(hrv_path):
    hrv_data = []
    with open(HRV_path) as hrv:
        hrv_reader = csv.reader(hrv, delimiter=";")
        for row in hrv_reader:

            #print(f"Length = {len(row)}")
            if not row[0].isalnum():
                # print(f"Cool beans man this is the output row: {row}")
                if not row[0] == '':
                    #print(f"is this the row thats gonna fuck it? {row}")
                    row_test = row[0][0]
                    if not row_test.isalpha():
                        print(f"ayyy")
                        row = row.replace(";;", ';')
                        #hrv_data.append(float(row[0]))
                        #hrv_data.append('\n')
                        temp = float(row[0])
                        #need to find a way to ignore the empty things where in the csv there is ";;"
                        hrv_data.append(temp)
                        hrv_data.append('\n')

    return hrv_data


hrv_data = get_hrv_data(HRV_path[0])
print(f"all the data saved that we want: {hrv_data}")


