from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unstats.const import CONF_USERNAME, DOMAIN
from custom_components.unstats.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics_redacts_username(hass: HomeAssistant, aioclient_mock) -> None:
    """Test diagnostics redact usernames from the entry and payload."""

    aioclient_mock.get(
        "https://un.hyclotron.com/stats/nickcardoso",
        json={
            "username": "nickcardoso",
            "downloads": {"total": 11268, "historical": {}},
            "views": {"total": 1961924, "historical": {}},
        },
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_USERNAME: "nickcardoso"},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    assert diagnostics["entry"]["data"][CONF_USERNAME] == "**REDACTED**"
    assert diagnostics["data"]["username"] == "**REDACTED**"
