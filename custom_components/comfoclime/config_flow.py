"""Config flow for Comfoclime."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import aiohttp_client

from .const import API_SYSTEMS, DEFAULT_PORT, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class ComfoclimeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow for Comfoclime."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            # Check if already configured
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            # Test connection
            try:
                session = aiohttp_client.async_get_clientsession(self.hass)
                systems_url = f"http://{host}:{port}{API_SYSTEMS}"

                async with session.get(
                    systems_url, timeout=DEFAULT_TIMEOUT
                ) as response:
                    if response.status == 200:
                        systems_data = await response.json()

                        if "systems" in systems_data and systems_data["systems"]:
                            # Connection successful, create entry
                            title = f"Comfoclime {host}"
                            if port != DEFAULT_PORT:
                                title += f":{port}"

                            return self.async_create_entry(
                                title=title,
                                data=user_input,
                            )
                        else:
                            errors["base"] = "no_systems_found"
                    else:
                        errors["base"] = "cannot_connect"

            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.error("Unexpected error: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
        )
