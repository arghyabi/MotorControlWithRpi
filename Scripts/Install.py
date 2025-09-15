import os
import grp
import pwd
import time
import socket
from Common import *

PHP_SERVICE_FILE       = "motor-control-with-rpi-php.service"
PYTHON_SERVICE_FILE    = "motor-control-with-rpi-python.service"


def getUserNameAndGroup():
    # Get current username
    username = pwd.getpwuid(os.getuid()).pw_name

    # Get primary group
    groupId = os.getgid()
    primaryGroup = grp.getgrgid(groupId).gr_name

    return username, primaryGroup


def getIpAddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ipAddress = s.getsockname()[0]
    except Exception:
        ipAddress = "127.0.0.1"
    finally:
        s.close()
    return ipAddress


def addPhpServerService(dryRun = False):
    absPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), WEBSITE_FOLDER)
    userName, userGroup = getUserNameAndGroup()
    serviceFileBody = f'''
[Unit]
Description=Motor Control PHP Web Server

[Service]
Type=simple
Restart=always
RestartSec=1
ExecStart=/usr/bin/php -S 0.0.0.0:8000 -t {absPath}
User={userName}
Group={userGroup}

[Install]
WantedBy=multi-user.target

'''
    serviceFilePath = os.path.join("/etc/systemd/system", PHP_SERVICE_FILE)
    print(f"Service file: {serviceFilePath}")

    CreateService = True

    if os.path.exists(serviceFilePath):
        with open(serviceFilePath, "r") as f:
            data = f.read()

        if data.strip() == serviceFileBody.strip():
            CreateService = False

    if CreateService or dryRun:
        print(f"Creating service file: {PHP_SERVICE_FILE}")
        with open(PHP_SERVICE_FILE, "w") as f:
            f.write(serviceFileBody)

        if dryRun:
            return

        os.system(f"sudo cp {PHP_SERVICE_FILE} /etc/systemd/system")
        time.sleep(0.5)

    print("Daemon reloading...")
    os.system("sudo systemctl daemon-reload")
    time.sleep(1)

    print("Service Enabling...")
    os.system(f"sudo systemctl enable {PHP_SERVICE_FILE}")
    time.sleep(1)

    print("Service Starting...")
    os.system(f"sudo systemctl start {PHP_SERVICE_FILE}")
    time.sleep(1)

    print(f"Service Should run on http://{getIpAddress()}:8000")


def addPythonServerService(dryRun = False):
    workspace = os.path.dirname(os.path.abspath(__file__))
    mainFile = os.path.join(workspace, "Main.py")

    userName, userGroup = getUserNameAndGroup()

    serviceFileBody = f'''
[Unit]
Description=Motor Control Python Server

[Service]
Type=simple
Restart=always
RestartSec=1
ExecStart=/usr/bin/python {mainFile}
WorkingDirectory={workspace}
User={userName}
Group={userGroup}

[Install]
WantedBy=multi-user.target

'''
    serviceFilePath = os.path.join("/etc/systemd/system", PYTHON_SERVICE_FILE)
    print(f"Service file: {serviceFilePath}")

    CreateService = True

    if os.path.exists(serviceFilePath):
        with open(serviceFilePath, "r") as f:
            data = f.read()

        if data.strip() == serviceFileBody.strip():
            CreateService = False

    if CreateService or dryRun:
        with open(PYTHON_SERVICE_FILE, "w") as f:
            f.write(serviceFileBody)

        if dryRun:
            return

        os.system(f"sudo cp {PYTHON_SERVICE_FILE} /etc/systemd/system")
        time.sleep(0.5)

    print("Daemon reloading...")
    os.system("sudo systemctl daemon-reload")
    time.sleep(1)

    print("Service Enabling...")
    os.system(f"sudo systemctl enable {PYTHON_SERVICE_FILE}")
    time.sleep(1)

    print("Service Starting...")
    os.system(f"sudo systemctl start {PYTHON_SERVICE_FILE}")
    time.sleep(1)

    print(f"Python Server Started!")


if __name__ == "__main__":
    dryRun = True
    addPhpServerService(dryRun = dryRun)
    addPythonServerService(dryRun = dryRun)
