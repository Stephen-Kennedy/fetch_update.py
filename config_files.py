#!/usr/bin/python3
# Author Stephen J Kennedy
# Version 1.1
# Script to check for and update the most current installs

import filecmp
import logging
import os
import subprocess
from logging.handlers import SysLogHandler
from tempfile import NamedTemporaryFile

# Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = SysLogHandler('/dev/log')
file_handler = logging.FileHandler('/var/log/pyupdate.log')
logger.addHandler(handler)
logger.addHandler(file_handler)

github_path = 'https://raw.githubusercontent.com/Stephen-Kennedy/fetch_update/master/'
current_directory = os.getcwd()


def run_command(command):
    """ Utility function to run a shell command. """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return None


def get_update_list():
    """ Get the most current list file from the GitHub fetch_update master and update files. """
    file_list_name = 'file_list.txt'
    file_list_url = f'{github_path}{file_list_name}'

    with NamedTemporaryFile(delete=False) as tmp_file:
        run_command(f'wget -O {tmp_file.name} {file_list_url}')
        with open(tmp_file.name, 'r') as file:
            file_list = file.read().splitlines()
        os.unlink(tmp_file.name)

    custom_files_to_update(file_list)


def custom_files_to_update(files):
    """ Checks and updates files based on the list from GitHub. """
    for file in files:
        file_name = os.path.basename(file)
        new_file_path = os.path.join(current_directory, file_name)

        if run_command(f'wget -O {new_file_path} {github_path}{file_name}') is not None:
            if os.path.isfile(file) and not filecmp.cmp(file, new_file_path):
                run_command(f'cp {new_file_path} {file}')
                logger.info(f'Updated file from GitHub: {file}')
            os.unlink(new_file_path)


get_update_list()
