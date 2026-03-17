"""The Unstats integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_USERNAME,
    DOMAIN,
    LOGGER,
    UPDATE_INTERVAL_MINUTES,
    build_proxy_url,
)

PLATFORMS: list[Platform] = [Platform.SENSOR]
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Unstats from a config entry."""
    username = entry.data[CONF_USERNAME]

    coordinator = UnstatsDataUpdateCoordinator(hass, username)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class UnstatsDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
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

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Unsplash Proxy."""
        api_url = build_proxy_url(self.username)

        try:
            async with self._session.get(api_url, timeout=REQUEST_TIMEOUT) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Error communicating with Proxy API: {err}") from err
