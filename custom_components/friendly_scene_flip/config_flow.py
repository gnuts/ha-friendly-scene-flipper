"""Config flow for Friendly Scene Flip."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import CONF_SCENE_A, CONF_SCENE_B, DOMAIN


class FriendlySceneFlipConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Friendly Scene Flip."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_NAME])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_SCENE_A): EntitySelector(
                        EntitySelectorConfig(domain="scene"),
                    ),
                    vol.Required(CONF_SCENE_B): EntitySelector(
                        EntitySelectorConfig(domain="scene"),
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow."""
        return FriendlySceneFlipOptionsFlow(config_entry)


class FriendlySceneFlipOptionsFlow(OptionsFlow):
    """Handle options flow for Friendly Scene Flip."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCENE_A,
                        default=self.config_entry.data.get(CONF_SCENE_A),
                    ): EntitySelector(
                        EntitySelectorConfig(domain="scene"),
                    ),
                    vol.Required(
                        CONF_SCENE_B,
                        default=self.config_entry.data.get(CONF_SCENE_B),
                    ): EntitySelector(
                        EntitySelectorConfig(domain="scene"),
                    ),
                }
            ),
        )
