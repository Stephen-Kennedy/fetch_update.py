#!/usr/bin/python3
# Author Stephen J Kennedy
# Version 2.1
# Auto update script for updating debian/ubuntu with Python

import subprocess
import os
import logging
from logging.handlers import SysLogHandler

# Configure Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('/var/log/pyupdate.log')
file_handler.setFormatter(formatter)
syslog_handler = SysLogHandler(address='/dev/log')
syslog_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(syslog_handler)

host_name = os.uname()[1]

def run_command(command):
    """ Run shell command and log output. """
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return False

def auto_update():
    """ Performs system updates and cleans up. """
    updates = ['update', 'upgrade', 'autoremove', 'autoclean']

    for update in updates:
        if run_command(f'apt-get -y {update}'):
            logger.info(f'Successfully ran apt-get {update} on {host_name}')
        else:
            logger.error(f'Failed to run apt-get {update} on {host_name}')

    if os.path.isfile('/usr/local/bin/pihole'):
        if run_command('pihole -up'):
            logger.info('Successfully updated pihole.')
        else:
            logger.error('Failed to update pihole.')

def auto_restart():
    """ Checks if a reboot is required and performs it. """
    if os.path.isfile('/var/run/reboot-required'):
        logger.warning(f"**** REBOOT REQUIRED for host: {host_name}. Rebooting now ****")
        run_command('reboot')
    else:
        logger.info(f'Update complete on {host_name}. No reboot required.')

if __name__ == "__main__":
    auto_update()
    auto_restart()
