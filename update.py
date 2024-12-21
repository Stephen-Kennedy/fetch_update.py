#!/usr/bin/python3
# Author: Stephen J Kennedy
# Version: 2.4
# Auto update script for Debian/Ubuntu with email notifications using local Postfix.

import subprocess
import os
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
import smtplib
from email.mime.text import MIMEText

# Configure Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File Handler with rotation
file_handler = RotatingFileHandler('/var/log/pyupdate.log', maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Syslog Handler
syslog_handler = SysLogHandler(address='/dev/log')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)

# Email Configuration
FROM_EMAIL = os.getenv('FROM_EMAIL', 'default@domain.com')
TO_EMAIL = os.getenv('TO_EMAIL', 'default@domain.com')

# Hostname
host_name = os.uname()[1]

def send_email(subject: str, body: str):
    """Send email notification using local Postfix."""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL

        with smtplib.SMTP('localhost') as server:
            server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())
        logger.info(f"Email notification sent: {subject}")
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email: {str(e)}")


def run_command(command: list[str]) -> str | None:
    """Run shell command securely and log output."""
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"Command '{' '.join(command)}' output: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Command '{' '.join(command)}' error: {result.stderr.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command '{' '.join(command)}' failed with return code {e.returncode}. Error: {e.stderr.strip()}")
        return None

def auto_update():
    """Performs system updates and cleans up."""
    command = ['sudo', 'sh', '-c', 'apt-get -y update && apt-get -y upgrade && apt-get -y autoremove && apt-get -y autoclean']
    update_output = run_command(command)

    if update_output:
        send_email(
            subject=f"Update Notification from {host_name}",
            body=f"System updates performed on {host_name}:\n\n{update_output}"
        )
    # Check if a distribution upgrade is available
    dist_upgrade_output = run_command(['sudo', 'apt-get', '-s', 'dist-upgrade'])
    if dist_upgrade_output and "upgraded," in dist_upgrade_output:
        send_email(
            subject=f"Distribution Upgrade Available on {host_name}",
            body=f"A distribution upgrade is available on {host_name}. Manual intervention is required.\n\nOutput:\n{dist_upgrade_output}"
        )

def auto_restart():
    """Checks if a reboot is required and performs it."""
    if os.path.isfile('/var/run/reboot-required'):
        send_email(
            subject=f"Reboot Required for {host_name}",
            body=f"A reboot is required on {host_name} after recent updates. Rebooting now."
        )
        logger.warning(f"**** REBOOT REQUIRED for host: {host_name}. Rebooting now ****")
        run_command(['sudo', 'reboot'])
    else:
        logger.info(f"Update complete on {host_name}. No reboot required.")
        send_email(
            subject=f"Update Complete on {host_name}",
            body=f"The update process is complete on {host_name}. No reboot was required."
        )

if __name__ == "__main__":
    try:
        auto_update()
        auto_restart()
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        send_email(
            subject=f"Error in Update Script on {host_name}",
            body=f"An error occurred during the update process on {host_name}. Check the logs for details.\n\nError: {str(e)}"
        )
