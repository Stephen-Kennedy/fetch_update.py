#!/usr/bin/python
#Auto update script for updating debian/ubuntu with Python
import os


def auto_update():
  #checks for available updates in repositories
  os.system('apt update ')

  #If upgrade is available, will prompt user to accept upgrade
  os.system('apt upgrade ')

  #removes old packages that are no longer needed as dependencies
  os.system('apt-get autoremove')

  # Clears out local repository of packages that can no longer be downloaded and are pretty much useless
  os.system('apt-get autoclean')

# Checks to see if the "reboot-required" file exists in /var/run/. If so, the kernel has changed and
# a reboot is required.
def auto_restart():
  reboot_exists = ""
  if os.path.isfile('/var/run/reboot-required') == True:
    restart = raw_input("A restart is required.  Do you want to restart now? (YES/NO)  ")
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
