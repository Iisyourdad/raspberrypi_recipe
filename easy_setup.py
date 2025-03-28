import os
import subprocess
import sys
import socket

# Paths and settings
REPO_URL = "https://github.com/Iisyourdad/raspberrypi_recipe.git"
REPO_DIR = "/home/pi/raspberrypi_recipe-main"
PROJECT_DIR = os.path.join(REPO_DIR, "westbrook_recipes")
VENV_DIR = os.path.join(PROJECT_DIR, "venv")
REQUIREMENTS_FILE = os.path.join(PROJECT_DIR, "requirements.txt")
DJANGO_SERVICE_FILE = "/etc/systemd/system/django.service"
AUTOSTART_DIR = "/home/pi/.config/lxsession/LXDE-pi"
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, "autostart")
# Update kiosk mode URL to reflect the new port (27645)
KIOSK_LINE = "@chromium-browser --kiosk http://127.0.0.1:27645/\n"
SELF_SERVICE_FILE = "/etc/systemd/system/easy_setup.service"
IP_OUTPUT_FILE = "/home/pi/ip_address.txt"  # File to save IP address

def run_command(cmd, cwd=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(1)

def update_system():
    run_command("apt-get update -y")
    run_command("apt-get upgrade -y")
    run_command("apt-get install -y git python3-pip python3-venv chromium-browser")

def clone_or_update_repo():
    if not os.path.exists(REPO_DIR):
        run_command(f"git clone {REPO_URL} {REPO_DIR}")
    else:
        print(f"Repository already exists at {REPO_DIR}. Pulling latest changes...")
        run_command("git pull", cwd=REPO_DIR)

def setup_virtualenv():
    os.chdir(PROJECT_DIR)
    if not os.path.exists(VENV_DIR):
        run_command("python3 -m venv venv")
    run_command(f"{VENV_DIR}/bin/pip install --upgrade pip")
    run_command(f"{VENV_DIR}/bin/pip install -r {REQUIREMENTS_FILE}")

def create_django_service():
    service_content = f"""[Unit]
Description=Django Development Server
After=network.target

[Service]
User=pi
WorkingDirectory={PROJECT_DIR}
ExecStart={VENV_DIR}/bin/python manage.py runserver 0.0.0.0:27645
Restart=always

[Install]
WantedBy=multi-user.target
"""
    try:
        with open(DJANGO_SERVICE_FILE, "w") as f:
            f.write(service_content)
        print(f"Created Django service file at {DJANGO_SERVICE_FILE}")
    except Exception as e:
        print(f"Failed to write Django service file: {e}")
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

def setup_self_autostart():
    """
    Creates a systemd service that runs this very script at boot.
    """
    if not os.path.exists(SELF_SERVICE_FILE):
        # Use the absolute path to the current script
        script_path = os.path.abspath(__file__)
        service_content = f"""[Unit]
Description=Run Easy Setup Script at Boot
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {script_path}
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
"""
        try:
            with open(SELF_SERVICE_FILE, "w") as f:
                f.write(service_content)
            print(f"Created self-autostart service file at {SELF_SERVICE_FILE}")
        except Exception as e:
            print(f"Failed to write self-autostart service file: {e}")
            sys.exit(1)
        run_command("systemctl daemon-reload")
        run_command("systemctl enable easy_setup.service")
        print("Enabled easy_setup.service to run at startup.")
    else:
        print("Self-autostart service already exists.")

def get_ip_address():
    """
    Retrieves the primary IP address of the Raspberry Pi.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't have to be reachable; it's used to determine the interface used
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def save_ip_address():
    """
    Saves the Raspberry Pi's IP address to a file.
    """
    ip = get_ip_address()
    try:
        with open(IP_OUTPUT_FILE, "w") as f:
            f.write(ip + "\n")
        print(f"Saved IP address {ip} to {IP_OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to save IP address: {e}")

def main():
    if os.geteuid() != 0:
        print("This script must be run as root (try using sudo).")
        sys.exit(1)

    print("Updating system and installing necessary packages...")
    update_system()

    print("Cloning or updating repository...")
    clone_or_update_repo()

    print("Setting up virtual environment and installing requirements...")
    setup_virtualenv()

    print("Creating Django systemd service...")
    create_django_service()

    print("Configuring Chromium kiosk mode...")
    setup_kiosk_mode()

    print("Setting up self-autostart service for this script...")
    setup_self_autostart()

    print("Saving Raspberry Pi IP address...")
    save_ip_address()

    print("Setup complete. Reboot your Raspberry Pi to test the configuration.")

if __name__ == "__main__":
    main()
