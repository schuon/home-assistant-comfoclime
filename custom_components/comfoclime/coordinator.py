"""Data coordinator for Comfoclime."""

from __future__ import annotations

import logging
from typing import Any
from datetime import timedelta

import aiohttp
from aiohttp import ClientTimeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import API_SYSTEMS, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ComfoclimeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Comfoclime data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.host = entry.data["host"]
        self.port = entry.data.get("port", 80)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=300),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via Comfoclime API."""
        session = aiohttp_client.async_get_clientsession(self.hass)

        try:
            timeout = ClientTimeout(total=DEFAULT_TIMEOUT)

            # 1. Get system information
            systems_url = f"http://{self.host}:{self.port}{API_SYSTEMS}"
            _LOGGER.debug("Fetching systems data from %s", systems_url)

            async with session.get(systems_url, timeout=timeout) as response:
                response.raise_for_status()
                systems_response = await response.json()
                _LOGGER.debug("Received systems data: %s", systems_response)

            # 2. Get dashboard data for each system
            all_data = {}
            for system in systems_response.get("systems", []):
                uuid = system.get("uuid")
                if not uuid:
                    continue

                dashboard_url = (
                    f"http://{self.host}:{self.port}/system/{uuid}/dashboard"
                )
                _LOGGER.debug("Fetching dashboard data from %s", dashboard_url)

                async with session.get(
                    dashboard_url, timeout=timeout
                ) as dashboard_response:
                    dashboard_response.raise_for_status()
                    dashboard_data = await dashboard_response.json()
                    _LOGGER.debug(
                        "Received dashboard data for %s: %s", uuid, dashboard_data
                    )

                # 3. Merge system and dashboard data
                all_data[uuid] = {**system, **dashboard_data}

            return all_data

        except aiohttp.ClientError as err:
            _LOGGER.error("Error communicating with Comfoclime: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise
