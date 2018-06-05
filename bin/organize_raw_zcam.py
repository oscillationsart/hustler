import argparse
import re
import sys
import os
import subprocess
import glob
import hustler.helpers.Logger as Logger
import hustler.helpers.DirCrawler as DirCrawler
import hustler.helpers.MediaInfo as MediaInfo

SRC_EXTENSIONS = "mov"

CAM_DIRS = ["CamA.*", "CamB.*", "CamC.*", "CamD.*", "CamE.*", "CamF.*", "CamG.*", "CamH.*", "CamI.*"]
MAX_LENGTH = 100500

# Instantiate the parser
parser = argparse.ArgumentParser(description="This script renames and/or creates links for WonderStitch batch outputs ")
parser.add_argument("input", type=str, help="Directory with the input folders from Z Cam")
parser.add_argument("out", type=str, nargs='?', default="", help="Directory for organized output files")
parser.add_argument("-t", "--test", action="store_true", help="Test input files and not do any organizing. Works best with ommitted 'out' argument")

args = parser.parse_args()

logger = Logger.get_logger("organize_raw_zcam", True)

def index_files(directory):
  all_files = {}
  cam_number = 0
  # Indexing all files
  for cam in CAM_DIRS:
    cam_dirs = DirCrawler.get_dirs(dir_path=directory, name_filters=[cam], include_current_dir=False, depth=1)
    logger.debug("Found matches for {} search:".format(cam), cam_dirs)
    if (cam_dirs.count != 1):
      logger.warning("Expecting exactly one directory for the camera. Found {}".format(cam_dirs.count))
    else:
      cam_files = DirCrawler.get_files(cam_dirs[0], name_filters=[".*\." + SRC_EXTENSIONS])
      all_files[cam_number] = cam_files
    cam_number += 1
  return all_files

def test_input(directory):
  errors = 0
  all_files = index_files(directory)
  # Confirming that all files match by name and have non-zero size
  for cam_number in all_files.keys:
    if (cam_number>0):
      expected_files = [os.path.basename(f).replace("_0000_", "_000{}_".format(cam_number)) for f in all_files[0]]
      actual_files = [os.path.basename(f) for f in all_files[cam_number]]
      
      missing_files = set(expected_files) - set(actual_files)
      if (missing_files.count > 0):
        logger.warning("Camera {} doesnt have the following files: {}".format(cam_number, missing_files))
      unexpected_files = set(actual_files) - set(expected_files)
      if (unexpected_files.count > 0):
        logger.warning("Camera {} has the following unexpected files: {}".format(cam_number, unexpected_files))
    for f in all_files[cam_number]:
      if (os.path.getsize(f) < 1000):
        logger.warning("File {} has zero size!".format(f))

  return(errors)
    
def create_sorted_structure(directory, output=""):
  errors = 0
  if (output == ""):
    output = dir
  all_files = index_files(directory)
  for cam in all_files.keys:
    take_count = 1
    for cam_file in all_files[cam]:
      cam_file_name = os.path.basename(cam_file)
      folder_name = os.path.join(output, "take {}".format(take_count))
      os.makedirs(folder_name, exist_ok=True)
      os.symlink(cam_file, os.path.join(folder_name, cam_file_name))
      frames = MediaInfo.get_frame_count(cam_file)
      frames_reference
      if (cam == 0):
        frames_reference = frames
        if (frames != -1):
          f = open(os.path.join(folder_name, "0-{}.frames".format(frames)),"w+")
          f.close()
      else:
        if (frames != frames_reference):
          errors += 1
          logger.warning("File {} has {} frames, but reference is {}".format(cam_file_name, frames, frames_reference))
  return(errors)

if (args.test):
  test_out = test_input(args.input)
  sys.exit(test_out)
else:
  sort_out = create_sorted_structure(args.input, args.out)
  sys.exit(sort_out)