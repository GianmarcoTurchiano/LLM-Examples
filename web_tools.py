import os
import subprocess
import time
import secrets
import urllib
from typing import Dict
from bs4 import BeautifulSoup
import json
import secrets

_SEARXNG_PORT_ENV_VAR = 'SEARXNG_PORT'
_SEARXNG_BIND_ADDRESS_ENV_VAR = 'SEARXNG_BIND_ADDRESS'
_SEARXNG_HOST = 'SEARXNG_HOST'
_SEARXNG_SETTINGS_PATH = 'SEARXNG_SETTINGS_PATH'
_SEARXNG_DEFAULT_PORT = 8080
_SEARXNG_DEFAULT_BIND_ADDRESS = 'localhost'

def _searxng_setup(bind_address=_SEARXNG_DEFAULT_BIND_ADDRESS, port=_SEARXNG_DEFAULT_PORT):
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

    return env

_searxng_process = None

def _is_searxng_running():
    global _searxng_process

    if _searxng_process is None:
        return False

    return _searxng_process.poll() is None

def searxng_start_background_process(bind_address=_SEARXNG_DEFAULT_BIND_ADDRESS, port=_SEARXNG_DEFAULT_PORT):
    global _searxng_process

    if _is_searxng_running():
        print('SearXNG is already running in the background.')
        return _searxng_process

    _searxng_setup(bind_address, port)
    
    _searxng_process = subprocess.Popen(['searxng-run'], env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    time.sleep(5)
    
    if _searxng_process.poll() is not None:
        output, _ = _searxng_process.communicate()
        print("SearXNG Startup Output:\n", output)
        raise RuntimeError(f'SearXNG exited with code {_searxng_process.returncode}.')

    print('SearXNG is now running in the background.')
    return _searxng_process

def web_search(query: str, lang='it') -> Dict[str, Dict[str, str]]:
    host = os.environ[_SEARXNG_HOST]

    base_url = f'{host}/search'

    params = {
        'q': query,
        'format': 'json',
        'language': lang
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode('utf-8'))
    
    results = {}
    for result in data['results']:
        results[result['url']] = {
            'title': result['title'],
            'content': result['content']
        }
            
    return results

def web_fetch(url: str) -> Dict[str, int | str]:
    headers = {
        'User-Agent': 'MyCoolBot/1.0 (https://example.org/my-tool/; contact@example.org)',
        'Accept-Encoding': 'gzip'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.status
            html_bytes = response.read()
            html_text = html_bytes.decode('utf-8', errors='ignore')
            
    except urllib.error.HTTPError as e:
        status_code = e.code

        if status_code == 429:
            retry_after = e.headers.get('Retry-After', 'unknown')
            return {
                'content': f'Error: Rate limited (429). Retry after {retry_after} seconds.',
                'status_code': status_code
            }
        return {
            'content': f'Error fetching {url}: {str(e)}',
            'status_code': status_code
        }
    except urllib.error.URLError as e:
        return {
            'content': f'Error fetching {url}: {str(e)}',
            'status_code': None
        }
    except Exception as e:
        return {
            'content': f'Error fetching {url}: {str(e)}',
            'status_code': None
        }
    
    soup = BeautifulSoup(html_text, 'html.parser')
    
    for element in soup(['script', 'style', 'noscript']):
        element.decompose()
    
    content = soup.get_text(' ', strip=True)
    
    return {
        'content': content,
        'status_code': status_code
    }