import os
import subprocess
import sys

REPO_DIR = "/home/pi/raspberrypi_recipe-main"
PROJECT_DIR = os.path.join(REPO_DIR, "westbrook_recipes")
VENV_DIR = os.path.join(PROJECT_DIR, "venv")
REQUIREMENTS_FILE = os.path.join(PROJECT_DIR, "requirements.txt")
SERVICE_FILE = "/etc/systemd/system/django.service"
AUTOSTART_DIR = "/home/pi/.config/lxsession/LXDE-pi"
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, "autostart")
KIOSK_LINE = "@chromium-browser --kiosk http://127.0.0.1:8000/\n"

def run_command(cmd, cwd=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(1)

def update_repo():
    print("Updating repository with latest changes...")
    # Change directory to the repository root and pull updates
    run_command("git pull", cwd=REPO_DIR)

def update_system():
    run_command("apt-get update -y")
    run_command("apt-get upgrade -y")
    run_command("apt-get install -y git python3-pip python3-venv chromium-browser")

def clone_repo():
    if not os.path.exists(REPO_DIR):
        run_command(f"git clone https://github.com/Iisyourdad/raspberrypi_recipe.git {REPO_DIR}")
    else:
        print(f"Repository already exists at {REPO_DIR}.")
        update_repo()

def setup_virtualenv():
    os.chdir(PROJECT_DIR)
    if not os.path.exists(VENV_DIR):
        run_command("python3 -m venv venv")
    run_command(f"{VENV_DIR}/bin/pip install --upgrade pip")
    run_command(f"{VENV_DIR}/bin/pip install -r {REQUIREMENTS_FILE}")

def create_systemd_service():
    service_content = f"""[Unit]
Description=Django Development Server
After=network.target

[Service]
User=pi
WorkingDirectory={PROJECT_DIR}
ExecStart={VENV_DIR}/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
    try:
        with open(SERVICE_FILE, "w") as f:
            f.write(service_content)
        print(f"Created systemd service file at {SERVICE_FILE}")
    except Exception as e:
        print(f"Failed to write systemd file: {e}")
        sys.exit(1)
    run_command("systemctl daemon-reload")
    run_command("systemctl enable django")
    run_command("systemctl start django")

def setup_kiosk_mode():
    os.makedirs(AUTOSTART_DIR, exist_ok=True)
    if os.path.exists(AUTOSTART_FILE):
        with open(AUTOSTART_FILE, "r") as f:
            lines = f.readlines()
        if KIOSK_LINE not in lines:
            with open(AUTOSTART_FILE, "a") as f:
                f.write(KIOSK_LINE)
            print("Added kiosk mode command to autostart.")
        else:
            print("Kiosk mode already set in autostart.")
    else:
        with open(AUTOSTART_FILE, "w") as f:
            f.write(KIOSK_LINE)
        print("Created autostart file with kiosk mode command.")

def main():
    if os.geteuid() != 0:
        print("This script must be run as root (try using sudo).")
        sys.exit(1)

    print("Updating system and installing necessary packages...")
    update_system()

    print("Cloning repository...")
    clone_repo()

    # Pull the latest changes every time the script runs
    update_repo()

    print("Setting up virtual environment and installing requirements...")
    setup_virtualenv()

    print("Creating systemd service for Django...")
    create_systemd_service()

    print("Configuring Chromium kiosk mode...")
    setup_kiosk_mode()

    print("Setup complete. Reboot your Raspberry Pi to test the configuration.")

if __name__ == "__main__":
    main()
