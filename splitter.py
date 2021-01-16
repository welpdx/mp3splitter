#!/usr/bin/env python3
import eyed3
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET
import os
import shutil

def convert_time(time_secs):
    fraction = int((time_secs % 1) * 1000)
    seconds = int(time_secs)
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return f"{hour:02}:{min:02}:{sec:02}.{fraction:03}"

def build_segments(filename):
    audio = eyed3.load(filename)
    end_time = convert_time(audio.info.time_secs)
    x = audio.tag.user_text_frames
    xmltext = x.get("OverDrive MediaMarkers").text
    print("xml before: " , xmltext)
    xmltext = xmltext.replace(" ", "")
    #xmltext = xmltext.replace(":", "")
    print("xml after: " , xmltext)
    markers = ET.fromstring(xmltext)
    #print(markers)
    #markers = markers.replace(" ", "_")
    #print("m2 :", markers)
    base_chapter = "invalid I hope I never have chapters like this"
    chapter_section = 0
    segments = []
    for marker in markers:
        # chapters can be split into several shorter sections and end up being
        # shown like this:
        #    Chapter 1         00:00.000
        #    Chapter 1 (03:21) 03:21.507
        #    Chapter 1 (06:27) 06:27.227
        #  Use the chapter name with a counter to create:
        #    Chapter 1-00      00:00.000
        #    Chapter 1-01      03:21.507
        #    Chapter 1-02      06:27.227
        name = marker[0].text.strip()
        # Not the place to filter our the whitespace
        #print(name)
        #name = name.replace(" ", "")
        name = name.replace(":", "")
        print("name: " , name)
        if not name.startswith(base_chapter):
            base_chapter = name
            chapter_section = 0
        name = f"{base_chapter}_{chapter_section:02}"
        chapter_section += 1
        start_time =  marker[1].text
        name = name.replace(" ", "_")
        segments.append((name, start_time))
    return end_time, segments


def complete_segments(segments, final_time):
    new_segments = []
    for index, segment in enumerate(segments):
        if index < len(segments) - 1:
            end_time = segments[index+1][1]
        else:
            end_time = final_time
        new_segments.append((segment[0], segment[1], end_time))
        print((segment[0], segment[1], end_time))
    return new_segments

def split_file(filename, segments):
    fn = pathlib.Path(filename)
    subdir = pathlib.Path(fn.stem)
    if os.path.exists(subdir):
        input("Folder exists already. Press enter to continue.")
        shutil.rmtree(subdir)
    subdir.mkdir()
    for segment in segments:
        segname = f"{subdir}/{fn.stem}_{segment[0]}{fn.suffix}"
        cmd = f"ffmpeg -i {filename} -acodec copy -ss {segment[1]} -to {segment[2]} {segname}"
        command = cmd.split()
        try:
            # ffmpeg requires an output file and so it errors when it does not
            # get one so we need to capture stderr, not stdout.
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
        except Exception as e:
            print("exception", e)
        else:
            for line in output.splitlines():
                print(f"Got line: {line}")


cur_dir = os.getcwd()
mp3_files = []
for file in os.listdir(cur_dir):
    if file.endswith(".mp3"):
        mp3_files.append(os.path.join(cur_dir, file))


m = []
m.append(mp3_files[-1])
print(m)


for filename in m:
    print(filename)
    end_time, segments = build_segments(filename)
    segments = complete_segments(segments, end_time)
    split_file(filename, segments)
