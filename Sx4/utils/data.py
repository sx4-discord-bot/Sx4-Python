import discord
import json

def read_json(file):
    with open(file, "rb") as f:
        jsonobj = json.loads(f.read().decode())
    return jsonobj