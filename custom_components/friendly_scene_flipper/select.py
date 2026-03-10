"""Select entity for Friendly Scene Flipper."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_NAME
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    ATTR_ACTIVE_SLOT,
    ATTR_FLIP_INDEX_A,
    ATTR_FLIP_INDEX_B,
    ATTR_FLIP_LIST_A,
    ATTR_FLIP_LIST_B,
    ATTR_SCENE_A,
    ATTR_SCENE_B,
    ATTR_SKIP_A,
    ATTR_SKIP_B,
    CONF_FLIP_LIST_A,
    CONF_FLIP_LIST_B,
    CONF_SCENE_A,
    CONF_SCENE_B,
    DOMAIN,
    SLOT_A,
    SLOT_B,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Friendly Scene Flipper select entity."""
    entity = FriendlySceneFlipperSelect(config_entry)
    async_add_entities([entity])

    # Store entity reference for service handlers
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = entity


def _scene_friendly_name(hass: HomeAssistant, entity_id: str) -> str:
    """Get the friendly name of a scene, falling back to entity_id."""
    state = hass.states.get(entity_id)
    if state is not None:
        return state.attributes.get("friendly_name", entity_id)
    # Strip "scene." prefix as a reasonable fallback
    return entity_id.removeprefix("scene.")


