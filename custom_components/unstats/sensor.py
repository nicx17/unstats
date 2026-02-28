"""Sensor platform for Unstats."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from . import UnstatsDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Fetch initial data so we have entities to create
    if not coordinator.data:
        LOGGER.error("No data returned from Unsplash API initially")
        return

    entities = [
        UnstatsSensorEntity(coordinator, "views", "mdi:eye", "Views"),
        UnstatsSensorEntity(coordinator, "downloads", "mdi:download", "Downloads"),
        UnstatsSensorEntity(coordinator, "likes", "mdi:thumb-up", "Likes"),
    ]

    async_add_entities(entities)


class UnstatsSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of an Unstats sensor."""

    def __init__(
        self,
        coordinator: UnstatsDataUpdateCoordinator,
        metric: str,
        icon: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._metric = metric
        self._attr_icon = icon
        self._attr_name = f"Unsplash {name}"
        self._attr_unique_id = f"{coordinator.username}_{metric}"
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        # Access the specific metric total from the response JSON
        metric_data = self.coordinator.data.get(self._metric, {})
        return metric_data.get("total")

    @property
    def extra_state_attributes(self):
        """Return extra state attributes (like historical data)."""
        if self.coordinator.data is None:
            return None

        metric_data = self.coordinator.data.get(self._metric, {})
        historical = metric_data.get("historical", {}).get("values", [])

        if historical:
            return {"historical": historical}
        return None
