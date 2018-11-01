import discord
from datetime import datetime, timedelta

def get(timestamp):
    m, s = divmod(timestamp, 60) 
    h, m = divmod(m, 60) 
    d, h = divmod(h, 24) 
    w, d = divmod(d, 7)
    M, w = divmod(w, 4.348214285714286)
    y, M = divmod(M, 12)
    if y == 0 and M == 0 and w == 0 and d == 0 and h == 0 and m == 0:
        return "%d second%s" % (s, "" if s == 0 else "s")
    elif y == 0 and M == 0 and w == 0 and d == 0 and h == 0:
        return "%d minute%s %d second%s" % (m, "" if m == 1 else "s", s, "" if s == 1 else "s")
    elif y == 0 and M == 0 and w == 0 and d == 0:
        return "%d hour%s %d minute%s %d second%s" % (h, "" if h == 1 else "s", m, "" if m == 1 else "s", s, "" if s == 1 else "s")
    elif y == 0 and M == 0 and w == 0:
        return "%d day%s %d hour%s %d minute%s %d second%s" % (d, "" if d == 1 else "s", h, "" if h == 1 else "s", m, "" if m == 1 else "s", s, "" if s == 1 else "s")
    elif y == 0 and M == 0:
        return "%d week%s %d day%s %d hour%s %d minute%s %d second%s" % (w, "" if w == 1 else "s", d, "" if d == 1 else "s", h, "" if h == 1 else "s", m, "" if m == 1 else "s", s, "" if s == 1 else "s")
    elif y == 0:
        return "%d month%s %d week%s %d day%s %d hour%s %d minute%s %d second%s" % (M, "" if M == 1 else "s", w, "" if w == 1 else "s", d, "" if d == 1 else "s", h, "" if h == 1 else "s", m, "" if m == 1 else "s", s, "" if s == 1 else "s")
    else:
        return "%d year%s %d month%s %d week%s %d day%s %d hour%s %d minute%s %d second%s" % (y, "" if y == 1 else "s", M, "" if M == 1 else "s", w, "" if w == 1 else "s", d, "" if d == 1 else "s", h, "" if h == 1 else "s", m, "" if m == 1 else "s", s, "" if s == 1 else "s")
