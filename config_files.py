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

# get current custom file list from Github
file_list_name = 'filelist.txt'
os.system(f'wget {github_path}/{file_list_name}')

# custom files to maintain
get_my_file_list = open(f'{current_directory}/{file_list_name}','r')
set_file_list = get_my_file_list.split("\n")
get_my_file_list.close()
                    
def custom_files_to_update():

                        

    """ Checks to see if file from custom_file exists on current system. If so, downloads
    current Github version and compares current file to newly downloaded version.  If the files
    do not match, replace existing file with new version. """
    for file in custom_files:
        if os.path.isfile(f'{file}'):
            get_file_name = os.path.basename(file)
            #  set file name from file path to facilitate download of github content
            f1 = (f'{current_directory}/{get_file_name}')
            f2 = (f'{file}')
            print(f1)
            print(f2)

            os.system(f'wget {github_path}{get_file_name}')

            if not filecmp.cmp(f1, f2):
                os.system(f'cp {f1} {f2}')
                logger.warning(f'*** New file configurations on Github. ***')
            else:
                logger.warning(f'*** No new configurations to install from Github ***')

            os.system(f'rm {f1}')

custom_files_to_update()
