import argparse
import sys
import logging
import os
import subprocess
import re

SRC_EXTENSION = ".mp4"
LOG_EXTENSION = ".log"

# Instantiate the parser
parser = argparse.ArgumentParser(description="This script renames and/or creates links for WonderStitch batch outputs ")
parser.add_argument("directory", type=str, help="Directory with the outputs from WonderStitch batch")
parser.add_argument("-r", "--rename", action="store_true", help="Rename output video files")
parser.add_argument("-l", "--links", type=str, help="Folder path where symlinks would be created. Folder will be created if it doesn't exist. WARNING: requires root on Windows.")

args = parser.parse_args()

logger = logging.getLogger('organize_batch_stitches.py')
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

def get_stitch_folders(dir_path, x_filters=[]):
    out_list = []
    logger.debug("Finding stitch folders in: " + dir_path)
    for file in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file)):
            if re.match(".*" + LOG_EXTENSION + "$", file, re.I):
                out_list += [dir_path]
                break

    for sub_dir in sorted(os.listdir(dir_path)):
        if (os.path.isdir(os.path.join(dir_path, sub_dir))):
            out_list += get_stitch_folders(os.path.join(dir_path, sub_dir), x_filters)

    return out_list

def get_good_name(dir_path):
    logger.debug("Getting good name for videos in folder '{}'".format(dir_path))
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            if re.match(".*" + LOG_EXTENSION + "$", file, re.I):
                logger.debug("Found log file:" + file_path)
                file_contents = open(file_path).readlines()[1:3]
                INPUT_PATTERN = ".*(Roll \d[^\r\n]+).*"
                n1 = re.match(INPUT_PATTERN, file_contents[0]).group(1).replace(os.sep, " - ")
                FRAMES_PATTERN = "\d+"
                n2, n3 = re.findall(FRAMES_PATTERN, file_contents[1])
                return (n1 + "fr_" + n2 + "_" + n3)


dirs_to_process = get_stitch_folders(args.directory)

if (args.rename):
    logger.info("Renaming all {} files in each folder to meaningful names".format(SRC_EXTENSION))
if (args.links):
    logger.info("Creating links in: " + args.links)
    os.makedirs(args.links, exist_ok=True)
for d in dirs_to_process:
    logger.debug("Processing folder:" + str(d))
    count = 0
    good_name = get_good_name(d)
    for f in os.listdir(d):
        if re.match(".*" + SRC_EXTENSION + "$", f, re.I):
            f_path = os.path.join(d, f)
            if (args.rename):
                new_path = os.path.join(d, good_name)
                if (count>0):
                    new_path += " ({})".format(count+1)
                os.rename(f_path, new_path + SRC_EXTENSION)
                f_path = new_path
            if (args.links):
                link_path = os.path.join(args.links, good_name)
                if (count>0):
                    link_path += " ({})".format(count+1)
                os.symlink(f_path, link_path + SRC_EXTENSION)
            count += 1
