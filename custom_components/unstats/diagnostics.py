"""Diagnostics support for Unstats."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import UnstatsDataUpdateCoordinator
from .const import CONF_USERNAME

TO_REDACT = {CONF_USERNAME, "username"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    del hass

    coordinator: UnstatsDataUpdateCoordinator = entry.runtime_data
    coordinator_data = coordinator.data if coordinator.data is not None else {}

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "data": async_redact_data(coordinator_data, TO_REDACT),
    }
