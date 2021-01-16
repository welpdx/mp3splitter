#!/usr/bin/env python3
import eyed3
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET
import os
import shutil
'''
Added code to do the following:
 - Check if ffmpeg is in directory.
 - Replace invalid characters in markers, so files can be created ni windows env
 - Added Special Case 1. If there's only one output file, just rename that one
      file to book name
 - Changed some variable names
 - Output all in a single folder! subdir = bookname
 - Output file naming now: {num_seq}_{marker information}_({bookname}).mp3
                       ie: 08_Screwtape_Proposes_a_Toast_(Some_Everyday_Thoughts)

Todo:
    1. A better way to customize file names? We got segment[0] from
        build_segments() and the rest in split_file()
'''

# Sequential number in beginnging (displays mp3 output files in order)
num_seq = 0

# For Special Case 1.
is_SingleInputFile = False
is_SingleOutputFile = False

# Converts time (in secs) to a hh:mm:ss.### format
def convert_time(time_secs):
    fraction = int((time_secs % 1) * 1000)
    seconds = int(time_secs)
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return f"{hour:02}:{min:02}:{sec:02}.{fraction:03}"

# Get OverDrive MediaMarkers, seperates each marker with it's time.
def build_segments(mp3file_path):
    audio = eyed3.load(mp3file_path)
    end_time = convert_time(audio.info.time_secs)
    x = audio.tag.user_text_frames
    xmltext = x.get("OverDrive MediaMarkers").text
    print("OverDrive MediaMarkers: " , xmltext)
    markers = ET.fromstring(xmltext)

    # init
    global num_seq
    global is_SingleInputFile
    global is_SingleOutputFile
    segments = []

    # (Special Case 1) If only 1 marker and if only 1 file, it is a single output file
    if (len(markers) == 1 and is_SingleInputFile == True) :
        is_SingleOutputFile = True


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


        # FILE NAME FORMAT For Last Half of the : _#_<filename>    NamingTag
        name = f'{num_seq:02d} {name}'

        # Replaces characters that are prohibited in Windows File Name Conventions
        name = name.replace(":", "-")
        name = name.replace("/", "_")
        name = name.replace('"', "")
        # Changes spaces to underscore.  (Personal preference)
        name = name.replace("  ", "_")  # Double Spaces converts to Single underscore first.
        name = name.replace(" ", "_")   # Then Single Spaces to single underscore

        num_seq += 1
        start_time =  marker[1].text
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


def split_file(mp3file_path, segment, bookname):

    # Init.
    global is_SingleOutputFile

    fn = pathlib.Path(mp3file_path)

    subdir = bookname

    # Remove Spaces in bookname, Which if the first part of the final file name
    bookname = bookname.replace("  ", "_")  # Double Spaces converts to Single underscore first.
    bookname = bookname.replace(" ", "_")   # Then Single Spaces to single underscore


    for segment in segments:

        if is_SingleOutputFile == True :
            segname = f"{subdir}/{bookname}{fn.suffix}" # Special Case 1.
        else:
            # FILE NAME FORMAT: {num_seq}_{marker information}_({bookname}).mp3    NamingTag
            segname = f"{subdir}/{segment[0]}_({bookname}){fn.suffix}"

        cmd = f"ffmpeg -i -acodec copy -ss {segment[1]} -to {segment[2]}"

        command = cmd.split()
        command.insert(2, mp3file_path  )
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

# Check if ffmpeg is in directory.
def isffmpeg(dir):
    if os.path.exists('ffmpeg.exe'):
        return True
    else:
        return False

# Special Case 1
def isOnly1ItemInList(list):
    if len(list) == 1:
        return True
    else:
        return False


# Get Current directory path
cur_dir =  os.getcwd()

# Check if ffmpeg in current directory. Exits if ffmpeg is not found.
if (isffmpeg(cur_dir) is False):
    print("Please put ffmpeg.exe in current directory")
    sys.exit()

# Get all .mp3s in folder
mp3paths_list = []
for file in os.listdir(cur_dir):
    if file.endswith(".mp3"):
        path=os.path.join(cur_dir, file)
        mp3paths_list.append(r"{}".format(path))
print("mp3 file list : \n", mp3paths_list)

# Create Single Directory For all mp3.
bookname = mp3paths_list[1]
bookname = pathlib.Path(bookname)
bookname = bookname.stem
bookname = bookname[:-7]
print("Bookname :", bookname)
subdir = pathlib.Path(bookname)

# Check if bookname subdirectory has already been created.
if os.path.exists(subdir):
    input("Folder exists already. Press enter to delete.")
    shutil.rmtree(subdir)
    print("subdir exists. Subdir deleted and new subdir created.")
    subdir.mkdir()
else:
    subdir.mkdir()


for mp3file_path in mp3paths_list:
    end_time, segments = build_segments(mp3file_path)
    segments = complete_segments(segments, end_time)

    # For Special Case 1. Check if there is only one file.
    if (isOnly1ItemInList(mp3paths_list) == True):
        is_SingleInputFile = True
        
    split_file(mp3file_path, segments, bookname)
