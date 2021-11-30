import json
import csv
import string

with open('asrSentences.txt') as file:
    data = file.readlines()
    i = 0 #iterator for the rows
    x = len(data)
    tem_line = data[0][0:]

    print(tem_line[102])

    #print(f"error is at: {tem_line[60:75]}\n")
    while i < x:
        temp_line = data[i][0:]
        temp_line = temp_line.replace("':",'":')
        temp_line = temp_line.replace("{'",'{"')
        temp_line = temp_line.replace("':", '":')
        temp_line = temp_line.replace(", '",', "')
        temp_line = temp_line.replace(": '", ': "')
        temp_line = temp_line.replace("',",'",')
        #temp_line = temp_line.replace("}",'},')
        data[i] = temp_line
        i = i + 1

    i = 0
    with open('doubleQuoteText.txt', 'w') as file:
        while i < x:
            file.write(data[i][0:]) # use `json.loads` to do the reverse
            #file.write("\n")
            i = i + 1
    file.close()
