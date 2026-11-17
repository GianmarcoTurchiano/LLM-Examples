import os
import platform
from urllib import request
import subprocess
import shutil
import time

DEFAULT_HOST = 'localhost:11434'
HOST_ENV_VAR_NAME = 'OLLAMA_HOST'

WINDOWS_INSTALLER_URL = 'https://ollama.com/download/OllamaSetup.exe'
UNIX_LIKE_INSTALLER_URL = 'https://ollama.com/install.sh'

PROGRAM_NAME = 'ollama'

def _is_installed():
    return shutil.which(PROGRAM_NAME) is not None

def _download_and_install_windows(url=WINDOWS_INSTALLER_URL):
    installer_path = 'OllamaSetup.exe'
    try:
        request.urlretrieve(url, installer_path)    
        subprocess.run([installer_path, '/VERYSILENT', '/NORESTART'], check=True)
    finally:
        if os.path.exists(installer_path):
            os.remove(installer_path)

def _download_and_install_unix_like(url=UNIX_LIKE_INSTALLER_URL):
    with request.urlopen(url) as response:
        script_content = response.read()
    subprocess.run(['sh'], input=script_content, check=True)

def download_and_install(url: str):
    if _is_installed():
        print('Ollama is already installed.')
        return

    current_os = platform.system()

    if current_os == 'Windows':
        _download_and_install_windows(url)
    elif current_os in ['Linux', 'Darwin']:
        _download_and_install_unix_like(url)
    else:
        raise BaseException(f"Unsupported OS: {current_os}")

    print('Ollama has been installed.')

def _is_server_running():
    url = os.environ.get(HOST_ENV_VAR_NAME, DEFAULT_HOST)
    
    try:
        request.urlopen(f'{url}/api/version', timeout=2)
        return True
    except:
        return False

_ollama_server_process = None

def start_background_process():
    global _ollama_server_process

    if _is_server_running():
        print('Ollama is already running in the background.')
        return _ollama_server_process

    _ollama_server_process = subprocess.Popen([PROGRAM_NAME, 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(5)
    
    if _ollama_server_process.poll() is not None:
        raise BaseException(f'Ollama exited with code {_ollama_server_process.returncode}.')

    print('Ollama is now running in the background.')
    return _ollama_server_process