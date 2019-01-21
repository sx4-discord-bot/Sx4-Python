import json
import os

class FileAlreadyExists(Exception):
    pass

def read_json(file):
    with open(file, "r") as f:
        return json.loads(f.read())

def write_json(file, data: dict):
    with open(file, "w") as f:
        f.write(json.dumps(data))

def file_exists(file):
    return os.path.isfile(file)

def create_file(file, data: dict={}):
    if file_exists(file):
        raise FileAlreadyExists("That file already exists, use write_json to update the file")
    else:
        with open(file, "w") as f:
            f.write(json.dumps(data))



    