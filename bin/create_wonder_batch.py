import argparse
import sys
import logging
import os
import subprocess
import re
from lxml import etree
import hustler.helpers.DirCrawler as DirCrawler
import hustler.helpers.MediaInfo as MediaInfo

SRC_EXTENSIONS = "mov"

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

def get_frame_count(dir_path):
  for f in DirCrawler.get_files(dir_path, [".*\." + SRC_EXTENSIONS + "$"]):
    return MediaInfo.get_frame_count(f)
  return "0"
  
dirs_with_files = []
if (args.circle):
  logger.info("Selected --circle option, filtering out non-circle takes")
  dirs_with_files = DirCrawler.get_dirs(args.directory, [".*circle.*"])
elif (args.plate_circle):
  logger.info("Selected --plate-circle option, filtering out non-circle-or-plate takes")
  dirs_with_files = DirCrawler.get_dirs(args.directory, [".*((circle)|(plate)).*"])
else:
  dirs_with_files = DirCrawler.get_dirs(args.directory)

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