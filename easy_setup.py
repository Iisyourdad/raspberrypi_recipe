#!/usr/bin/env python3

import os
import subprocess
import shutil
import pwd

# Function to run shell commands
def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e}")
        exit(1)

# Check if running as root
if os.geteuid() != 0:
    print("This script must be run as root!")
    exit(1)

# Ensure user 'tyler' exists
try:
    pwd.getpwnam('tyler')
except KeyError:
    print("Creating user 'tyler'...")
    run_command("useradd -m -s /bin/bash tyler")
    run_command("echo 'tyler:password' | chpasswd")  # Set a default password (change as needed)

# Define paths
home_dir = "/home/tyler"
downloads_dir = os.path.join(home_dir, "Downloads")
project_dir = os.path.join(downloads_dir, "raspberrypi_recipe")
venv_dir = os.path.join(project_dir, "venv")

# Create Downloads directory if it doesn't exist
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)
    run_command(f"chown tyler:tyler {downloads_dir}")

# Clone the repository
if not os.path.exists(project_dir):
    print("Cloning repository...")
    run_command(f"git clone https://github.com/Iisyourdad/raspberrypi_recipe.git {project_dir}")
    run_command(f"chown -R tyler:tyler {project_dir}")

# Set up virtual environment
if not os.path.exists(venv_dir):
    print("Creating virtual environment...")
    run_command(f"python3 -m venv {venv_dir}")

# Install dependencies
print("Installing dependencies...")
pip_cmd = f"{venv_dir}/bin/pip install asgiref Django django-ckeditor django-crispy-forms django-js-asset pillow sqlparse tzdata gunicorn"
run_command(pip_cmd)

# Set hostname
print("Setting hostname to recipes.swestbrook.org...")
run_command("echo 'recipes.swestbrook.org' > /etc/hostname")
run_command("hostname -F /etc/hostname")

# Configure Django to run on 0.0.0.0:80
settings_file = os.path.join(project_dir, "raspberrypi_recipe", "settings.py")
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        settings_content = f.read()
    if "ALLOWED_HOSTS" in settings_content:
        settings_content = settings_content.replace(
            "ALLOWED_HOSTS = []",
            "ALLOWED_HOSTS = ['recipes.swestbrook.org', 'localhost', '0.0.0.0', '127.0.0.1']"
        )
    with open(settings_file, 'w') as f:
        f.write(settings_content)

# Create systemd service for Django server
service_content = """[Unit]
Description=Django Recipe Server
After=network.target

[Service]
ExecStart=/bin/bash -c "cd {0} && git pull && {1}/bin/python manage.py runserver 0.0.0.0:80"
WorkingDirectory={0}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
""".format(project_dir, venv_dir)

service_file = "/etc/systemd/system/recipe_server.service"
with open(service_file, "w") as f:
    f.write(service_content)

print("Enabling Django server service...")
run_command("systemctl daemon-reload")
run_command("systemctl enable recipe_server.service")

# Install required packages for display (lightdm and chromium)
print("Installing lightdm and chromium-browser...")
run_command("apt-get update")
run_command("apt-get install -y lightdm chromium-browser")

# Configure lightdm for autologin
lightdm_conf = "/etc/lightdm/lightdm.conf"
if not os.path.exists(lightdm_conf):
    os.makedirs(os.path.dirname(lightdm_conf), exist_ok=True)
lightdm_content = """[Seat:*]
autologin-user=tyler
autologin-user-timeout=0
user-session=chromium
"""
with open(lightdm_conf, "w") as f:
    f.write(lightdm_content)

# Create custom Chromium session
xsessions_dir = "/usr/share/xsessions"
if not os.path.exists(xsessions_dir):
    os.makedirs(xsessions_dir)
chromium_desktop = os.path.join(xsessions_dir, "chromium.desktop")
chromium_content = """[Desktop Entry]
Name=Chromium Kiosk
Exec=chromium-browser --noerrdialogs --disable-infobars --kiosk http://localhost
Type=Application
"""
with open(chromium_desktop, "w") as f:
    f.write(chromium_content)

# Enable graphical target
print("Enabling graphical target...")
run_command("systemctl set-default graphical.target")

# Ensure permissions
run_command(f"chown -R tyler:tyler {home_dir}")

print("Setup complete! Reboot the Raspberry Pi to start the Django website.")

# Optional: Reboot immediately (uncomment if desired)
# run_command("reboot")