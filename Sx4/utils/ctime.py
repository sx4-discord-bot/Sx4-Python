import discord

def convert(time: str):
    times = time.split(" ")
    seconds = 0
    for x in times:
        if x.lower().endswith("s"):
            seconds += int(x[:-1])
        elif x.lower().endswith("m"):
            seconds += int(x[:-1]) * 60
        elif x.lower().endswith("h"):
            seconds += int(x[:-1]) * 3600
        elif x.lower().endswith("d"):
            seconds += int(x[:-1]) * 86400
        elif x.isdigit():
            seconds += int(x)
        else:
            pass
    return seconds
