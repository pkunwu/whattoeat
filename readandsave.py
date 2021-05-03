#This function will write and read a log of food. The log of food will be saved as a json file.
import json
#Read a json file and return a dictionary value. If the file does not exists, then return a empty dictionary.
def read(file):
    try:
        with open(file) as f:
            data = json.load(f)
            f.close()
    except FileNotFoundError:
        data = {}
    return data
#Save a dictionary value as a json file.
def save(data,file):
    f = open(file, 'w')
    f.write(json.dunps(data))
    f.close()    