# update.py version to auto-update, to include pihole, via cronjob
import os
from logging.handlers import SysLogHandler
import logging

logger = logging.getLogger()
logger.addHandler(SysLogHandler('/dev/log'))
logger.addHandler(logging.FileHandler('/var/log/pyupdate.log'))

def auto_update():
    updates = ['update', 'upgrade', 'remove', 'autoclean']

    # Checks respositories for available updates, installs upgrades, removes old packages,
    # clears local repository of packages that are no longer useful
    for update in updates:
        os.system(f'apt -y {update}')
        logger.warning(f'Running apt {update}')

# checks for update to pihole
def piupdate ():
    os.system('pihole -up')
    logger.warning('Running pihole update.')

# Checks to see if "reboot-required" file exists in /var/run/.
def auto_restart():
    #reboot_exists = ""
    if os.path.isfile('/var/run/reboot-required') == True:
        logger.warning("*** REBOOT REQUIRED ***")
        os.system('shutdown -r now')

    else:
        logger.warning(' Update complete.')

auto_update()
piupdate()
auto_restart()