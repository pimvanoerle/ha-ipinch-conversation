"""Config flow: the bridge's turn URL, its token, and the device name it's told."""

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import CONF_DEVICE, CONF_TOKEN, CONF_URL, DEFAULT_DEVICE, DOMAIN, TIMEOUT_S, TOKEN_HEADER

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
        vol.Required(CONF_TOKEN): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
        vol.Required(CONF_DEVICE, default=DEFAULT_DEVICE): str,
    }
)


class IPinchConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            # An empty turn is answered with an empty reply, so it checks the URL and the
            # token without waking a brain.
            session = async_get_clientsession(self.hass)
            try:
                async with session.post(
                    user_input[CONF_URL],
                    json={"text": "", "device": user_input[CONF_DEVICE]},
                    headers={TOKEN_HEADER: user_input[CONF_TOKEN]},
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT_S),
                ) as resp:
                    if resp.status == 401:
                        errors["base"] = "invalid_auth"
                    elif resp.status != 200:
                        errors["base"] = "cannot_connect"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            if not errors:
                await self.async_set_unique_id(user_input[CONF_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="iPinch", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(SCHEMA, user_input),
            errors=errors,
        )
