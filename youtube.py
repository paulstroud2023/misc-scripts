#!/usr/bin/python3

# This script is a batch downloader of youtube videos.
# It reads URLs from a text file and 
#   saves all downloaded videos to the download dir
# You can pass up to three arguments:
# - first arg is the url file
# - second is the output dir
# - third is the video resolution

from pytube import YouTube
import datetime
import os
import sys

a = 0  ### global var used in between invocations of progress_tracker()
def progress_tracker(chunk, file_handle, bytes_left):
    ### chunk.filesize is the total size of the file
    ### '\r' allows to overwrite the line instead of printing a new one    
    total = chunk.filesize  ### assign to a var for brevity/readability
    global a
    padding = '.' * (1 + a%3) + ' ' * (2 - a%3)  ### create a 3-char padding string
    print(f"[ Download progress {padding} {round((total - bytes_left) / total * 100)}% ]", end="\r")
    a += 1


### to add:
###     custom output dir ✓
###     custom video resolution ✓
###     pull video list from channel
###     pull subtitles
###     pull audio
###     pass params as CLI arguments ✓
###     save messages to a log file (i.e. "Download OK!") with date in filename, times for msgs


if len(sys.argv) > 1:       # if first arg exists
  url_file = sys.argv[1]    # use it as the URL file
else:   # otherwise, ask user to enter/confirm URL file
  url_file = input(f'Enter the URL file (default = url.txt): ')
  url_file = 'url.txt' if (url_file == "") else url_file  # if nothing entered, use the default filename

default_dir = datetime.datetime.now().strftime("%Y%m%d.%H%M%S") + "_download"

if len(sys.argv) > 2:       # if second arg exists
  output_dir = sys.argv[2]  # use it as the output dir
else:   # otherwise, ask user to enter/confirm dir
  output_dir = input(f'Enter the dir for downloads (default = {default_dir}): ')
  output_dir = default_dir if (output_dir == "") else output_dir  # if nothing entered, use the default dir

  if not os.path.exists(output_dir):
    print(f"Creating a new dir {output_dir}... ", end="")
    os.mkdir(output_dir)
    print("DONE")


video_res = "360p"          # default video resolution
if len(sys.argv) > 3:       # if third arg present
  video_res = sys.argv[3]   # use custom res



### calculate the number of lines in the file
video_total = sum(1 for x in open(url_file, "rt"))
num_padd = len(str(video_total))   ### filename padding for leading 0s

print(">>> STROUD VIDEO DOWNLOADER (v1.0) <<<")
message = f"Parsing {video_total} lines in url.txt..."
print(message)
print("_" * len(message))



bad_char = { '/':',', ':':'-', '"':'', '&':'n', '#':'', '  ':'', '?':' ', '!':' '}

file_number = 0  # var used for filename prefix
error_count = 0  # counter for any errors
file_stream = open(url_file, "rt")

for i in file_stream:   # iterate over the URLs in the file
    file_number += 1       
    ### generate filename prefix
    prefix_str = '[' + str(file_number).zfill(num_padd) + '] '
    
    try:    
        ### create a YouTube object from the URL, use progress_tracker() to display loading %
        video = YouTube((i), on_progress_callback = progress_tracker)
        ### locate the correct video stream using video_res var
        video_stream = video.streams.filter(progressive=True, res = video_res)[0]
        filesize_str = f"{round(video_stream.filesize / (2**20))}MB"
        
        ### filename is sanitized for any rogue characters (i.e. emoji, sys chars, etc)
        clean_filename = video.title.encode('ascii', 'ignore').decode('ascii') + ".mp4"
        clean_filename = video.title + ".mp4"
        
        for i, j in bad_char.items():
            clean_filename = clean_filename.replace(i, j)
        
        print(f"File {prefix_str[1:-2]}/{video_total}: {filesize_str}\t{clean_filename[:50]} ...")

        ### download to file with specified location and name
        ### existing files can be overwritten or not (if matching name)
        video_stream.download(output_path = output_dir, \
                              filename = clean_filename, \
                              filename_prefix = prefix_str, \
                              skip_existing = True, timeout = 10, max_retries = 10)

    except Exception as exc:
        print("Download error! ", exc)
        print(f"Line {prefix_str}: {i}")
        error_count += 1

print("\n\nFinished!")
if (error_count): print(f"(A total of {error_count} errors)")
else: print("(No Errors)")

