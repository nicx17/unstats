"""Config flow for Unstats integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_USERNAME, PROXY_URL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Validate that the Unsplash username can be resolved by the proxy.
    username = data[CONF_USERNAME]
    api_url = PROXY_URL.format(username=username)
    session = async_get_clientsession(hass)

    try:
        async with session.get(api_url, timeout=10) as response:
            if response.status == 404:
                raise InvalidAuth
            if response.status >= 500:
                raise CannotConnect

            response.raise_for_status()
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        _LOGGER.error("Failed to connect to Unsplash Proxy: %s", err)
        raise CannotConnect from err

    # Return info that will be stored in the config entry.
    return {"title": f"Unstats ({username})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Unstats."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        username = user_input[CONF_USERNAME].strip()
        user_input[CONF_USERNAME] = username

        try:
            await self.async_set_unique_id(username.lower())
            self._abort_if_unique_id_configured()
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate the username is invalid."""
