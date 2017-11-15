#!/usr/bin/python
#Auto update script for updating debian/ubuntu with Python
import os
import time

def auto_update():
  updates = ['update', 'upgrade', 'autoremove', 'autoclean']

  # Checks respositories for available updates, installs upgrades, removes old packages,
  # clears local repository of packages that are no longer useful
  for update in updates:
    os.system('apt -y %s' % (update))

def install_default():
  programs = ['vim', 'dnsutils', 'ccze', 'iftop', 'htop']
  for program in programs:
    print("Installing %s " % program)
    os.system('apt-get install -y %s' % (program))

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
install_default()
auto_restart()
