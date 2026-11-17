import os
import platform
from urllib import request
import subprocess
import shutil
import time

DEFAULT_HOST = 'localhost:11434'
HOST_ENV_VAR_NAME = 'OLLAMA_HOST'
KEEP_ALIVE_ENV_VAR_NAME = 'OLLAMA_KEEP_ALIVE'

WINDOWS_INSTALLER_URL = 'https://ollama.com/download/OllamaSetup.exe'
UNIX_LIKE_INSTALLER_URL = 'https://ollama.com/install.sh'

PROGRAM_NAME = 'ollama'

def _is_installed():
    return shutil.which(PROGRAM_NAME) is not None

def _download_and_install_windows(url: str = None):
    if url is None:
        url = WINDOWS_INSTALLER_URL
    
    installer_path = 'OllamaSetup.exe'
    
    try:
        request.urlretrieve(url, installer_path)    
        subprocess.run([installer_path, '/VERYSILENT', '/NORESTART'], check=True)
    finally:
        if os.path.exists(installer_path):
            os.remove(installer_path)

def _download_and_install_unix_like(url: str = None):
    if url is None:
        url = UNIX_LIKE_INSTALLER_URL

    with request.urlopen(url) as response:
        script_content = response.read()
    subprocess.run(['sh'], input=script_content, check=True)

def download_and_install(url: str = None):
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

_ollama_server_process = None

def _is_running():
    global _ollama_server_process

    if _ollama_server_process is None:
        return False

    return _ollama_server_process.poll() is None

def start_background_process(host=DEFAULT_HOST, keep_alive=True):
    global _ollama_server_process

    if _is_running():
        print('Ollama is already running in the background.')
        return _ollama_server_process

    env = os.environ.copy()
    env[HOST_ENV_VAR_NAME] = host

    if keep_alive:
        env[KEEP_ALIVE_ENV_VAR_NAME] = '-1'

    _ollama_server_process = subprocess.Popen([PROGRAM_NAME, 'serve'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(5)
    
    if _ollama_server_process.poll() is not None:
        raise BaseException(f'Ollama exited with code {_ollama_server_process.returncode}.')

    print('Ollama is now running in the background.')
    return _ollama_server_process