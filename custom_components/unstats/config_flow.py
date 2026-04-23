"""Config flow for Unstats integration."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_USERNAME, DOMAIN, build_proxy_url

_LOGGER = logging.getLogger(__name__)
INVALID_USERNAME_CHARS = re.compile(r"[\x00-\x1f\x7f/\?#]")
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
    }
)


def normalize_username(username: str) -> str:
    """Normalize and validate the configured username."""
    normalized = username.strip()
    if not normalized or len(normalized) > 100:
        raise InvalidAuth
    if INVALID_USERNAME_CHARS.search(normalized):
        raise InvalidAuth

    return normalized


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Validate that the Unsplash username can be resolved by the proxy.
    username = data[CONF_USERNAME]
    api_url = build_proxy_url(username)
    session = async_get_clientsession(hass)

    try:
        async with session.get(api_url, timeout=REQUEST_TIMEOUT) as response:
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


# pylint: disable=abstract-method
class ConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):  # pyright: ignore[reportGeneralTypeIssues,reportCallIssue]
    """Handle a config flow for Unstats."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        try:
            username = normalize_username(user_input[CONF_USERNAME])
        except InvalidAuth:
            errors["base"] = "invalid_auth"
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
            )

        user_input[CONF_USERNAME] = username

        try:
            await self.async_set_unique_id(username.lower())
            self._abort_if_unique_id_configured()
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except AbortFlow:
            raise
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
