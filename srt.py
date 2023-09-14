# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 19:23:00 2023

@author: thiesesh
"""

from datetime import timedelta, datetime

# Some handy functions

# Convert number to color hex code
def to_hex(num):
    return "#" + hex(num)[2:8]

# Format time in milliseconds to seconds
def format_time(millis):
    """ Format time in HH:MM:SS,MMM format """
    seconds, remainder = divmod(millis, 1000)
    
    delta = timedelta(seconds = seconds, milliseconds = remainder)
    
    time_component = datetime(1, 1, 1) + delta
    my_time = time_component.time()
    result = my_time.strftime("%H:%M:%S") + f",{my_time.microsecond // 1000:03d}"
    
    return result

# Format text, if required
def format_text(adict, fmt):
    """ Format text with color, underline, italic """
    raw_text = ": ".join([adict[x] for x in ["role", "content"] if len(adict[x]) > 0])
    
    if fmt:
        formatted_text = raw_text
        if adict["italic"]:
            formatted_text = f"<i>{formatted_text}</i>"
        if adict["underline"]:
            formatted_text = f"<u>{formatted_text}</u>"
        if adict["color"]:
            color = adict["color"]
            formatted_text = f'<font color="{color}">{formatted_text}</font>'
    else:
        formatted_text = raw_text
    
    return formatted_text

def transform(subs_raw):
    """ Format time and tansform color to hex """
    subs_out = list()
    for entry in subs_raw:
        new_entry = entry.copy()
        new_entry["start_time"] = format_time(new_entry["start_time"])
        new_entry["end_time"] = format_time(new_entry["end_time"])
        new_entry["color"] = to_hex(new_entry["color"])
        subs_out.append(new_entry)
    return subs_out

def to_srt(subs_raw, fmt):
    """ Dictionary to srt format """
    subs_out = list()
    
    for num, entry in enumerate(subs_raw):
        text = format_text(entry, fmt)
        entry = f"""{num}
{entry["start_time"]} --> {entry["end_time"]}
{text}""" 
        subs_out.append(entry) 
    
    return "\n\n".join(subs_out)

def to_table(subs):
    """ Transform subs to list that is suitable to write as csv """
    table = list()
    cols = ["role", "content", "start_time", "end_time",
            "color", "italic", "underline"]
    
    for entry in subs:
        row = [entry.get(col, "") for col in cols]
        table.append(row)
    
    return table