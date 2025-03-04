import os
import json
import asyncio
import re
import time
from kasa import Discover
from kasa.iot import IotBulb

def simplify(s):
    return re.sub(r'\W+', '', s).lower()

CONFIG_FILE = 'config.json'

def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError:
            # If the file is corrupted, return an empty dict.
            return {}
    return {}

def set_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_cached_ip():
    config = get_config()
    return config.get('ip')

def set_cached_ip(ip):
    config = get_config()
    config['ip'] = ip
    set_config(config)

def get_cached_alias():
    config = get_config()
    return config.get('alias')

def discover_device(desired_alias):
    """
    Replace this with your actual device discovery logic.
    This function should return a tuple of (ip, alias).
    For demonstration, we return placeholder values.
    """
    simplified_alias = simplify(desired_alias)
    devices = asyncio.run(Discover.discover())
    lamp = next(
        (x for x in devices.values() if simplify(getattr(x, 'alias', '')) == simplified_alias),
        None
    )

    if lamp:
        set_cached_ip(lamp.host)
        asyncio.run(lamp.update())
        return lamp

    return None

def verify_device(ip, desired_alias):
    """
    Implement this function to verify that the device at the given IP
    is the one you expect. For example, you might query the device for its alias.
    For now, we'll just simulate verification.
    """
    bulb = IotBulb(ip)
    try:
        asyncio.run(bulb.update())
    except:
        return False

    if simplify(bulb.alias) == simplify(desired_alias):
        return bulb

    return False

def get_device():
    """
    Attempts to retrieve the device IP from cache. If the cached IP
    and alias are valid, return them. Otherwise, perform discovery,
    update the cache, and return the new IP.
    """
    cached_ip = get_cached_ip()
    cached_alias = get_cached_alias()
    if cached_ip and cached_alias:
        verified_device = verify_device(cached_ip, cached_alias)
        if verified_device:
            return verified_device

    # Discovery is needed.
    if cached_alias:
        discovered_device = discover_device(cached_alias)
        if discovered_device:
            return discovered_device
    return None

def get_light():
    lamp = get_device()
    if lamp:
        light = lamp.modules.get('Light', None)
        return light
    return None


# Usage example:
def get_status():
    light = get_light()
    if light:
        return light.state
    return None
