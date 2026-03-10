"""Tests for domain-level services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.friendly_scene_flipper.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def test_toggle_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the toggle service is registered."""
    assert hass.services.has_service(DOMAIN, "toggle")


async def test_set_scene_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the set_scene service is registered."""
    assert hass.services.has_service(DOMAIN, "set_scene")


async def test_activate_service_registered(hass: HomeAssistant, setup_entry) -> None:
    """Test that the activate service is registered."""
    assert hass.services.has_service(DOMAIN, "activate")


async def test_services_removed_on_unload(hass: HomeAssistant, setup_entry) -> None:
    """Test that services are removed when the last entry is unloaded."""
    await hass.config_entries.async_unload(setup_entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, "toggle")
    assert not hass.services.has_service(DOMAIN, "set_scene")
    assert not hass.services.has_service(DOMAIN, "activate")
