"""Test the Unstats config flow."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.core import HomeAssistant

from custom_components.unstats.const import CONF_USERNAME, DOMAIN


async def test_user_flow_creates_entry(hass: HomeAssistant, aioclient_mock) -> None:
    """Test the user config flow."""

    aioclient_mock.get(
        "https://un.hyclotron.com/stats/nickcardoso",
        json={
            "downloads": {"total": 11268, "historical": {}},
            "views": {"total": 1961924, "historical": {}},
        },
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USERNAME: " nickcardoso "},
    )

    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert result.get("title") == "Unstats (nickcardoso)"
    assert result.get("data") == {CONF_USERNAME: "nickcardoso"}


async def test_user_flow_aborts_if_already_configured(
    hass: HomeAssistant, aioclient_mock
) -> None:
    """Test duplicate usernames are rejected."""

    aioclient_mock.get(
        "https://un.hyclotron.com/stats/nickcardoso",
        json={
            "downloads": {"total": 11268, "historical": {}},
            "views": {"total": 1961924, "historical": {}},
        },
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USERNAME: "nickcardoso"},
    )

    assert result.get("type") is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].unique_id == "nickcardoso"

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USERNAME: "NickCardoso"},
    )

    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "already_configured"


async def test_user_flow_shows_invalid_auth_error(
    hass: HomeAssistant, aioclient_mock
) -> None:
    """Test invalid usernames are surfaced in the config flow."""

    aioclient_mock.get("https://un.hyclotron.com/stats/unknown-user", status=404)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USERNAME: "unknown-user"},
    )

    assert result.get("type") is FlowResultType.FORM
    assert result.get("errors") == {"base": "invalid_auth"}
