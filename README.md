
Forked from [Jim Anderson](https://twitter.com/jimande75053775)! See his repo [here](https://github.com/jima80525/mp3splitter). This brilliant idea and HUGE amount of code is from him. I'm just adding my own preferences and spin onto it.

# MP3 Chapter Splitter

This utility reads the headers of MP3 audiobook files and splits them according to the information found in the tags. It is currently written to split files that are downloaded from the Overdrive service from our library.


# What this script does
1. Gathers all mp3 files in the script's current directory.
2. Using OverDrive Markers, split all mp3 files according to it's chapter.
Naming starts with a number (to keep it in order), then the chapter name (from the marker), then the book name.
3. Creates a subfolder named after the book. All output mp3 files goes here.

# How do I use?

![see this](https://i.imgur.com/0RNtVhg.gif)
1. Copy ffmpeg and splitter.py into directory.
2. Run splitter.py

# Dependencies
1. Python >= 3.6
2. [eyed3](https://pypi.org/project/eyed3/)
In cmd, do:
>pip install eyed3


## Differences with Jim's script

 - Check if ffmpeg is in directory.
 - Replace invalid characters in markers, so files can be created ni windows env
 - Added Special Case 1. If there's only one output file, just rename that one file to book name
 - Changed some variable names
 - Output all in a single folder! subdir = bookname
 - Output file naming now: {num_seq}_{marker information}_({bookname}).mp3
                       ie: 08_Screwtape_Proposes_a_Toast_(Some_Everyday_Thoughts)


## Other notes
The project is currently in the "userful tool for me" stage and has not been tested beyond seeing that it works on the files I needed splitting.  
If you're interested in more features or have a file it doesn't work with, send me a note or create an issue and I'll see what I can do!
