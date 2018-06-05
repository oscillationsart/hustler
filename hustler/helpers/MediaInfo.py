import os
import subprocess
import hustler.helpers.Logger as Logger

logger = Logger.get_logger("MediaInfo", True)

"""
This method returns frame count of the file
"""
def get_frame_count(video_file):
  FRAME_COUNT_CMD = 'mediainfo "--Inform=Video;%FrameCount%" "{}"'
  logger.debug("Getting frame count of the file '{}'".format(video_file))
  out = -1
  if os.path.isfile(video_file):
    output = subprocess.check_output(FRAME_COUNT_CMD.format(video_file), shell=False)
    output = output.strip().decode('ascii')
    if output.isdigit():
      out = output
  return out
  