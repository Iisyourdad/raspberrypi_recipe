#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import time

# ------------------------------
# Configuration
# ------------------------------
REPO_URL = "https://github.com/Iisyourdad/raspberrypi_recipe.git"
USER_NAME = "tyler"  # Changed here
USER_HOME = f"/home/{USER_NAME}"
CODE_DIR = os.path.join(USER_HOME, "raspberrypi_recipe")
VENV_DIR = os.path.join(CODE_DIR, "env")
MANAGE_PY = os.path.join(CODE_DIR, "manage.py")

# Required APT packages
APT_PACKAGES = [
    "python3",
    "python3-venv",
    "git",
    "chromium-browser",
    "florence"
]

# Required Python packages
PYTHON_PACKAGES = [
    "asgiref",
    "Django",
    "django-ckeditor",
    "django-crispy-forms",
    "django-js-asset",
    "pillow",
    "sqlparse",
    "tzdata",
    "gunicorn"
]

# Systemd service file path
SERVICE_FILE = "/etc/systemd/system/recipe-kiosk.service"

# The systemd service content (it calls this script with `--run` on boot)
SERVICE_CONTENT = f"""[Unit]
Description=Django Recipe Kiosk Auto-Setup Service
After=network-online.target graphical.target
Wants=network-online.target

[Service]
Type=simple
User={USER_NAME}
Group={USER_NAME}
WorkingDirectory={USER_HOME}
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)} --run
Environment=DISPLAY=:0
Environment=XAUTHORITY={USER_HOME}/.Xauthority
Restart=on-failure

[Install]
WantedBy=graphical.target
"""

# ------------------------------
# Helpers
# ------------------------------
def run_cmd(cmd, cwd=None, check=True):
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=check)

def apt_install():
    print("Updating apt and installing required system packages...")
    run_cmd(["apt-get", "update"])
    run_cmd(["apt-get", "install", "-y"] + APT_PACKAGES)

def write_service_file():
    print(f"Writing systemd service file at {SERVICE_FILE}")
    with open(SERVICE_FILE, "w") as f:
        f.write(SERVICE_CONTENT)
    run_cmd(["chmod", "644", SERVICE_FILE])
    run_cmd(["systemctl", "daemon-reload"])
    run_cmd(["systemctl", "enable", "recipe-kiosk.service"])

def clone_repo():
    if os.path.exists(CODE_DIR):
        print(f"Removing existing repository at {CODE_DIR}")
        shutil.rmtree(CODE_DIR)
    print("Cloning latest repo...")
    run_cmd(["git", "clone", REPO_URL, CODE_DIR])

def setup_venv():
    if not os.path.exists(VENV_DIR):
        print("Creating Python virtual environment...")
        run_cmd(["python3", "-m", "venv", "env"], cwd=CODE_DIR)
    else:
        print("Virtual environment already exists, skipping creation.")

def install_python_packages():
    print("Installing/Upgrading required Python packages...")
    pip_bin = os.path.join(VENV_DIR, "bin", "pip")
    run_cmd([pip_bin, "install", "--upgrade"] + PYTHON_PACKAGES)

def run_django_commands():
    print("Running Django migrations and collectstatic...")
    python_bin = os.path.join(VENV_DIR, "bin", "python")
    run_cmd([python_bin, MANAGE_PY, "migrate"], cwd=CODE_DIR)
    run_cmd([python_bin, MANAGE_PY, "collectstatic", "--noinput"], cwd=CODE_DIR)

def launch_django_dev_server():
    print("Launching Django development server (0.0.0.0:8000)...")
    python_bin = os.path.join(VENV_DIR, "bin", "python")
    return subprocess.Popen(
        [python_bin, MANAGE_PY, "runserver", "0.0.0.0:8000", "--noreload"],
        cwd=CODE_DIR
    )

def launch_chromium():
    print("Launching Chromium in kiosk mode...")
    chromium_cmd = [
        "/usr/bin/chromium-browser",
        "--noerrdialogs",
        "--disable-infobars",
        "--disable-restore-session-state",
        "--touch-events=enabled",
        "--kiosk",
        "http://localhost:8000"
    ]
    return subprocess.Popen(chromium_cmd, env=dict(os.environ))

# ------------------------------
# Main Logic
# ------------------------------
def initial_setup():
    if os.geteuid() != 0:
        print("Please run this script with sudo (as root). Exiting.")
        sys.exit(1)
    print("Performing initial setup steps...")
    apt_install()
    write_service_file()
    clone_repo()
    setup_venv()
    install_python_packages()
    run_django_commands()

    print("\nInitial setup complete. Rebooting system...")
    time.sleep(3)
    run_cmd(["reboot"])

def run_mode():
    print("Running kiosk startup steps...")
    clone_repo()
    setup_venv()
    install_python_packages()
    run_django_commands()

    server_proc = launch_django_dev_server()
    time.sleep(5)
    browser_proc = launch_chromium()
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            browser_proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        run_mode()
    else:
        initial_setup()
