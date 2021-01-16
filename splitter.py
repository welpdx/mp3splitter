#!/usr/bin/env python3
import eyed3
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET
import os
import shutil
'''
Removed unneccesary comments.
Revamped command list creation.
Don't forget to put ffmpeg in folder you welp dumbass!
'''

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
    print("OverDrive MediaMarkers: " , xmltext)
    markers = ET.fromstring(xmltext)
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
        # Replaces characters that misses with complete_segments
        name = name.replace(":", "")
        name = name.replace("/", "_")
        if not name.startswith(base_chapter):
            base_chapter = name
            chapter_section = 0
        # The 00 is ignored if chapter_section == 0. (personal preference: Want names to be as short as possible. I didnt like 00 for every book)
        name = f'{base_chapter}{"_" + str(chapter_section) if chapter_section!=0 else ""}'
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
    # Gives user a warning before deleting existing folder.
    if os.path.exists(subdir):
        input("Folder exists already. Press enter to continue.")
        shutil.rmtree(subdir)
    subdir.mkdir()
    for segment in segments:
        segname = f"{subdir}/{fn.stem}_{segment[0]}{fn.suffix}"
        # GOT IT. It is the command = cmd.split() that split it all based on "spaces". We need to split cmd and add ["ffmpeg", "-i", "asdf123"] in front into command.
        cmd = f"ffmpeg -i -acodec copy -ss {segment[1]} -to {segment[2]}"
        command = cmd.split()
        command.insert(2, filename  )
        command.append( segname   )
        try:
            # ffmpeg requires an output file and so it errors when it does not
            # get one so we need to capture stderr, not stdout.
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
        except Exception as e:
            print("exception", e)
        else:
            for line in output.splitlines():
                print(f"Got line: {line}")

# Get all .mp3 files in current directory
cur_dir =  os.getcwd()
mp3_files = []
for file in os.listdir(cur_dir):
    if file.endswith(".mp3"):
        path=os.path.join(cur_dir, file)
        mp3_files.append(r"{}".format(path))


for filename in mp3_files:
    print(filename)
    end_time, segments = build_segments(filename)
    segments = complete_segments(segments, end_time)
    split_file(filename, segments)
