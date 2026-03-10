"""Tests for domain-level services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.friendly_scene_flipper.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

ALL_SERVICES = ("toggle", "set_scene", "activate", "skip", "flip_next", "flip_prev")


async def test_toggle_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the toggle service is registered."""
    assert hass.services.has_service(DOMAIN, "toggle")


async def test_set_scene_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the set_scene service is registered."""
    assert hass.services.has_service(DOMAIN, "set_scene")


async def test_activate_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the activate service is registered."""
    assert hass.services.has_service(DOMAIN, "activate")


async def test_skip_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the skip service is registered."""
    assert hass.services.has_service(DOMAIN, "skip")


async def test_flip_next_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the flip_next service is registered."""
    assert hass.services.has_service(DOMAIN, "flip_next")


async def test_flip_prev_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the flip_prev service is registered."""
    assert hass.services.has_service(DOMAIN, "flip_prev")


async def test_all_services_removed_on_unload(hass: HomeAssistant, setup_entry) -> None:
    """Test that all services are removed when the last entry is unloaded."""
    await hass.config_entries.async_unload(setup_entry.entry_id)
    await hass.async_block_till_done()

    for service in ALL_SERVICES:
        assert not hass.services.has_service(DOMAIN, service), f"{service} should be removed"
