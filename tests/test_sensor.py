from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unstats.const import DOMAIN, CONF_USERNAME


async def test_sensor_creation(hass: HomeAssistant, aioclient_mock):
    """Test that the sensors are created correctly."""

    # Mock the API response
    aioclient_mock.get(
        "https://un.hyclotron.com/stats/nickcardoso",
        json={
            "id": "EM_a1wq_Txo",
            "username": "nickcardoso",
            "downloads": {
                "total": 11268,
                "historical": {
                    "change": 528,
                    "average": 18,
                    "resolution": "days",
                    "quantity": 30,
                    "values": [{"date": "2026-02-27", "value": 23}],
                },
            },
            "views": {
                "total": 1961924,
                "historical": {
                    "change": 45972,
                    "average": 1532,
                    "resolution": "days",
                    "quantity": 30,
                    "values": [{"date": "2026-02-27", "value": 1248}],
                },
            },
        },
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_USERNAME: "nickcardoso"},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED

    entity_registry = er.async_get(hass)

    views_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, "nickcardoso_views"
    )
    assert views_entity_id is not None
    views_state = hass.states.get(views_entity_id)
    assert views_state is not None
    assert views_state.state == "1961924"
    assert views_state.attributes.get("change_30d") == 45972
    assert views_state.attributes.get("average_30d") == 1532
    assert views_state.attributes.get("icon") == "mdi:eye"
    assert views_state.attributes.get("friendly_name") == "Unsplash nickcardoso Views"

    downloads_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, "nickcardoso_downloads"
    )
    assert downloads_entity_id is not None
    downloads_state = hass.states.get(downloads_entity_id)
    assert downloads_state is not None
    assert downloads_state.state == "11268"
    assert downloads_state.attributes.get("change_30d") == 528
    assert downloads_state.attributes.get("average_30d") == 18
    assert downloads_state.attributes.get("icon") == "mdi:download"
    assert (
        entity_registry.async_get_entity_id("sensor", DOMAIN, "nickcardoso_likes")
        is None
    )


async def test_unload_entry_removes_entities(hass: HomeAssistant, aioclient_mock):
    """Test unloading a config entry removes its entities."""

    aioclient_mock.get(
        "https://un.hyclotron.com/stats/nickcardoso",
        json={
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

    entity_registry = er.async_get(hass)
    views_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, "nickcardoso_views"
    )
    assert views_entity_id is not None

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    state = hass.states.get(views_entity_id)
    assert state is not None
    assert state.state == STATE_UNAVAILABLE
