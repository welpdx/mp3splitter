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
Added function to check if ffmpeg is in directory.

'''

# Converts time (in secs) to a hh:mm:ss.### format
def convert_time(time_secs):
    fraction = int((time_secs % 1) * 1000)
    seconds = int(time_secs)
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return f"{hour:02}:{min:02}:{sec:02}.{fraction:03}"

# Get OverDrive MediaMarkers, seperates each marker with it's time.
def build_segments(filename):
    audio = eyed3.load(filename)
    end_time = convert_time(audio.info.time_secs)
    x = audio.tag.user_text_frames
    xmltext = x.get("OverDrive MediaMarkers").text
    print("OverDrive MediaMarkers: " , xmltext)
    markers = ET.fromstring(xmltext)
    base_chapter = "invalid I hope I never have chapters like this"
    num_seq = 0
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
        # Replaces characters that are prohibited in Windows File Name Conventions
        name = name.replace(":", "-")
        name = name.replace("/", "_")
        if not name.startswith(base_chapter):
            base_chapter = name

        # if num_seq != 0 show 0
        name = f'{"_" + (str(num_seq) if num_seq!=0 else "0") + "_"   }{base_chapter}'
        num_seq += 1
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
    print("filename: ", filename)
    fn = pathlib.Path(filename)
    fname = fn.stem
    # removes last 11 digits. inclding
    fname = fname[:-7]
    subdir = pathlib.Path(fname)
    # Gives user a warning before deleting existing folder.
    if os.path.exists(subdir):
        # input("Folder exists already. Press enter to continue.")
        shutil.rmtree(subdir)
    else:
        subdir.mkdir()

    print("subdir: ",subdir)
    for segment in segments:
        print("segments: ",segments)
        print("segment: ",segment)

        segname = f"{subdir}/{fname}_{segment[0]}{fn.suffix}"
        print("segname: ",segname)
        # GOT IT. It is the command = cmd.split() that split it all based on "spaces". We need to split cmd and add ["ffmpeg", "-i", "asdf123"] in front into command.
        cmd = f"ffmpeg -i -acodec copy -ss {segment[1]} -to {segment[2]}"
        command = cmd.split()
        command.insert(2, filename  )
        command.append( segname   )

        print("command: ",command)
        print("segment[1]: " + segment[1] + "segment[2]: " + segment[2] + "segname: " +  segname)
        try:
            # ffmpeg requires an output file and so it errors when it does not
            # get one so we need to capture stderr, not stdout.
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
        except Exception as e:
            print("exception", e)
        else:
            for line in output.splitlines():
                print(f"Got line: {line}")

def isffmpeg(dir):
    if os.path.exists('ffmpeg.exe'):
        return True
    else:
        return False

# Get Current directory path
cur_dir =  os.getcwd()

# Check if ffmpeg in current directory. Exits script if ffmpeg is not found in current dir.
if (isffmpeg(cur_dir) is False):
    print("Please put ffmpeg.exe in current directory")
    sys.exit()


mp3_files_list = []
for file in os.listdir(cur_dir):
    if file.endswith(".mp3"):
        path=os.path.join(cur_dir, file)
        mp3_files_list.append(r"{}".format(path))

print("mp3 file list : \n", mp3_files_list)


for filename in mp3_files_list:
    print(filename)
    end_time, segments = build_segments(filename)
    segments = complete_segments(segments, end_time)
    split_file(filename, segments)
