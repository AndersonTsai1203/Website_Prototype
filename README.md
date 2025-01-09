# Sakura Website Prototype
a website application prototype to make the current version of application more sufficient for user experience and security reason.

## Components
1. ACR122U NFC card reader
2. NFC cards

## Set up Guide
Note: In my case, I'm using <b>Ubuntu 24.04 LTS distribution<b>

1. Open terminal, run
    ```
    sudo apt-get update
    ```
2. Install Python, I'm using <b>Python3 version<b>
    ```
    sudo apt install python
    ```
3. Set up a Python virtual environment in the current directory
    ```
    python3 -m venv <your venv name>
    ```
4. Activate the virtual environment in the current directory where the venv is located
    ```
    source <your venv name>/bin/activate
    ```
5. Run the <b>"requirements.txt"<b> to install the required packages for this project
    ```
    python3 -m pip install -r requirements.txt
    ```
6. After installing these packages, start PC/SC daemon
    ```
    sudo systemctl enable pcscard
    sudo systemctl start pcscard
    ```
7. Verify the card reader installation with
    ```
    pcsc_scan
    ```
    This should detect the ACR122U reader when it's plugged in