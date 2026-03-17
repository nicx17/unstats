"""Sensor platform for Unstats."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import UnstatsDataUpdateCoordinator
from .const import DOMAIN, LOGGER


@dataclass(frozen=True, kw_only=True)
class UnstatsSensorEntityDescription(SensorEntityDescription):
    """Describe an Unstats sensor entity."""


SENSOR_DESCRIPTIONS: tuple[UnstatsSensorEntityDescription, ...] = (
    UnstatsSensorEntityDescription(
        key="views",
        name="Views",
        icon="mdi:eye",
        state_class=SensorStateClass.TOTAL,
    ),
    UnstatsSensorEntityDescription(
        key="downloads",
        name="Downloads",
        icon="mdi:download",
        state_class=SensorStateClass.TOTAL,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    del hass

    coordinator: UnstatsDataUpdateCoordinator = entry.runtime_data

    # Fetch initial data so we have entities to create
    if not coordinator.data:
        LOGGER.error("No data returned from Unsplash API initially")
        return

    entities = [
        UnstatsSensorEntity(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class UnstatsSensorEntity(SensorEntity):
    """Representation of an Unstats sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: UnstatsDataUpdateCoordinator,
        description: UnstatsSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.username}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.username)},
            name=f"Unsplash {coordinator.username}",
            manufacturer="Unsplash",
            entry_type=DeviceEntryType.SERVICE,
        )
        self._update_from_coordinator()

    async def async_added_to_hass(self) -> None:
        """Register coordinator updates when entity is added."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )

    def _update_from_coordinator(self) -> None:
        """Update cached entity attributes from coordinator data."""
        self._attr_available = self.coordinator.last_update_success
        if self.coordinator.data is None:
            self._attr_native_value = None
            if hasattr(self, "_attr_extra_state_attributes"):
                del self._attr_extra_state_attributes
            return

        self._attr_native_value = self._get_native_value()
        extra_state_attributes = self._get_extra_state_attributes()
        if extra_state_attributes is None:
            if hasattr(self, "_attr_extra_state_attributes"):
                del self._attr_extra_state_attributes
        else:
            self._attr_extra_state_attributes = extra_state_attributes

    def _get_native_value(self) -> int | None:
        """Return the current native value from coordinator data."""
        if self.coordinator.data is None:
            return None

        public_profile = self.coordinator.data.get("public_profile", {})
        if self.entity_description.key in public_profile:
            public_value = public_profile.get(self.entity_description.key)
            return public_value if isinstance(public_value, int) else None

        metric_data = self.coordinator.data.get(self.entity_description.key)
        if isinstance(metric_data, dict):
            total = metric_data.get("total")
            return total if isinstance(total, int) else None

        return metric_data if isinstance(metric_data, int) else None

    def _get_extra_state_attributes(self) -> dict[str, Any] | None:
        """Return historical attributes from coordinator data."""
        if self.coordinator.data is None:
            return None
        metric_data = self.coordinator.data.get(self.entity_description.key)
        if not isinstance(metric_data, dict):
            return None

        historical = metric_data.get("historical", {})

        attrs = {}
        values = historical.get("values", [])

        if values:
            attrs["historical"] = values
            if len(values) > 0:
                attrs["latest_daily_value"] = values[-1].get("value")

        if "change" in historical:
            attrs["change_30d"] = historical.get("change")
        if "average" in historical:
            attrs["average_30d"] = historical.get("average")

        return attrs if attrs else None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_from_coordinator()
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Refresh data from the coordinator."""
        if not self.enabled:
            return

        await self.coordinator.async_request_refresh()
