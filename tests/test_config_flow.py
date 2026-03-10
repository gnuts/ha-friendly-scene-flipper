"""Tests for the Friendly Scene Flipper config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.friendly_scene_flipper.const import CONF_SCENE_A, CONF_SCENE_B, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def test_user_flow(hass: HomeAssistant) -> None:
    """Test the full user config flow."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Living Room",
            CONF_SCENE_A: "scene.daylight",
            CONF_SCENE_B: "scene.all_lights_off",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living Room"
    assert result["data"][CONF_SCENE_A] == "scene.daylight"
    assert result["data"][CONF_SCENE_B] == "scene.all_lights_off"


async def test_duplicate_entry(hass: HomeAssistant) -> None:
    """Test that duplicate names are rejected."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Living Room",
            CONF_SCENE_A: "scene.daylight",
            CONF_SCENE_B: "scene.all_lights_off",
        },
    )

    # Try to add another with the same name
    result2 = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            "name": "Living Room",
            CONF_SCENE_A: "scene.evening",
            CONF_SCENE_B: "scene.night",
        },
    )
    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "already_configured"
