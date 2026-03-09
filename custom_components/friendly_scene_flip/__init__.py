"""Friendly Scene Flip — toggle between two scene slots."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import DOMAIN, SLOT_A, SLOT_B

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["select"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Friendly Scene Flip from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register domain-level services (once)
    if not hass.services.has_service(DOMAIN, "toggle"):
        _register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    # Unregister services if no entries remain
    if not hass.data[DOMAIN]:
        for service in ("toggle", "set_scene", "activate"):
            hass.services.async_remove(DOMAIN, service)

    return unload_ok


def _get_entity(hass: HomeAssistant, call: ServiceCall):
    """Resolve target entity from service call."""
    entity_ids = call.data.get("entity_id", [])
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]

    entities = []
    for entry_id, entity in hass.data[DOMAIN].items():
        if entity.entity_id in entity_ids:
            entities.append(entity)

    return entities


SLOT_SCHEMA = vol.In([SLOT_A, SLOT_B])


def _register_services(hass: HomeAssistant) -> None:
    """Register domain services."""

    async def handle_toggle(call: ServiceCall) -> None:
        """Handle the toggle service."""
        for entity in _get_entity(hass, call):
            await entity.async_toggle()

    async def handle_set_scene(call: ServiceCall) -> None:
        """Handle the set_scene service."""
        slot = call.data["slot"]
        scene_entity_id = call.data["scene_entity_id"]
        for entity in _get_entity(hass, call):
            await entity.async_set_scene(slot, scene_entity_id)

    async def handle_activate(call: ServiceCall) -> None:
        """Handle the activate service."""
        slot = call.data["slot"]
        for entity in _get_entity(hass, call):
            await entity.async_activate(slot)

    hass.services.async_register(
        DOMAIN,
        "toggle",
        handle_toggle,
        schema=vol.Schema(
            {vol.Required("entity_id"): cv.entity_ids}
        ),
    )

    hass.services.async_register(
        DOMAIN,
        "set_scene",
        handle_set_scene,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_ids,
                vol.Required("slot"): SLOT_SCHEMA,
                vol.Required("scene_entity_id"): cv.entity_id,
            }
        ),
    )

    hass.services.async_register(
        DOMAIN,
        "activate",
        handle_activate,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_ids,
                vol.Required("slot"): SLOT_SCHEMA,
            }
        ),
    )
