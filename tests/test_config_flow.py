"""Tests for the Friendly Scene Flipper config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component

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


async def test_import_flow(hass: HomeAssistant) -> None:
    """Test importing a config entry from configuration.yaml."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data={
            "name": "testflip",
            CONF_SCENE_A: "scene.day_mode",
            CONF_SCENE_B: "scene.night_mode",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "testflip"
    assert result["data"]["name"] == "testflip"
    assert result["data"][CONF_SCENE_A] == "scene.day_mode"
    assert result["data"][CONF_SCENE_B] == "scene.night_mode"


async def test_import_flow_duplicate(hass: HomeAssistant) -> None:
    """Test that importing a duplicate entry is silently aborted."""
    import_data = {
        "name": "testflip",
        CONF_SCENE_A: "scene.day_mode",
        CONF_SCENE_B: "scene.night_mode",
    }

    # First import succeeds
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data=import_data,
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY

    # Second import with same name aborts
    result2 = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data=import_data,
    )
    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_async_setup_triggers_import(hass: HomeAssistant) -> None:
    """Test that async_setup fires import flows for each YAML entry."""
    config = {
        DOMAIN: [
            {
                "name": "testflip",
                CONF_SCENE_A: "scene.day_mode",
                CONF_SCENE_B: "scene.night_mode",
            },
        ],
    }

    with patch("homeassistant.config_entries.ConfigEntriesFlowManager.async_init") as mock_init:
        mock_init.return_value = {"type": FlowResultType.CREATE_ENTRY}
        await async_setup_component(hass, DOMAIN, config)
        await hass.async_block_till_done()

    mock_init.assert_called_once_with(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data=config[DOMAIN][0],
    )


async def test_async_setup_no_config(hass: HomeAssistant) -> None:
    """Test that async_setup returns True when domain not in config."""
    with patch("homeassistant.config_entries.ConfigEntriesFlowManager.async_init") as mock_init:
        await async_setup_component(hass, DOMAIN, {})
        await hass.async_block_till_done()

    mock_init.assert_not_called()
