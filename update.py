#!/usr/bin/python3
# Author Stephen J Kennedy
# Version 1.0
# Auto update script for updating debian/ubuntu with Python
import os
import time

def auto_update():
  updates = ['update', 'upgrade', 'autoremove', 'autoclean']

  # Checks respositories for available updates, installs upgrades, removes old packages,
  # clears local repository of packages that are no longer useful
  for update in updates:
    os.system('apt-get -y %s' % (update))

# Checks to see if "reboot-required" file exists in /var/run/.
def auto_restart():
  reboot_exists = ""
  if os.path.isfile('/var/run/reboot-required') == True:
    restart = input("A restart is required.  Do you want to restart now? (YES/NO)  ")
    restart = str.strip(restart)
    if restart.lower() in ('yes', 'y'):
      print("Restarting....")
      os.system('shutdown -r now')
    elif restart.lower() in ('no', 'n'):
      print("Exiting without restart")
    else:
      print("Sorry, I did not understand you. Exiting...")
      return
  else:
    print("No reboot required.")

auto_update()
auto_restart()
