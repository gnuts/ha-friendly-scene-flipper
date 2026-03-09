"""Shared test fixtures for Friendly Scene Flip."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant.core import HomeAssistant

from custom_components.friendly_scene_flip.const import (
    CONF_SCENE_A,
    CONF_SCENE_B,
    DOMAIN,
)

pytest_plugins = "pytest_homeassistant_custom_component"

MOCK_CONFIG = {
    "name": "Living Room Lights",
    CONF_SCENE_A: "scene.daylight",
    CONF_SCENE_B: "scene.all_lights_off",
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in all tests."""
    yield


@pytest.fixture
async def setup_entry(hass: HomeAssistant):
    """Create and set up a config entry."""
    from homeassistant.config_entries import ConfigEntry

    entry = ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Living Room Lights",
        data=MOCK_CONFIG.copy(),
        source="user",
        unique_id="Living Room Lights",
    )
    entry.add_to_hass(hass)

    # Set up mock scene states so friendly name resolution works
    hass.states.async_set(
        "scene.daylight", "scening", {"friendly_name": "Daylight"}
    )
    hass.states.async_set(
        "scene.all_lights_off",
        "scening",
        {"friendly_name": "All lights off"},
    )

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry
