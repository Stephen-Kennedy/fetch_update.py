#!/usr/bin/python3
# Author: Stephen J Kennedy
# Version: 3.9
# Auto update script for Debian/Ubuntu with Gmail SMTP relay support, including Pi-hole.

import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import smtplib
from email.mime.text import MIMEText

# Configuration
LOG_FILE = "/var/log/pyupdate.log"
ENV_FILE = "/etc/postfix/env_variables.env"
REQUIRED_ENV_VARS = ['FROM_EMAIL', 'TO_EMAIL', 'SMTP_SERVER', 'EMAIL_PASSWORD']

# Configure logging
logger = logging.getLogger("update_script")
logger.setLevel(logging.DEBUG)  # Use DEBUG for testing, INFO for production
handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Hostname
host_name = os.uname()[1]

def load_env_variables():
    """Load environment variables from ENV_FILE."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as env_file:
            return dict(line.strip().split("=", 1) for line in env_file if "=" in line)
    else:
        logger.critical(f"Environment file {ENV_FILE} not found.")
        raise FileNotFoundError(f"Environment file {ENV_FILE} not found.")

def validate_env_variables(env_vars):
    """Ensure required environment variables are present."""
    for var in REQUIRED_ENV_VARS:
        if var not in env_vars or not env_vars[var]:
            logger.critical(f"Environment variable {var} is missing or empty.")
            raise EnvironmentError(f"Missing required environment variable: {var}")

def send_email(subject, body):
    """Send email notification using Gmail SMTP relay."""
    try:
        env_vars = load_env_variables()
        validate_env_variables(env_vars)

        FROM_EMAIL = env_vars['FROM_EMAIL']
        TO_EMAIL = env_vars['TO_EMAIL']
        SMTP_SERVER = env_vars['SMTP_SERVER']
        EMAIL_PASSWORD = env_vars['EMAIL_PASSWORD']

        # Compose and send email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL

        with smtplib.SMTP(SMTP_SERVER, 587) as server:
            server.ehlo()  # Identify with the SMTP server
            server.starttls()  # Enable TLS
            server.ehlo()  # Re-identify after TLS
            server.login(FROM_EMAIL, EMAIL_PASSWORD)  # Authenticate
            server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())

        logger.info(f"Email notification sent: {subject}")
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email: {str(e)}")
    except Exception as e:
        logger.error(f"General error while sending email: {str(e)}")

def run_command(command, timeout=600):
    """Run shell command securely and log output."""
    try:
        env = os.environ.copy()
        env["DEBIAN_FRONTEND"] = "noninteractive"
        result = subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            env=env,
            stdin=subprocess.DEVNULL,  # Suppress input prompts
            timeout=timeout  # Set timeout to prevent indefinite hangs
        )
        logger.info(f"Command executed successfully: {' '.join(command)}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out: {' '.join(command)} | Timeout: {timeout}s")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)} | Exit Code: {e.returncode} | Error: {e.stderr.strip()}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during command execution: {' '.join(command)} | Error: {str(e)}")
        raise

def auto_update():
    """Perform system updates and clean-up."""
    commands = [
        ['apt-get', '-y', 'update'],
        ['apt-get', '-y', 'upgrade'],
        ['apt-get', '-y', 'autoremove'],
        ['apt-get', '-y', 'autoclean']
    ]

    updates_performed = []
    for command in commands:
        try:
            result = run_command(command)
            if result:
                updates_performed.append(' '.join(command))
        except Exception as e:
            logger.error(f"Failed to run {' '.join(command)}: {str(e)}")

    if updates_performed:
        send_email(
            subject=f"Update Notification from {host_name}",
            body=f"The following updates were performed on {host_name}:\n\n" + '\n'.join(updates_performed)
        )
    else:
        logger.info("No updates were performed.")

def check_pihole_installation():
    """Check if Pi-hole is installed by verifying the executable's existence."""
    possible_paths = ['/usr/local/bin/pihole', '/usr/bin/pihole']
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            logger.info(f"Pi-hole found at {path}")
            return True
    logger.info("Pi-hole is not installed.")
    return False

def update_pihole():
    """Update Pi-hole to the latest version if installed."""
    possible_paths = ['/usr/local/bin/pihole', '/usr/bin/pihole']
    pihole_path = None

    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            pihole_path = path
            break

    if pihole_path:
        try:
            # Run the Pi-hole update command and log output to the update log
            logger.info(f"Running Pi-hole update using {pihole_path}")
            result = run_command([pihole_path, '-up'], timeout=300)
            
            # Log the result to the logger
            logger.info(f"Pi-hole update completed successfully:\n{result}")
            send_email(
                subject=f"Pi-hole Update Completed on {host_name}",
                body=f"Pi-hole was updated successfully on {host_name}.\n\nOutput:\n{result}"
            )
        except subprocess.TimeoutExpired as e:
            logger.error(f"Pi-hole update timed out: {str(e)}")
            send_email(
                subject=f"Pi-hole Update Timed Out on {host_name}",
                body=f"The Pi-hole update process on {host_name} timed out after 300 seconds. Please check manually."
            )
        except Exception as e:
            logger.error(f"Failed to update Pi-hole: {str(e)}")
            send_email(
                subject=f"Pi-hole Update Failed on {host_name}",
                body=f"An error occurred while updating Pi-hole on {host_name}.\n\nError: {str(e)}"
            )
    else:
        logger.info("Pi-hole is not installed. No update performed.")

def check_distribution_upgrade():
    """Check if a distribution upgrade is available and send a notification."""
    try:
        dist_upgrade_output = run_command(['apt-get', '-s', 'dist-upgrade'])
        if "The following packages will be upgraded:" in dist_upgrade_output:
            send_email(
                subject=f"Distribution Upgrade Available on {host_name}",
                body=f"A distribution upgrade is available on {host_name}. Manual intervention is required.\n\n"
                     f"Output:\n{dist_upgrade_output}"
            )
            logger.info("Distribution upgrade notification sent.")
        else:
            logger.info("No distribution upgrades available.")
    except Exception as e:
        logger.error(f"Failed to check for distribution upgrade: {str(e)}")

def auto_restart():
    """Check if a reboot is required and perform it."""
    if os.path.isfile('/var/run/reboot-required'):
        send_email(
            subject=f"Reboot Required for {host_name}",
            body=f"A reboot is required on {host_name} after recent updates. Rebooting now."
        )
        try:
            run_command(['reboot'])
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

def main():
    """Main function to execute the update and upgrade checks."""
    try:
        auto_update()
        update_pihole()  # Check for and update Pi-hole if installed
        check_distribution_upgrade()
        auto_restart()
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        send_email(
            subject=f"Error in Update Script on {host_name}",
            body=f"An error occurred during the update process on {host_name}. Check the logs for details.\n\nError: {str(e)}"
        )

if __name__ == "__main__":
    main()
