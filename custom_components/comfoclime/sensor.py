"""Sensor platform for Comfoclime."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfVolumeFlowRate
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ComfoclimeDataUpdateCoordinator

SEASON_MAPPING = {0: "heating", 1: "shoulder", 2: "cooling"}
SEASON_OPTIONS = list(SEASON_MAPPING.values())

SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    "indoorTemperature": SensorEntityDescription(
        key="indoorTemperature",
        name="Indoor Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "outdoorTemperature": SensorEntityDescription(
        key="outdoorTemperature",
        name="Outdoor Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "exhaustAirFlow": SensorEntityDescription(
        key="exhaustAirFlow",
        name="Exhaust Air Flow",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-remove",
    ),
    "supplyAirFlow": SensorEntityDescription(
        key="supplyAirFlow",
        name="Supply Air Flow",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-add",
    ),
    "fanSpeed": SensorEntityDescription(
        key="fanSpeed",
        name="Fan Speed",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    "setPointTemperature": SensorEntityDescription(
        key="setPointTemperature",
        name="Setpoint Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "season": SensorEntityDescription(
        key="season",
        name="Season",
        icon="mdi:sun-snowflake",
        device_class=SensorDeviceClass.ENUM,
        options=SEASON_OPTIONS,
    ),
    "schedule": SensorEntityDescription(
        key="schedule",
        name="Schedule",
        icon="mdi:calendar-clock",
    ),
    "status": SensorEntityDescription(
        key="status",
        name="Status",
        icon="mdi:information-outline",
    ),
    "heatPumpStatus": SensorEntityDescription(
        key="heatPumpStatus",
        name="Heat Pump Status",
        icon="mdi:heat-pump-outline",
    ),
    "hpStandby": SensorEntityDescription(
        key="hpStandby",
        name="HP Standby",
        icon="mdi:power-sleep",
    ),
    "freeCoolingEnabled": SensorEntityDescription(
        key="freeCoolingEnabled",
        name="Free Cooling Enabled",
        icon="mdi:snowflake-thermometer",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Comfoclime sensor based on a config entry."""
    coordinator: ComfoclimeDataUpdateCoordinator = entry.runtime_data

    entities = []
    for uuid, device_data in coordinator.data.items():
        for key, description in SENSOR_DESCRIPTIONS.items():
            if key in device_data:
                if key == "season":
                    entities.append(
                        ComfoclimeSeasonSensor(coordinator, uuid, description)
                    )
                else:
                    entities.append(
                        ComfoclimeDashboardSensor(coordinator, uuid, description)
                    )
    async_add_entities(entities)


class ComfoclimeDashboardSensor(
    CoordinatorEntity[ComfoclimeDataUpdateCoordinator], SensorEntity
):
    """Representation of a Comfoclime Dashboard Sensor."""

    def __init__(
        self,
        coordinator: ComfoclimeDataUpdateCoordinator,
        uuid: str,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._uuid = uuid
        self._attr_unique_id = f"{uuid}_{entity_description.key}"
        self._attr_device_info = {"identifiers": {(DOMAIN, uuid)}}

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data[self._uuid].get(self.entity_description.key)


class ComfoclimeSeasonSensor(ComfoclimeDashboardSensor):
    """Representation of the Comfoclime Season Sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = self.coordinator.data[self._uuid].get(self.entity_description.key)
        return SEASON_MAPPING.get(value)
