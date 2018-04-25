import argparse
import sys
import logging
import os
import subprocess
import re
from lxml import etree

SRC_EXTENSIONS = ".mov"

# Instantiate the parser
parser = argparse.ArgumentParser(description="This script generates a wonderstitch batch file for all scenes inside the selected subfolder")
parser.add_argument("directory", type=str, help="Directory with the source footage, sorted by scenes")
parser.add_argument("-c", "--circle", action="store_true", help="Only include circle takes")
parser.add_argument("-p", "--plate-circle", action="store_true", help="Only include circle takes AND plates")
parser.add_argument("-o", "--out", type=str, help="Output xml file name")

args = parser.parse_args()

logger = logging.getLogger('create_wonder_batch.py')
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

def get_take_folders(dir_path, x_filters=[]):
    out_list = []
    logger.debug("Finding takes folders in: " + dir_path)
    if (filter_dir_names(dir_path, [".*take.*"] + x_filters)):
        for file in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file)):
                if re.match(".*" + SRC_EXTENSIONS + "$", file, re.I):
                    out_list += [dir_path]
                    break
            
    for sub_dir in sorted(os.listdir(dir_path)):
        if (os.path.isdir(os.path.join(dir_path, sub_dir))):
            out_list += get_take_folders(os.path.join(dir_path, sub_dir), x_filters)

    return out_list

def get_frame_count(dir_path):
    FRAME_COUNT_CMD = 'mediainfo "--Inform=Video;%FrameCount%" "{}"'
    logger.debug("Getting frame count of videos in folder '{}'".format(dir_path))
    for file in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file)):
            if re.match(".*" + SRC_EXTENSIONS + "$", file, re.I):
                logger.debug(FRAME_COUNT_CMD.format(os.path.join(dir_path, file)))
                output = subprocess.check_output(FRAME_COUNT_CMD.format(os.path.join(dir_path, file)), shell=False)
                output = output.strip().decode('ascii')
                break
    print(output)
    logger.debug("Frame count is {}".format(output))
    if output.isdigit():
        return str(output)
    return "0"
    
dirs_with_files = []
if (args.circle):
    logger.info("Selected --circle option, filtering out non-circle takes")
    dirs_with_files = get_take_folders(args.directory, [".*circle.*"])
elif (args.plate_circle):
    logger.info("Selected --plate-circle option, filtering out non-circle-or-plate takes")
    dirs_with_files = get_take_folders(args.directory, [".*((circle)|(plate)).*"])
else:
    dirs_with_files = get_take_folders(args.directory)

logger.debug("Folders found for processing:" + str(dirs_with_files))

# create XML 
xml = etree.Element("WonderStitch_BatchInfo")
for d in dirs_with_files:
    dir_item = etree.Element("BatchInfo_Item")

    directory = etree.Element("Directory")
    directory.text = os.path.join(d, "")
    dir_item.append(directory)

    start = etree.Element("Start")
    start.text = "0"
    dir_item.append(start)

    end = etree.Element("End")
    end.text = str(get_frame_count(d))
    dir_item.append(end)

    enabled = etree.Element("Enabled")
    enabled.text = "1"
    dir_item.append(enabled)
    
    xml.append(dir_item)

s = etree.tostring(xml, pretty_print=True)

# pretty string
if (args.out):
    f = open(args.out, 'wb')
    f.write(s)
    f.close()
else:
    logger.warning("No output file specificed. Writing XML contents to console.")
    print(s)