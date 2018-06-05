import argparse
import sys
import logging
import os
import subprocess
import re

SRC_EXTENSIONS = "(mov)|(mp4)"
FFMPEG_TIMECODE_NVIDIA_CMD = 'ffmpeg  -hwaccel cuvid -c:v h264_cuvid -i "{}" -c:v h264_nvenc -preset fast -vf "drawtext=fontfile=DroidSansMono.ttf: timecode=00\:00\:00\:00: r=29.97: x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000099" -y "{}"'
FFMPEG_TIMECODE_CPU_CMD = 'ffmpeg -i "{infile}" -c:v libx264 -b:v 30M -preset fast -vf "drawtext=fontfile=\'{fontfile}\': text=\'{filename}\\ \\ %{{n}}\\ \\ \':x=(w-tw)/2: y=h-(2*lh)-80: fontsize=70: fontcolor=white: box=1: boxcolor=0x00000099, drawtext=fontfile=\'{fontfile}\': timecode=\'00\\:00\\:00\\:00\': r=29.97: x=(w-tw)/2: y=h-(2*lh): fontsize=70: fontcolor=white: box=1: boxcolor=0x00000099" -y "{outfile}"'

FONT_FILE = os.path.join(os.path.dirname(__file__), "..", "lib", "DroidSansMono.ttf")
# FFMPEG_TIMECODE_CPU_CMD = 'ffmpeg -i "{}" -c:v libx264 -b:v 30M -preset fast -vf "drawtext=fontfile=DroidSansMono.ttf: timecode=00\:00\:00\:00: r=29.97: x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000099" -y "{}"'

# Instantiate the parser
parser = argparse.ArgumentParser(description="This script burns in timecode information in the file around nadir, so that it's easy to identify which part of the file requires higher quality stitching")
parser.add_argument("input", type=str, help="Either a video file or a directory with video files")
parser.add_argument("-p", "--in-place", action="store_true", help="Owerwrites source files with timecode-embedded files")
parser.add_argument("-o", "--out", type=str, help="Output filename or directory name. If ommitted, new file(s) are created next to input file(s)")

args = parser.parse_args()

logger = logging.getLogger('burn_in_timecodes.py')
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)

def filter_dir_names(dir_path, filters):
  dir_name = os.path.basename(dir_path)
  for f in filters:
    if (not re.match(f, dir_name, re.I)):
      return False
  return True

"""
This method returns a list of folders in a tree that match all the regex filters passed,
starting with the current folder.
Iterate through the resulting list to process the folders or their files.
"""
def get_dirs(dir_path, name_filters=[], path_filters=[], include_current_dir=True):
  out_list = []
  logger.debug("Filtering folders in: '{}' using the filters for name:{} and path:{} ".format(dir_path, name_filters, path_filters))

  dir_name = os.path.basename(dir_path)
  if (include_current_dir):
    for filter in name_filters:
      if (not re.match(filter, dir_name, re.I)):
        include_current_dir = False
        break
  if (include_current_dir):
    for filter in path_filters:
      if (not re.match(filter, dir_path, re.I)):
        include_current_dir = False
        break
  if (include_current_dir and os.path.isdir(dir_path)):
    out_list = [dir_path]

  for sub_dir in sorted(os.listdir(dir_path)):
    if (os.path.isdir(os.path.join(dir_path, sub_dir))):
      out_list += get_dirs(os.path.join(dir_path, sub_dir), name_filters, path_filters, True)

  return out_list

"""
This method returns a list of files which names match all the regex filters passed. Combine with get_dirs for recursive processing of directories.
"""
def get_files(dir_path, name_filters=[]):
  out_list = []
  logger.debug("Filtering files in: '{}' using filters for name:{}".format(dir_path, name_filters))

  for f in sorted(os.listdir(dir_path)):
    include_f = True
    if (os.path.isfile(os.path.join(dir_path, f))):
      for filter in name_filters:
        logger.debug("Testing filter {} on file {}".format(filter, f))
        if (not re.match(filter, f, re.I)):
          logger.debug("Filter fail")
          include_f = False
          break
      if (include_f):
        logger.debug("This file will work!")
        out_list += [os.path.join(dir_path, f)]
  return out_list

for directory in get_dirs(args.input):
  logger.debug("processing folder: {}".format(directory))
  for f in get_files(directory, [".*\.({})$".format(SRC_EXTENSIONS)]):
    logger.debug("processing file: {}".format(f))
    f_name = os.path.basename(f)
    if (args.in_place):
      logger.info("Specified --in-place option. Removing original file once timecode burn in is done.")
      tempname = os.path.join(directory, "src_{}".format(f_name))
      os.rename(f, tempname)
      infile = tempname
      outfile_name = f
    else:
      infile = f
      outfile_name = "tc_{}".format(f_name)
    outfile = os.path.join(directory, outfile_name)
    CMD = FFMPEG_TIMECODE_CPU_CMD.format(infile=f, outfile=outfile, fontfile=FONT_FILE, filename=f_name)
    logger.debug("Running command: {}".format(CMD))
    try:
      output = subprocess.check_output(CMD, shell=True)
    except subprocess.CalledProcessError as grepexc:
      logger.error("ffmpeg run failed with code: {}. Output: {}".format(grepexc.returncode, grepexc.output))
    else:
      logger.info("Successfully embedded timecode in {}".format(f))
      output = output.strip().decode('ascii')
      logger.debug("Burn in output is: {}".format(output))

logger.info("All done!")