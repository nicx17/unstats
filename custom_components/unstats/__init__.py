"""The Unstats integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import Platform

from .const import (
    DOMAIN,
    LOGGER,
    CONF_USERNAME,
    UPDATE_INTERVAL_MINUTES,
    PROXY_URL,
)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Unstats from a config entry."""
    username = entry.data[CONF_USERNAME]

    coordinator = UnstatsDataUpdateCoordinator(hass, username)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class UnstatsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Unsplash data."""

    def __init__(self, hass: HomeAssistant, username: str) -> None:
        """Initialize."""
        self.username = username
        self._session = async_get_clientsession(hass)

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self):
        """Fetch data from Unsplash Proxy."""
        api_url = PROXY_URL.format(username=self.username)

        try:
            async with self._session.get(api_url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Error communicating with Proxy API: {err}") from err
