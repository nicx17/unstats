"""Constants for the Unstats integration."""

import logging
from urllib.parse import quote

DOMAIN = "unstats"
LOGGER = logging.getLogger(__package__)

CONF_USERNAME = "username"

# Hardcoded proxy URL where the requests are proxied via Cloudflare
PROXY_URL = "https://un.hyclotron.com/stats/{username}"

# Update interval for polling the API
UPDATE_INTERVAL_MINUTES = 60


def build_proxy_url(username: str) -> str:
    """Build a safe proxy URL for a username."""
    return PROXY_URL.format(username=quote(username, safe=""))