class FriendlySceneFlipperSelect(SelectEntity, RestoreEntity):
    """A select entity that toggles between two scene slots."""

    _attr_has_entity_name = True

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the scene flipper select entity."""
        self._config_entry = config_entry
        self._scene_a: str = config_entry.data[CONF_SCENE_A]
        self._scene_b: str = config_entry.data[CONF_SCENE_B]
        self._active_slot: str = SLOT_A
        self._skip_a: bool = False
        self._skip_b: bool = False
        self._lock = asyncio.Lock()

        # Flip lists from options (not initial config)
        self._flip_list_a: list[str] = list(config_entry.options.get(CONF_FLIP_LIST_A, []))
        self._flip_list_b: list[str] = list(config_entry.options.get(CONF_FLIP_LIST_B, []))
        self._flip_index_a: int = 0
        self._flip_index_b: int = 0

        self._attr_unique_id = config_entry.entry_id
        self._attr_name = config_entry.data.get(CONF_NAME, "Scene Flipper")

    @property
    def options(self) -> list[str]:
        """Return the list of selectable options (scene friendly names)."""
        if self.hass is None:
            return [self._scene_a, self._scene_b]
        name_a = _scene_friendly_name(self.hass, self._scene_a)
        name_b = _scene_friendly_name(self.hass, self._scene_b)
        return [name_a, name_b]

    @property
    def current_option(self) -> str | None:
        """Return the friendly name of the currently active scene."""
        if self.hass is None:
            return None
        entity_id = self._scene_a if self._active_slot == SLOT_A else self._scene_b
        return _scene_friendly_name(self.hass, entity_id)

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        return {
            ATTR_ACTIVE_SLOT: self._active_slot,
            ATTR_SCENE_A: self._scene_a,
            ATTR_SCENE_B: self._scene_b,
            ATTR_SKIP_A: self._skip_a,
            ATTR_SKIP_B: self._skip_b,
            ATTR_FLIP_LIST_A: self._flip_list_a,
            ATTR_FLIP_LIST_B: self._flip_list_b,
            ATTR_FLIP_INDEX_A: self._flip_index_a,
            ATTR_FLIP_INDEX_B: self._flip_index_b,
        }

    def _clamp_flip_indices(self) -> None:
        """Clamp flip indices to valid bounds after list changes."""
        if self._flip_list_a:
            self._flip_index_a = min(self._flip_index_a, len(self._flip_list_a) - 1)
        else:
            self._flip_index_a = 0
        if self._flip_list_b:
            self._flip_index_b = min(self._flip_index_b, len(self._flip_list_b) - 1)
        else:
            self._flip_index_b = 0

    async def async_added_to_hass(self) -> None:
        """Restore state on startup without triggering scenes."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            restored_slot = last_state.attributes.get(ATTR_ACTIVE_SLOT, SLOT_A)
            if restored_slot in (SLOT_A, SLOT_B):
                self._active_slot = restored_slot

            restored_a = last_state.attributes.get(ATTR_SCENE_A)
            if restored_a:
                self._scene_a = restored_a

            restored_b = last_state.attributes.get(ATTR_SCENE_B)
            if restored_b:
                self._scene_b = restored_b

            self._skip_a = bool(last_state.attributes.get(ATTR_SKIP_A, False))
            self._skip_b = bool(last_state.attributes.get(ATTR_SKIP_B, False))

            # Restore flip indices
            self._flip_index_a = int(last_state.attributes.get(ATTR_FLIP_INDEX_A, 0))
            self._flip_index_b = int(last_state.attributes.get(ATTR_FLIP_INDEX_B, 0))
            self._clamp_flip_indices()

            _LOGGER.debug(
                "Restored %s: active_slot=%s, scene_a=%s, scene_b=%s, skip_a=%s, skip_b=%s",
                self.entity_id,
                self._active_slot,
                self._scene_a,
                self._scene_b,
                self._skip_a,
                self._skip_b,
            )

        # Listen for options flow updates
        self.async_on_remove(self._config_entry.add_update_listener(self._async_options_updated))

    @staticmethod
    async def _async_options_updated(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Handle options flow updates."""
        await hass.config_entries.async_reload(config_entry.entry_id)

    async def async_select_option(self, option: str) -> None:
        """Handle the user selecting an option (scene name) from the dropdown."""
        async with self._lock:
            # Determine which slot matches the selected option
            name_a = _scene_friendly_name(self.hass, self._scene_a)
            if option == name_a:
                self._active_slot = SLOT_A
            else:
                self._active_slot = SLOT_B

            await self._activate_current_slot(check_skip=False)

    def _should_skip_slot(self) -> bool:
        """Check if the current slot's skip flag is set, and reset it if so."""
        if self._active_slot == SLOT_A and self._skip_a:
            self._skip_a = False
            return True
        if self._active_slot == SLOT_B and self._skip_b:
            self._skip_b = False
            return True
        return False

    async def _activate_current_slot(self, *, check_skip: bool = False) -> None:
        """Activate the scene in the current active slot."""
        scene_id = self._scene_a if self._active_slot == SLOT_A else self._scene_b

        if check_skip and self._should_skip_slot():
            _LOGGER.debug("Skipping activation of slot %s → %s (skip flag was set)", self._active_slot, scene_id)
            self.async_write_ha_state()
            return

        _LOGGER.debug("Activating slot %s → %s", self._active_slot, scene_id)
        await self.hass.services.async_call("scene", "turn_on", {"entity_id": scene_id}, blocking=True)
        self.async_write_ha_state()

    async def async_toggle(self) -> None:
        """Toggle between slot A and B."""
        async with self._lock:
            self._active_slot = SLOT_B if self._active_slot == SLOT_A else SLOT_A
            await self._activate_current_slot(check_skip=False)

    async def async_set_scene(self, slot: str, scene_entity_id: str) -> None:
        """Assign a scene to a slot, reactivating if the slot is currently active."""
        async with self._lock:
            if slot == SLOT_A:
                self._scene_a = scene_entity_id
            else:
                self._scene_b = scene_entity_id

            _LOGGER.debug("Set slot %s → %s", slot, scene_entity_id)

            if self._active_slot == slot:
                await self._activate_current_slot(check_skip=True)
            else:
                self.async_write_ha_state()

    async def async_activate(self, slot: str) -> None:
        """Explicitly activate a specific slot."""
        async with self._lock:
            self._active_slot = slot
            await self._activate_current_slot(check_skip=True)

    async def async_skip(self, slot: str, enable: bool) -> None:
        """Set or clear the skip flag for a slot."""
        async with self._lock:
            if slot in (SLOT_A, "both"):
                self._skip_a = enable
            if slot in (SLOT_B, "both"):
                self._skip_b = enable

            _LOGGER.debug("Skip flags: skip_a=%s, skip_b=%s", self._skip_a, self._skip_b)
            self.async_write_ha_state()

    async def async_flip_next(self) -> None:
        """Advance to the next scene in the active slot's flip list."""
        async with self._lock:
            await self._flip(direction=1)

    async def async_flip_prev(self) -> None:
        """Go to the previous scene in the active slot's flip list."""
        async with self._lock:
            await self._flip(direction=-1)

    async def _flip(self, *, direction: int) -> None:
        """Cycle through the flip list for the active slot."""
        flip_list = self._flip_list_a if self._active_slot == SLOT_A else self._flip_list_b

        if not flip_list:
            _LOGGER.warning("Flip list for slot %s is empty, nothing to do", self._active_slot)
            return

        if self._active_slot == SLOT_A:
            self._flip_index_a = (self._flip_index_a + direction) % len(flip_list)
            self._scene_a = flip_list[self._flip_index_a]
        else:
            self._flip_index_b = (self._flip_index_b + direction) % len(flip_list)
            self._scene_b = flip_list[self._flip_index_b]

        _LOGGER.debug(
            "Flip slot %s → index %d → %s",
            self._active_slot,
            self._flip_index_a if self._active_slot == SLOT_A else self._flip_index_b,
            self._scene_a if self._active_slot == SLOT_A else self._scene_b,
        )

        await self._activate_current_slot(check_skip=True)
