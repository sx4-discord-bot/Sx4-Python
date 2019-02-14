import discord
from datetime import datetime, timedelta

def get(timestamp):
    m, s = divmod(timestamp, 60) 
    h, m = divmod(m, 60) 
    d, h = divmod(h, 24) 
    w, d = divmod(d, 7)
    M, w = divmod(w, 4.345238095238096)
    y, M = divmod(M, 12)
    time_str = ""
    if y:
        time_str += "%d year%s " % (y, "" if y == 1 else "s")
    if M:
        time_str += "%d month%s " % (M, "" if M == 1 else "s")
    if w >= 1:
        time_str += "%d week%s " % (w, "" if w == 1 else "s")
    if d:
        time_str += "%d day%s " % (d, "" if d == 1 else "s")
    if h:
        time_str += "%d hour%s " % (h, "" if h == 1 else "s")
    if m:
        time_str += "%d minute%s " % (m, "" if m == 1 else "s")
    if s:
        time_str += "%d second%s " % (s, "" if s >= 1 and s < 2 else "s")
    return time_str[:-1]
