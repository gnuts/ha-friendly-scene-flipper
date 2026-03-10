"""Tests for the Skipper feature (skip next automatic scene change)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant, ServiceRegistry

from custom_components.friendly_scene_flipper.const import (
    ATTR_SKIP_A,
    ATTR_SKIP_B,
    DOMAIN,
    SLOT_A,
    SLOT_B,
)


async def test_initial_skip_flags_false(hass: HomeAssistant, setup_entry) -> None:
    """Test that skip flags start as False."""
    state = hass.states.get("select.living_room_lights")
    assert state.attributes[ATTR_SKIP_A] is False
    assert state.attributes[ATTR_SKIP_B] is False


async def test_skip_a_suppresses_set_scene(hass: HomeAssistant, setup_entry) -> None:
    """Test that skip_a suppresses activation when set_scene targets active slot A."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    # Arm skip for slot A
    await entity.async_skip(SLOT_A, True)
    assert entity._skip_a is True

    # set_scene on active slot A should be suppressed
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_set_scene(SLOT_A, "scene.evening")
        mock_call.assert_not_called()

    # Scene should still be assigned
    assert entity._scene_a == "scene.evening"
    # Skip flag should be reset (one-shot)
    assert entity._skip_a is False


async def test_skip_b_suppresses_activate(hass: HomeAssistant, setup_entry) -> None:
    """Test that skip_b suppresses activation when activate targets slot B."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    # Arm skip for slot B
    await entity.async_skip(SLOT_B, True)
    assert entity._skip_b is True

    # Activate slot B — should switch slot but suppress scene.turn_on
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_activate(SLOT_B)
        mock_call.assert_not_called()

    assert entity._active_slot == SLOT_B
    # Skip flag should be reset
    assert entity._skip_b is False


async def test_skip_does_not_affect_toggle(hass: HomeAssistant, setup_entry) -> None:
    """Test that toggle always activates regardless of skip flags."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    # Arm skip for both slots
    await entity.async_skip("both", True)

    # Toggle should still call scene.turn_on (check_skip=False)
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_toggle()
        mock_call.assert_called_once()

    assert entity._active_slot == SLOT_B
    # Skip flags should NOT be consumed by toggle
    assert entity._skip_b is True


async def test_skip_does_not_affect_dropdown(hass: HomeAssistant, setup_entry) -> None:
    """Test that dropdown selection always activates regardless of skip flags."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    # Arm skip for slot B
    await entity.async_skip(SLOT_B, True)

    # Select "All lights off" (slot B) via dropdown
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

    # scene.turn_on should have been called (skip not consumed)
    assert len(scene_calls) == 1
    # Skip flag should NOT be consumed
    assert entity._skip_b is True


async def test_skip_one_shot_reset(hass: HomeAssistant, setup_entry) -> None:
    """Test that skip resets after one skipped activation."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    await entity.async_skip(SLOT_A, True)

    # First set_scene: skipped
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_set_scene(SLOT_A, "scene.evening")
        mock_call.assert_not_called()

    assert entity._skip_a is False

    # Second set_scene: NOT skipped (flag was reset)
    hass.states.async_set("scene.bright", "scening", {"friendly_name": "Bright"})
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_set_scene(SLOT_A, "scene.bright")
        mock_call.assert_called_once()


async def test_skip_both_sets_both_flags(hass: HomeAssistant, setup_entry) -> None:
    """Test that slot='both' sets both skip flags."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    await entity.async_skip("both", True)
    assert entity._skip_a is True
    assert entity._skip_b is True


async def test_clear_skip(hass: HomeAssistant, setup_entry) -> None:
    """Test that enable=False clears skip flags."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    await entity.async_skip("both", True)
    assert entity._skip_a is True
    assert entity._skip_b is True

    await entity.async_skip("both", False)
    assert entity._skip_a is False
    assert entity._skip_b is False


async def test_skip_attributes_exposed(hass: HomeAssistant, setup_entry) -> None:
    """Test that skip attributes are visible in entity state."""
    entity = hass.data[DOMAIN][setup_entry.entry_id]

    await entity.async_skip(SLOT_A, True)

    state = hass.states.get("select.living_room_lights")
    assert state.attributes[ATTR_SKIP_A] is True
    assert state.attributes[ATTR_SKIP_B] is False
