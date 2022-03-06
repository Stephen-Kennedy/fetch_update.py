#!/usr/bin/python3
# Author Stephen J Kennedy
# Version 1.0
# Auto update script for updating debian/ubuntu with Python
import os
import time
from logging.handlers import SysLogHandler
import logging
import socket

logger = logging.getLogger()
logger.addHandler(SysLogHandler('/dev/log'))
logger.addHandler(logging.FileHandler('/var/log/pyupdate.log'))

# get local machine hostname
local_host = socket.gethostname()

# Checks respositories for available updates, installs upgrades, removes old packages,
# clears local repository of packages that are no longer useful
def auto_update():
  updates = ['update', 'upgrade', 'remove', 'autoclean', 'autoremove']

  for update in updates:
    os.system(f'apt -y {update}')
    logger.warning(f'Running apt {update} on {local_host}.')

# Checks to see if "reboot-required" file exists in /var/run/.
def auto_restart():
  reboot_exists = ""
  if os.path.isfile('/var/run/reboot-required') == True:
     logging.warning(f'***REBOOT required. Rebooting {local_host} now***')
     os.system('shutdown -r now')

  else:
      logging.warning(f'   Update complete on {local_host}.')

auto_update()
auto_restart()