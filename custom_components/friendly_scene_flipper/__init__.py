"""Friendly Scene Flipper — toggle between two scene slots."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, SLOT_A, SLOT_B, SLOT_BOTH

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["select"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Friendly Scene Flipper from a config entry."""
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
        for service in ("toggle", "set_scene", "activate", "skip", "flip_next", "flip_prev"):
            hass.services.async_remove(DOMAIN, service)

    return unload_ok


def _get_entity(hass: HomeAssistant, call: ServiceCall):
    """Resolve target entity from service call."""
    entity_ids = call.data.get("entity_id", [])
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]

    entities = []
    for _entry_id, entity in hass.data[DOMAIN].items():
        if entity.entity_id in entity_ids:
            entities.append(entity)

    return entities


SLOT_SCHEMA = vol.In([SLOT_A, SLOT_B])
SLOT_WITH_BOTH_SCHEMA = vol.In([SLOT_A, SLOT_B, SLOT_BOTH])


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

    async def handle_skip(call: ServiceCall) -> None:
        """Handle the skip service."""
        slot = call.data["slot"]
        enable = call.data["enable"]
        for entity in _get_entity(hass, call):
            await entity.async_skip(slot, enable)

    async def handle_flip_next(call: ServiceCall) -> None:
        """Handle the flip_next service."""
        for entity in _get_entity(hass, call):
            await entity.async_flip_next()

    async def handle_flip_prev(call: ServiceCall) -> None:
        """Handle the flip_prev service."""
        for entity in _get_entity(hass, call):
            await entity.async_flip_prev()

    hass.services.async_register(
        DOMAIN,
        "toggle",
        handle_toggle,
        schema=vol.Schema({vol.Required("entity_id"): cv.entity_ids}),
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

    hass.services.async_register(
        DOMAIN,
        "skip",
        handle_skip,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_ids,
                vol.Required("slot"): SLOT_WITH_BOTH_SCHEMA,
                vol.Required("enable"): cv.boolean,
            }
        ),
    )

    entity_id_schema = vol.Schema({vol.Required("entity_id"): cv.entity_ids})

    hass.services.async_register(
        DOMAIN,
        "flip_next",
        handle_flip_next,
        schema=entity_id_schema,
    )

    hass.services.async_register(
        DOMAIN,
        "flip_prev",
        handle_flip_prev,
        schema=entity_id_schema,
    )
