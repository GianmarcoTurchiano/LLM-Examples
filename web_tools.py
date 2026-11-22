import os
import subprocess
import time
import secrets
from typing import Dict
import json
import secrets

from requests import RequestException
import requests
from bs4 import BeautifulSoup

_SEARXNG_PORT_ENV_VAR = 'SEARXNG_PORT'
_SEARXNG_BIND_ADDRESS_ENV_VAR = 'SEARXNG_BIND_ADDRESS'
_SEARXNG_HOST = 'SEARXNG_HOST'
_SEARXNG_SETTINGS_PATH = 'SEARXNG_SETTINGS_PATH'
_SEARXNG_DEFAULT_PORT = 8080
_SEARXNG_DEFAULT_BIND_ADDRESS = 'localhost'

def searxng_setup(bind_address=_SEARXNG_DEFAULT_BIND_ADDRESS, port=_SEARXNG_DEFAULT_PORT):
    secret_key = secrets.token_hex(32)
    yaml_content = (
        "use_default_settings: true\n"
        "server:\n"
        f'  bind_address: "{bind_address}"\n'
        f"  port: {port}\n"
        f'  secret_key: "{secret_key}"\n'
        "  debug: false\n"
        "search:\n"
        "  formats:\n"
        "    - html\n"
        "    - json\n"
    )

    settings_filename = "searxng_settings.yml"
    with open(settings_filename, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    env = os.environ.copy()
    env[_SEARXNG_SETTINGS_PATH] = os.path.abspath(settings_filename)
    env[_SEARXNG_BIND_ADDRESS_ENV_VAR] = bind_address
    env[_SEARXNG_PORT_ENV_VAR] = str(port)
    os.environ[_SEARXNG_HOST] = f'http://{bind_address}:{port}'

_searxng_process = None

def _is_searxng_running():
    global _searxng_process

    if _searxng_process is None:
        return False

    return _searxng_process.poll() is None

def searxng_start_background_process():
    global _searxng_process

    if _is_searxng_running():
        print('SearXNG is already running in the background.')
        return _searxng_process
    
    _searxng_process = subprocess.Popen(['searxng-run'], env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    time.sleep(5)
    
    if _searxng_process.poll() is not None:
        output, _ = _searxng_process.communicate()
        print("SearXNG Startup Output:\n", output)
        raise RuntimeError(f'SearXNG exited with code {_searxng_process.returncode}.')

    print('SearXNG is now running in the background.')
    return _searxng_process

def web_search(query: str):
    host = os.environ['SEARXNG_HOST']
    response = requests.get(
        f"{host}/search",
        params={
            "q": query,
            "format": "json",
            "language": "it"
        },
    )
    
    response.raise_for_status()
    
    data = response.json()
    
    results = {}
    
    for result in data['results']:
        results[result['url']] = {
            'title': result['title'],
            'content': result['content']
        }
            
    return results

def web_fetch(url: str):
    headers = {
        "User-Agent": "MyCoolBot/1.0 (https://example.org/my-tool/; contact@example.org)",
        "Accept-Encoding": "gzip"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        status_code = r.status_code
        
        if status_code == 429:
            retry_after = r.headers.get("Retry-After", "unknown")
            return {
                "content": f"Error: Rate limited (429). Retry after {retry_after} seconds.",
                "status_code": status_code
            }
            
        r.raise_for_status()
    except RequestException as e:
        # Extract status code if a response was received despite the error
        status_code = e.response.status_code if e.response is not None else None
        return {
            "content": f"Error fetching {url}: {str(e)}",
            "status_code": status_code
        }
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    
    content = soup.get_text(" ", strip=True)
    
    return {
        "content": content,
        "status_code": status_code
    }