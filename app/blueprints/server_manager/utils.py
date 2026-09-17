import base64
import json
import os
import platform
from urllib.parse import urljoin

import requests
from cryptography.fernet import Fernet


# encryption, used for creating a save file to store login credentials
def get_encryption_key(config):
    key = config.ENCRYPTION_KEY
    if len(key) != 32:
        raise ValueError("ENCRYPTION_KEY has to be 32 chars")
    return base64.urlsafe_b64encode(key.encode())

def encrypt_data(data: dict, config) -> str:
    fernet = Fernet(get_encryption_key(config))
    json_data = json.dumps(data).encode()
    return fernet.encrypt(json_data).decode()

def decrypt_data(encrypted_data: str, config) -> dict:
    fernet = Fernet(get_encryption_key(config))
    decrypted_data = fernet.decrypt(encrypted_data.encode())
    return json.loads(decrypted_data.decode())

# actually load/save the login credentials
def save_servers(servers: list, config):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    encrypted_data = encrypt_data({"servers": servers}, config)
    with open(config.SERVER_DATA_FILE, "w") as f:
        f.write(encrypted_data)

def load_servers(config) -> list:
    if not os.path.exists(config.SERVER_DATA_FILE):
        return []
    with open(config.SERVER_DATA_FILE, "r") as f:
        encrypted_data = f.read()
    return decrypt_data(encrypted_data, config).get("servers", [])


# jellyfin api helper functions
def authenticate_jellyfin(server_url: str, username: str, password: str):
    """Gives back AccessToken and Server-ID"""
    auth_url = urljoin(server_url, "/Users/AuthenticateByName")
    auth_data = {"Username": username, "Pw": password}

    response = requests.post(auth_url, json=auth_data, headers=get_headers())
    if response.status_code != 200:
        raise Exception(f"Authentication failed: {response.status_code} - {response.text}")

    return response.json().get("AccessToken"), response.json().get("User", {}).get("Id")

def fetch_jellyfin_libraries(server_url: str, access_token: str, user_id: str):

    libraries_url = urljoin(server_url, f"/Users/{user_id}/Views")
    response = requests.get(libraries_url, headers=get_headers(access_token))

    if response.status_code != 200:
        raise Exception(f"Error fetching libraries: {response.status_code} - {response.text}")

    return response.json().get("Items", [])

def fetch_media_from_library(server_url: str, access_token: str, library_id: str, media_type: str):

    media_url = urljoin(server_url, "/Items")
    params = {
        "ParentId": library_id,
        "Recursive": "true",
        "IncludeItemTypes": media_type,
        "Fields": "PrimaryImageAspectRatio,ItemCounts,ProviderIds"
    }

    response = requests.get(media_url, headers=get_headers(access_token), params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching media: {response.status_code} - {response.text}")

    return response.json().get("Items", [])


def get_headers(access_token=""):
    client_name = "OverseaFin - Overview Available Media"
    device_id = str({platform.node()})
    version = "1.0.0"

    vanilla_token = (
        f'MediaBrowser Client="{client_name}", '
        f'Device="{device_id}", '
        f'DeviceId="{device_id}", '
        f'Version="{version}", '
        f'Token="{access_token}"'
    )

    headers = {
        "Authorization": f'{vanilla_token}',
        "Content-Type": "application/json"
    }

    return headers
