"""Tests for the FriendlySceneFlipperSelect entity."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant, ServiceRegistry

from custom_components.friendly_scene_flipper.const import (
    ATTR_ACTIVE_SLOT,
    ATTR_SCENE_A,
    ATTR_SCENE_B,
    DOMAIN,
    SLOT_A,
    SLOT_B,
)


async def test_initial_state(hass: HomeAssistant, setup_entry) -> None:
    """Test entity has correct initial state."""
    state = hass.states.get("select.living_room_lights")
    assert state is not None
    assert state.state == "Daylight"
    assert state.attributes[ATTR_ACTIVE_SLOT] == SLOT_A
    assert state.attributes[ATTR_SCENE_A] == "scene.daylight"
    assert state.attributes[ATTR_SCENE_B] == "scene.all_lights_off"


async def test_options_list(hass: HomeAssistant, setup_entry) -> None:
    """Test that options list contains both scene friendly names."""
    state = hass.states.get("select.living_room_lights")
    assert state.attributes["options"] == ["Daylight", "All lights off"]


async def test_select_option(hass: HomeAssistant, setup_entry) -> None:
    """Test selecting an option activates the corresponding scene."""
    original_async_call = ServiceRegistry.async_call
    scene_calls = []

    async def _tracking_async_call(self, domain, service, service_data=None, **kw):
        if domain == "scene":
            scene_calls.append((domain, service, service_data))
            return
        return await original_async_call(self, domain, service, service_data, **kw)

    with patch.object(ServiceRegistry, "async_call", _tracking_async_call):
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": "select.living_room_lights", "option": "All lights off"},
            blocking=True,
        )

    state = hass.states.get("select.living_room_lights")
    assert state.attributes[ATTR_ACTIVE_SLOT] == SLOT_B


async def test_toggle_service(hass: HomeAssistant, setup_entry) -> None:
    """Test the toggle service switches between slots."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_toggle()

    assert entity._active_slot == SLOT_B

    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_toggle()

    assert entity._active_slot == SLOT_A


async def test_set_scene_reactivates_active_slot(hass: HomeAssistant, setup_entry) -> None:
    """Test set_scene reactivates when changing the active slot's scene."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    # Scene A is active, replace it
    hass.states.async_set("scene.evening", "scening", {"friendly_name": "Evening"})

    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_set_scene(SLOT_A, "scene.evening")

        # Should have called scene.turn_on with the new scene
        mock_call.assert_called_once_with("scene", "turn_on", {"entity_id": "scene.evening"}, blocking=True)

    assert entity._scene_a == "scene.evening"


async def test_set_scene_inactive_slot_no_activation(hass: HomeAssistant, setup_entry) -> None:
    """Test set_scene does NOT activate when changing an inactive slot."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    # Slot A is active, change slot B — should not trigger scene
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_set_scene(SLOT_B, "scene.night")

        mock_call.assert_not_called()

    assert entity._scene_b == "scene.night"


async def test_activate_service(hass: HomeAssistant, setup_entry) -> None:
    """Test the activate service explicitly sets a slot."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_activate(SLOT_B)

        mock_call.assert_called_once_with(
            "scene",
            "turn_on",
            {"entity_id": "scene.all_lights_off"},
            blocking=True,
        )

    assert entity._active_slot == SLOT_B
