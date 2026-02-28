"""Constants for the Unstats integration."""

import logging

DOMAIN = "unstats"
LOGGER = logging.getLogger(__package__)

CONF_USERNAME = "username"

# Hardcoded proxy URL where the requests are proxied via Cloudflare
PROXY_URL = "https://un.hyclotron.com/stats/{username}"

# Update interval for polling the API
UPDATE_INTERVAL_MINUTES = 60
