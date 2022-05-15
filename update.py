#!/usr/bin/python3
# Author Stephen J Kennedy
# Version 2.0
# Auto update script for updating debian/ubuntu with Python
import os
import time
from logging.handlers import SysLogHandler
import logging
import socket

logger = logging.getLogger()
logger.addHandler(SysLogHandler('/dev/log'))
logger.addHandler(logging.FileHandler('/var/log/pyupdate.log'))

host_name = socket.gethostname()

# Checks respositories for available updates, installs upgrades, removes old packages,
# clears local repository of packages that are no longer useful
def auto_update():
    updates = ['update', 'upgrade', 'remove', 'autoclean', 'autoremove']

    for update in updates:
        os.system(f'apt -y {update}')
        logger.warning(f'Running apt {update} on {host_name}.')

    if os.path.isfile('/usr/local/bin/pihole'):
        piupdate()

# checks for update to pihole
def piupdate ():
    os.system('pihole -up')
    logger.warning(f'Running pihole update on {host_name}. ')

# Checks to see if "reboot-required" file exists in /var/run/.
def auto_restart():
    reboot_exists = ""
    if os.path.isfile('/var/run/reboot-required') == True:
        logger.warning(f"**** REBOOT REQUIRED for host: {host_name}. Rebooting now ****")
        os.system('reboot')

    else:
        logging.warning(f'**** Update complete on {host_name}.')

auto_update()
auto_restart()