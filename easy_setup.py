#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import time

# --- CONFIGURATION ---
# Repository URL
REPO_URL = "https://github.com/Iisyourdad/raspberrypi_recipe.git"

# We'll clone/pull into /home/pi/raspberrypi_recipe
PI_HOME = os.path.expanduser("~pi")
CODE_DIR = os.path.join(PI_HOME, "raspberrypi_recipe")
VENV_DIR = os.path.join(CODE_DIR, "env")
MANAGE_PY = os.path.join(CODE_DIR, "manage.py")

# apt packages to install
APT_PACKAGES = [
    "python3", "python3-venv", "git", "chromium-browser", "florence"
]

# pip packages to install in the virtualenv
PYTHON_PACKAGES = [
    "asgiref", "Django", "django-ckeditor", "django-crispy-forms",
    "django-js-asset", "pillow", "sqlparse", "tzdata", "gunicorn"
]

# systemd service file
SERVICE_FILE = "/etc/systemd/system/recipe-kiosk.service"

# This service runs this script with the "--run" flag at boot
SERVICE_CONTENT = f"""[Unit]
Description=Django Recipe Kiosk Auto-Setup Service
After=network-online.target graphical.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory={PI_HOME}
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)} --run
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
Restart=on-failure

[Install]
WantedBy=graphical.target
"""

# --- UTILITY FUNCTIONS ---
def run_command(cmd, cwd=None, check=True):
    """Run a shell command, optionally in a given working directory."""
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=check)

def apt_install():
    """Install required apt packages."""
    print("Updating apt and installing required packages...")
    run_command(["apt-get", "update"])
    run_command(["apt-get", "install", "-y"] + APT_PACKAGES)

def write_service_file():
    """Write and enable the systemd service file."""
    print(f"Writing systemd service file to {SERVICE_FILE}")
    with open(SERVICE_FILE, "w") as f:
        f.write(SERVICE_CONTENT)
    run_command(["chmod", "644", SERVICE_FILE])
    run_command(["systemctl", "daemon-reload"])
    run_command(["systemctl", "enable", "recipe-kiosk.service"])

def update_repo():
    """
    If the repo folder exists, do a git pull.
    Otherwise, clone it fresh.
    """
    if os.path.exists(CODE_DIR):
        print("Repository exists. Updating with git pull...")
        run_command(["git", "pull"], cwd=CODE_DIR)
    else:
        print("Cloning repository...")
        run_command(["git", "clone", REPO_URL, CODE_DIR])

def setup_virtualenv():
    """Create virtual environment if not present."""
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        run_command(["python3", "-m", "venv", "env"], cwd=CODE_DIR)
    else:
        print("Virtual environment already exists.")

def install_python_packages():
    """Install all required Python packages into the virtual environment."""
    pip_path = os.path.join(VENV_DIR, "bin", "pip")
    print("Installing required Python packages...")
    run_command([pip_path, "install", "--upgrade"] + PYTHON_PACKAGES)

def run_django_commands():
    """Run migrations and collectstatic."""
    python_path = os.path.join(VENV_DIR, "bin", "python")
    print("Running Django migrations...")
    run_command([python_path, MANAGE_PY, "migrate"], cwd=CODE_DIR)
    print("Collecting static files...")
    run_command([python_path, MANAGE_PY, "collectstatic", "--noinput"], cwd=CODE_DIR)

def launch_django_server():
    """Launch Django dev server on 0.0.0.0:8000 (non-blocking)."""
    python_path = os.path.join(VENV_DIR, "bin", "python")
    print("Launching Django development server on 0.0.0.0:8000...")
    return subprocess.Popen(
        [python_path, MANAGE_PY, "runserver", "0.0.0.0:8000", "--noreload"],
        cwd=CODE_DIR
    )

def launch_chromium():
    """Launch Chromium in kiosk mode."""
    chrome_cmd = [
        "/usr/bin/chromium-browser",
        "--noerrdialogs",
        "--disable-infobars",
        "--disable-restore-session-state",
        "--touch-events=enabled",
        "--kiosk",
        "http://localhost:8000"
    ]
    print("Launching Chromium in kiosk mode...")
    return subprocess.Popen(chrome_cmd, env=dict(os.environ))

def launch_florence():
    """Launch Florence on-screen keyboard."""
    print("Launching Florence on-screen keyboard...")
    return subprocess.Popen(["florence"], env=dict(os.environ))

# --- MAIN MODES ---
def initial_setup():
    """
    Runs once when the script is manually executed (without --run).
    Installs system packages, writes service file, sets up the project,
    and reboots so that the kiosk starts automatically on next boot.
    """
    print("Starting initial setup...")

    # Must run as root
    if os.geteuid() != 0:
        print("ERROR: This script must be run with sudo or as root.")
        sys.exit(1)

    # Install required apt packages
    apt_install()

    # Write systemd service file
    write_service_file()

    # Initial clone/pull + venv setup + dependencies + migrations
    update_repo()
    setup_virtualenv()
    install_python_packages()
    run_django_commands()

    print("Initial setup complete. Rebooting now to launch the kiosk on next boot...")
    time.sleep(3)
    run_command(["reboot"])

def run_service():
    """
    Runs at every boot via systemd (with --run).
    Pulls repo, sets up venv, runs migrations, then launches Django, Chromium, and Florence.
    """
    print("Running kiosk service mode...")

    # Update repository
    update_repo()

    # Ensure virtual environment is ready and packages are installed
    setup_virtualenv()
    install_python_packages()

    # Run Django migrations and collect static files
    run_django_commands()

    # Launch Django server
    server_proc = launch_django_server()

    # Give server a few seconds to start up
    time.sleep(5)

    # Launch Chromium in kiosk mode
    browser_proc = launch_chromium()

    # Launch Florence on-screen keyboard
    florence_proc = launch_florence()

    # Keep the service alive as long as the Django server is running
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        pass

    # On exit, attempt to terminate Chromium and Florence
    try:
        browser_proc.terminate()
    except Exception:
        pass
    try:
        florence_proc.terminate()
    except Exception:
        pass

# --- ENTRY POINT ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        run_service()
    else:
        initial_setup()
