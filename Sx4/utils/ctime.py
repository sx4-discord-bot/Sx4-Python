import discord

def convert(time: str):
    times = time.split(" ")
    seconds = 0
    for x in times:
        if x.endswith("s"):
            seconds += int(x[:-1])
        elif x.endswith("m"):
            seconds += int(x[:-1]) * 60
        elif x.endswith("h"):
            seconds += int(x[:-1]) * 3600
        elif x.endswith("d"):
            seconds += int(x[:-1]) * 86400
        elif x.isdigit():
            seconds += int(x)
        else:
            pass
    return seconds