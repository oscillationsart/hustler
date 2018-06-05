
import logging

def get_logger(logger_name="", is_debug=False):
  _logger = logging.getLogger(logger_name)
  if is_debug:
    _logger.setLevel(logging.DEBUG)
  # create console handler with a higher log level
  sh = logging.StreamHandler()
  sh.setLevel(logging.DEBUG)
  # create formatter and add it to the handlers
  formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
  sh.setFormatter(formatter)
  # add the handlers to the logger
  _logger.addHandler(sh)
  return _logger
