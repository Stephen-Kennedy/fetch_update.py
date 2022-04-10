#!/usr/bin/python3
# Author Stephen J Kennedy
# Version 1.0
# Script to check for and update most current installs
import os
import socket
import filecmp
import logging
from logging.handlers import SysLogHandler

logger = logging.getLogger()
logger.addHandler(SysLogHandler('/dev/log'))
logger.addHandler(logging.FileHandler('/var/log/pyupdate.log'))

github_path = 'https://raw.githubusercontent.com/Stephen-Kennedy/fetch_update/master/'
current_directory = os.getcwd()

def get_update_list():
    """ Get the most current list file from the Github fetch_update master. Read the txt file
    into a list for custom_files_to_update(). After processing custom_file_to_update() remove
    temp_file_list"""

    file_list_name = 'file_list.txt'
    get_file_list = (f'{github_path}{file_list_name}')
    os.system(f'wget {get_file_list}')

    temp_file_list = (f'{current_directory}/{file_list_name}')
    with open (f'{temp_file_list}') as file:
        file_list = file.read().splitlines()

    custom_files_to_update(file_list)
    os.system(f'rm {temp_file_list}')

def custom_files_to_update(files):
    """ Checks to see if file from custom_file exists on current system. If so, downloads
    current Github version and compares current file to newly downloaded version.  If the files
    do not match, replace existing file with new version. """

    for file in files:
        get_file_name = os.path.basename(file)
        os.system(f'wget {github_path}{get_file_name}')
        existing_file = (f'{file}')
        new_file = (f'{current_directory}/{get_file_name}')

        if os.path.isfile(file):
            existing_file = (f'{file}')

            if not filecmp.cmp(existing_file, new_file):
                os.system(f'cp {new_file} {existing_file}')
                logger.warning(f'*** New file configurations on Github. ***')
        else:
            os.system(f'cp {new_file} {file}')

        os.system(f'rm {new_file}')

get_update_list()
