#!/usr/bin/python3
# Author: Stephen J Kennedy
# Version: 3.5
# Auto update script for Debian/Ubuntu with email notifications using local Postfix.

import subprocess
import os
import logging
from logging.handlers import RotatingFileHandler
import smtplib
from email.mime.text import MIMEText

# Ensure pip is installed
try:
    subprocess.run(['pip', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
except (FileNotFoundError, subprocess.CalledProcessError):
    print("pip not found, attempting to install pip...")
    subprocess.run(['sudo', 'apt-get', 'update'], check=True)
    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-pip'], check=True)

# Check for dotenv and install if missing
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    subprocess.run(['pip', 'install', 'python-dotenv'], check=True)
    from dotenv import load_dotenv

# Load environment variables from .env file
ENV_FILE = '/etc/postfix/env_variables.env'
if not os.path.exists(ENV_FILE):
    raise FileNotFoundError(f"Environment file {ENV_FILE} not found. Please create it with the required variables.")
load_dotenv(ENV_FILE)

# Configure Logging
LOG_FILE = "/var/log/pyupdate.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Email Configuration from environment variables
FROM_EMAIL = os.getenv('FROM_EMAIL', 'default@domain.com')
TO_EMAIL = os.getenv('TO_EMAIL', 'default@domain.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'localhost')

# Hostname
host_name = os.uname()[1]

def send_email(subject, body):
    """Send email notification using local Postfix or specified SMTP server."""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL

        with smtplib.SMTP(SMTP_SERVER) as server:
            server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())
        logger.info(f"Email notification sent: {subject}")
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email: {str(e)}")

def run_command(command):
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
    commands = [
        ['sudo', 'apt-get', '-y', 'update'],
        ['sudo', 'apt-get', '-y', 'upgrade'],
        ['sudo', 'apt-get', '-y', 'autoremove'],
        ['sudo', 'apt-get', '-y', 'autoclean']
    ]

    updates_performed = []
    for command in commands:
        result = run_command(command)
        if result is not None:
            updates_performed.append(' '.join(command))
        else:
            logger.error(f"Failed to run {' '.join(command)} on {host_name}")

    if updates_performed:
        send_email(
            subject=f"Update Notification from {host_name}",
            body=f"The following updates were performed on {host_name}:\n\n" + '\n'.join(updates_performed)
        )

    # Check if a distribution upgrade is available
    dist_upgrade_output = run_command(['sudo', 'apt-get', '-s', 'dist-upgrade'])
    if dist_upgrade_output and "The following packages will be upgraded:" in dist_upgrade_output:
        send_email(
            subject=f"Distribution Upgrade Available on {host_name}",
            body=f"A distribution upgrade is available on {host_name}. Manual intervention is required.\n\nOutput:\n{dist_upgrade_output}"
        )
    else:
        logger.info("No distribution upgrades available.")

def auto_restart():
    """Checks if a reboot is required and performs it."""
    if os.path.isfile('/var/run/reboot-required'):
        send_email(
            subject=f"Reboot Required for {host_name}",
            body=f"A reboot is required on {host_name} after recent updates. Rebooting now."
        )
        logger.warning(f"**** REBOOT REQUIRED for host: {host_name}. Rebooting now ****")
        try:
            run_command(['sudo', 'reboot'])
        except Exception as e:
            logger.critical(f"Failed to reboot: {str(e)}")
            send_email(
                subject=f"Reboot Failed on {host_name}",
                body=f"A reboot was required on {host_name}, but it failed. Manual intervention is required.\n\nError: {str(e)}"
            )
    else:
        logger.info(f"Update complete on {host_name}. No reboot required.")
        send_email(
            subject=f"Update Complete on {host_name}",
            body=f"The update process is complete on {host_name}. No reboot was required."
        )

def test_smtp_connection():
    """Test SMTP server connection."""
    try:
        with smtplib.SMTP(SMTP_SERVER) as server:
            server.noop()
        logger.info(f"SMTP server {SMTP_SERVER} is reachable.")
    except Exception as e:
        logger.error(f"SMTP server {SMTP_SERVER} is unreachable: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        test_smtp_connection()
        auto_update()
        auto_restart()
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        send_email(
            subject=f"Error in Update Script on {host_name}",
            body=f"An error occurred during the update process on {host_name}. Check the logs for details.\n\nError: {str(e)}"
        )
