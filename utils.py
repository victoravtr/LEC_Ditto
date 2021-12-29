""" Common functions """
from logging.handlers import RotatingFileHandler
import os
import sys
import json
import math
import pickle
import logging
from datetime import datetime


logging.basicConfig(handlers=[RotatingFileHandler('data/log.txt', maxBytes=524288, backupCount=10)],
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def get_file_content(path):
    """ Reads a file and returns its content.

    Args:
        path (str): path to the file

    Returns:
        str: content of the file. False if the file does not exist.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ''
    except Exception:
        LOGGER.error(exception_info(sys.exc_info()))
        sys.exit(1)

def get_json_content(path):
    """ Reads a json file and returns its content.

    Args:
        path (str): path to the file

    Returns:
        json: content of the file. False if the file does not exist.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return False


def save_json_content(path, content):
    """ Saves a json file with the given content.

    Args:
        path (str): path to the file
        content (dict): content to be saved
    """
    try:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(content, file)
    except Exception:
        LOGGER.error(exception_info(sys.exc_info()))
        sys.exit(1)


def get_pickle_content(path):
    """ Reads a pickle file and returns its content.

    Args:
        path (str): path to the file

    Returns:
        pickle: content of the file. Empty array if the file does not exist.
    """
    try:
        with open(path, 'rb') as file:
            pickle_content = pickle.load(file)
        return pickle_content
    except (FileNotFoundError, EOFError):
        return []


def save_pickle_content(path, content):
    """ Saves a pickle file with the given content.

    Args:
        path (str): path to the file
        content (dict): content to be saved
    """
    try:
        with open(path, 'wb') as file:
            pickle.dump(content, file)
    except Exception:
        LOGGER.error(exception_info(sys.exc_info()))
        sys.exit(1)


def epoch_to_datetime(epoch):
    """ Converts an epoch to a datetime object.

    Args:
        epoch (str): epoch to be converted

    Returns:
        datetime: datetime object
    """
    return datetime.fromtimestamp(epoch)


def get_seconds_remaining(epoch):
    """ Calculates the seconds remaining until the given epoch.

    Args:
        epoch (str): epoch to be converted

    Returns:
        int: seconds remaining
    """
    return math.ceil((epoch_to_datetime(int(epoch)) - datetime.now()).total_seconds())

def exception_info(sys_info):
    """ Returns a string with the exception information.

    Args:
        sys_info (tuple): sys.exc_info()

    Returns:
        str: exception information
    """
    exc_type, exc_value, exc_traceback = sys_info

    exception_name = exc_type.__name__
    filename = os.path.split(exc_traceback.tb_frame.f_code.co_filename)[1]
    line_number = exc_traceback.tb_lineno
    function_name = exc_traceback.tb_frame.f_code.co_name
    value = exc_value

    return f"{exception_name} while executing {filename}:{function_name} at line {line_number}: {value}"
