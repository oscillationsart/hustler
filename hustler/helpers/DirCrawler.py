import os
import re
import hustler.helpers.Logger as Logger

logger = Logger.get_logger("DirCrawler", True)

def get_dirs(dir_path, name_filters=[], path_filters=[], include_current_dir=True, depth=-1):
  """
  This method returns a list of folders in a tree that match all the regex filters passed,
  starting with the current folder.
  Iterate through the resulting list to process the folders or their files.
  Use "-1" for maximum depth, 0 for current dir only
  """
  out_list = []
  logger.debug("Filtering folders in: '{}' using the filters for name:{} and path:{} ".format(dir_path, name_filters, path_filters))

  dir_name = os.path.basename(dir_path)
  if include_current_dir:
    for filter in name_filters:
      if not re.match(filter, dir_name, re.I):
        include_current_dir = False
        break
  if include_current_dir:
    for filter in path_filters:
      if not re.match(filter, dir_path, re.I):
        include_current_dir = False
        break
  if include_current_dir and os.path.isdir(dir_path):
    out_list = [dir_path]

  if depth!=0:
    for sub_dir in sorted(os.listdir(dir_path)):
      if (os.path.isdir(os.path.join(dir_path, sub_dir))):
        out_list += get_dirs(
          dir_path = os.path.join(dir_path, sub_dir), 
          name_filters = name_filters, 
          path_filters = path_filters, 
          include_current_dir = True, 
          depth = depth-1)

  return out_list

"""
This method returns a list of files which names match all the regex filters passed. Combine with get_dirs for recursive processing of directories.
"""
def get_files(dir_path, name_filters=[]):
  out_list = []
  logger.debug("Filtering files in: '{}' using filters for name:{}".format(dir_path, name_filters))

  for f in sorted(os.listdir(dir_path)):
    include_f = True
    if os.path.isfile(os.path.join(dir_path, f)):
      for filter in name_filters:
        logger.debug("Testing filter {} on file {}".format(filter, f))
        if not re.match(filter, f, re.I):
          logger.debug("Filter fail")
          include_f = False
          break
      if include_f:
        logger.debug("This file will work!")
        out_list += [os.path.join(dir_path, f)]
  return out_list
