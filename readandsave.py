#This function will write and read a log of food. The log of food will be saved as a json file.
import json
#Read a json file and return a dictionary value. If the file does not exists, then return a empty dictionary.
def read(file):
    try:
        with open(file) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    finally:
        print('Data is loaded.')
        return data
#Save a dictionary value as a json file.
def save(data):
    try:
        with open('%s_%s.json'%(data['cat'],data['ty']), 'w') as f:
            f.write(json.dumps(data))
    finally:
        print('Data is saved.')