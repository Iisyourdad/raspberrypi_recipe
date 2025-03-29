#!/usr/bin/env python3
import os, sys, subprocess, shutil, time

# --- CONFIGURATION ---
# Repository URL and target directories
REPO_URL = "https://github.com/Iisyourdad/raspberrypi_recipe.git"
# We’ll clone into /home/pi/raspberrypi_recipe (if repo creates a different folder name, adjust accordingly)
PI_HOME = os.path.expanduser("~pi")
CODE_DIR = os.path.join(PI_HOME, "raspberrypi_recipe")
VENV_DIR = os.path.join(CODE_DIR, "env")
# Path to manage.py; adjust if necessary (e.g., if inside a subfolder)
MANAGE_PY = os.path.join(CODE_DIR, "manage.py")

# Required apt packages (if not already installed)
APT_PACKAGES = ["python3", "python3-venv", "git", "chromium-browser"]

# Required Python packages to install in the virtualenv
PYTHON_PACKAGES = [
    "asgiref", "Django", "django-ckeditor", "django-crispy-forms",
    "django-js-asset", "pillow", "sqlparse", "tzdata", "gunicorn"
]

# Systemd service file path and content
SERVICE_FILE = "/etc/systemd/system/recipe-kiosk.service"
# This service will run this script with the "--run" flag.
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
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=check)

def apt_install():
    print("Updating apt and installing required packages...")
    run_command(["apt-get", "update"])
    run_command(["apt-get", "install", "-y"] + APT_PACKAGES)

def write_service_file():
    print(f"Writing systemd service file to {SERVICE_FILE}")
    with open(SERVICE_FILE, "w") as f:
        f.write(SERVICE_CONTENT)
    # Set proper permissions (644) and reload systemd daemon
    run_command(["chmod", "644", SERVICE_FILE])
    run_command(["systemctl", "daemon-reload"])
    # Enable the service so it starts at boot
    run_command(["systemctl", "enable", "recipe-kiosk.service"])

def update_repo():
    if os.path.exists(CODE_DIR):
        print("Repository exists. Updating with git pull...")
        run_command(["git", "pull"], cwd=CODE_DIR)
    else:
        print("Cloning repository...")
        run_command(["git", "clone", REPO_URL, CODE_DIR], check=True)

def setup_virtualenv():
    # Create virtual environment if it doesn't exist
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        run_command(["python3", "-m", "venv", "env"], cwd=CODE_DIR)
    else:
        print("Virtual environment already exists.")

def install_python_packages():
    pip_path = os.path.join(VENV_DIR, "bin", "pip")
    print("Installing required Python packages...")
    run_command([pip_path, "install", "--upgrade"] + PYTHON_PACKAGES)

def run_django_commands():
    python_path = os.path.join(VENV_DIR, "bin", "python")
    print("Running Django migrations...")
    run_command([python_path, MANAGE_PY, "migrate"], cwd=CODE_DIR)
    print("Collecting static files...")
    run_command([python_path, MANAGE_PY, "collectstatic", "--noinput"], cwd=CODE_DIR)

def launch_django_server():
    python_path = os.path.join(VENV_DIR, "bin", "python")
    print("Launching Django development server on 0.0.0.0:8000 (with --noreload)...")
    # Use Popen so we can continue in the script (and later wait on it)
    return subprocess.Popen([python_path, MANAGE_PY, "runserver", "0.0.0.0:8000", "--noreload"],
                            cwd=CODE_DIR)

def launch_chromium():
    # Launch Chromium in kiosk mode with touch enabled
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

# --- MAIN MODES ---
def initial_setup():
    # This is run if no "--run" flag is provided.
    print("Starting initial setup...")
    # 1. Ensure we are running as root
    if os.geteuid() != 0:
        print("This script must be run as root. Exiting.")
        sys.exit(1)
    # 2. Install required apt packages
    apt_install()
    # 3. Write systemd service file and enable it
    write_service_file()
    # 4. Do initial clone and setup (so that on first boot, service has code)
    update_repo()
    setup_virtualenv()
    install_python_packages()
    run_django_commands()
    print("Initial setup complete. The system will reboot now to launch the kiosk service on boot.")
    time.sleep(3)
    run_command(["reboot"])

def run_service():
    # This is run when the service is triggered (via systemd with the --run flag)
    print("Running kiosk service tasks...")
    # Update repo (only pulls new changes if available)
    update_repo()
    setup_virtualenv()
    install_python_packages()
    run_django_commands()
    # Launch Django server
    server_proc = launch_django_server()
    # Wait a few seconds to let Django start up
    time.sleep(5)
    # Launch Chromium in kiosk mode
    browser_proc = launch_chromium()
    # Wait for the Django server process to exit (keeps the service alive)
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        pass
    # On exit, attempt to terminate Chromium
    try:
        browser_proc.terminate()
    except Exception:
        pass

# --- ENTRY POINT ---
if __name__ == "__main__":
    # If run with the "--run" flag, execute the service mode.
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        run_service()
    else:
        initial_setup()
