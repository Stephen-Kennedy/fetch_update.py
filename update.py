#!/usr/bin/python3
# Author: Stephen J Kennedy
# Version: 2.2
# Auto update script for updating Debian/Ubuntu with Python

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

# Hostname
host_name = os.uname()[1]

def run_command(command):
    """Run shell command securely and log output."""
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"Command '{' '.join(command)}' output: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Command '{' '.join(command)}' error: {result.stderr.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command '{' '.join(command)}' failed with return code {e.returncode}. Error: {e.stderr.strip()}")
        return False

def auto_update():
    """Performs system updates and cleans up."""
    commands = [
        ['sudo', 'apt-get', '-y', 'update'],
        ['sudo', 'apt-get', '-y', 'upgrade'],
        ['sudo', 'apt-get', '-y', 'autoremove'],
        ['sudo', 'apt-get', '-y', 'autoclean']
    ]

    for command in commands:
        if run_command(command):
            logger.info(f"Successfully ran {' '.join(command)} on {host_name}")
        else:
            logger.error(f"Failed to run {' '.join(command)} on {host_name}")

    # Pi-hole update check
    if os.path.isfile('/usr/local/bin/pihole'):
        if run_command(['pihole', '-up']):
            logger.info("Successfully updated Pi-hole.")
        else:
            logger.error("Failed to update Pi-hole.")

def auto_restart():
    """Checks if a reboot is required and performs it."""
    if os.path.isfile('/var/run/reboot-required'):
        logger.warning(f"**** REBOOT REQUIRED for host: {host_name}. Rebooting now ****")
        run_command(['sudo', 'reboot'])
    else:
        logger.info(f"Update complete on {host_name}. No reboot required.")

if __name__ == "__main__":
    try:
        auto_update()
        auto_restart()
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
