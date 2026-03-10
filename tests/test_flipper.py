"""Tests for the Flipper feature (cycle through scene lists)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant, ServiceRegistry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.friendly_scene_flipper.const import (
    ATTR_FLIP_INDEX_A,
    ATTR_FLIP_INDEX_B,
    ATTR_FLIP_LIST_A,
    ATTR_FLIP_LIST_B,
    CONF_FLIP_LIST_A,
    CONF_FLIP_LIST_B,
    CONF_SCENE_A,
    CONF_SCENE_B,
    DOMAIN,
    SLOT_A,
    SLOT_B,
)

FLIP_SCENES = ["scene.day_mode", "scene.night_mode", "scene.movie_time"]


async def _setup_with_flip_lists(hass: HomeAssistant, flip_a: list[str], flip_b: list[str]):
    """Set up an entry with flip lists configured via options."""
    entry = MockConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Flip Test",
        data={
            "name": "Flip Test",
            CONF_SCENE_A: "scene.daylight",
            CONF_SCENE_B: "scene.all_lights_off",
        },
        options={
            CONF_FLIP_LIST_A: flip_a,
            CONF_FLIP_LIST_B: flip_b,
        },
        source="user",
        unique_id="Flip Test",
    )
    entry.add_to_hass(hass)

    # Set up mock scene states
    hass.states.async_set("scene.daylight", "scening", {"friendly_name": "Daylight"})
    hass.states.async_set("scene.all_lights_off", "scening", {"friendly_name": "All lights off"})
    for scene_id in flip_a + flip_b:
        name = scene_id.removeprefix("scene.").replace("_", " ").title()
        hass.states.async_set(scene_id, "scening", {"friendly_name": name})

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry


async def test_flip_next_advances_and_activates(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test flip_next advances the index and changes the scene."""
    entry = await _setup_with_flip_lists(hass, FLIP_SCENES, [])
    entity = hass.data[DOMAIN][entry.entry_id]

    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_flip_next()
        mock_call.assert_called_once_with("scene", "turn_on", {"entity_id": "scene.night_mode"}, blocking=True)

    assert entity._flip_index_a == 1
    assert entity._scene_a == "scene.night_mode"


async def test_flip_next_wraps_around(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test flip_next wraps to the beginning when reaching the end."""
    entry = await _setup_with_flip_lists(hass, FLIP_SCENES, [])
    entity = hass.data[DOMAIN][entry.entry_id]

    # Advance to end of list
    for _ in range(3):
        with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
            await entity.async_flip_next()

    # Should wrap to index 0
    assert entity._flip_index_a == 0
    assert entity._scene_a == "scene.day_mode"


async def test_flip_prev_decrements(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test flip_prev goes to the previous scene."""
    entry = await _setup_with_flip_lists(hass, FLIP_SCENES, [])
    entity = hass.data[DOMAIN][entry.entry_id]

    # First go forward to index 2
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_flip_next()
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_flip_next()

    assert entity._flip_index_a == 2

    # Now go back
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_flip_prev()

    assert entity._flip_index_a == 1
    assert entity._scene_a == "scene.night_mode"


async def test_flip_prev_wraps_around(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test flip_prev wraps to the end from index 0."""
    entry = await _setup_with_flip_lists(hass, FLIP_SCENES, [])
    entity = hass.data[DOMAIN][entry.entry_id]

    # At index 0, go backward
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_flip_prev()

    assert entity._flip_index_a == 2
    assert entity._scene_a == "scene.movie_time"


async def test_flip_empty_list_does_nothing(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test that flipping with an empty list logs a warning and does nothing."""
    entry = await _setup_with_flip_lists(hass, [], [])
    entity = hass.data[DOMAIN][entry.entry_id]

    original_scene = entity._scene_a

    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_flip_next()
        mock_call.assert_not_called()

    assert entity._scene_a == original_scene


async def test_flip_operates_on_active_slot(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test that flip operates on the active slot only."""
    entry = await _setup_with_flip_lists(hass, FLIP_SCENES, ["scene.bright_lights", "scene.dim_lights"])
    entity = hass.data[DOMAIN][entry.entry_id]

    # Set up extra scenes
    hass.states.async_set("scene.bright_lights", "scening", {"friendly_name": "Bright Lights"})
    hass.states.async_set("scene.dim_lights", "scening", {"friendly_name": "Dim Lights"})

    # Switch to slot B
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_activate(SLOT_B)

    # Flip next should operate on slot B's list
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_flip_next()
        mock_call.assert_called_once_with("scene", "turn_on", {"entity_id": "scene.dim_lights"}, blocking=True)

    assert entity._flip_index_b == 1
    assert entity._scene_b == "scene.dim_lights"
    # Slot A should be unchanged
    assert entity._flip_index_a == 0


async def test_flip_respects_skip(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test that flip respects the skip flag."""
    entry = await _setup_with_flip_lists(hass, FLIP_SCENES, [])
    entity = hass.data[DOMAIN][entry.entry_id]

    # Arm skip for slot A
    await entity.async_skip(SLOT_A, True)

    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock) as mock_call:
        await entity.async_flip_next()
        # scene.turn_on should NOT be called (skipped)
        mock_call.assert_not_called()

    # Index should still advance
    assert entity._flip_index_a == 1
    assert entity._scene_a == "scene.night_mode"
    # Skip flag should be consumed
    assert entity._skip_a is False


async def test_flip_attributes_exposed(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test that flip attributes are visible in entity state."""
    await _setup_with_flip_lists(hass, FLIP_SCENES, [])

    state = hass.states.get("select.flip_test")
    assert state.attributes[ATTR_FLIP_LIST_A] == FLIP_SCENES
    assert state.attributes[ATTR_FLIP_LIST_B] == []
    assert state.attributes[ATTR_FLIP_INDEX_A] == 0
    assert state.attributes[ATTR_FLIP_INDEX_B] == 0


async def test_flip_index_clamped_on_shorter_list(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test that flip index is clamped when list shrinks on reload."""
    entry = await _setup_with_flip_lists(hass, FLIP_SCENES, [])
    entity = hass.data[DOMAIN][entry.entry_id]

    # Advance to index 2
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_flip_next()
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_flip_next()

    assert entity._flip_index_a == 2

    # Simulate a shorter list via direct update
    entity._flip_list_a = ["scene.day_mode"]
    entity._clamp_flip_indices()

    assert entity._flip_index_a == 0


async def test_flip_restore_indices(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test that flip indices are restored from state on startup."""
    entry = await _setup_with_flip_lists(hass, FLIP_SCENES, ["scene.bright_lights"])
    entity = hass.data[DOMAIN][entry.entry_id]

    hass.states.async_set("scene.bright_lights", "scening", {"friendly_name": "Bright Lights"})

    # Advance index
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_flip_next()
    with patch.object(ServiceRegistry, "async_call", new_callable=AsyncMock):
        await entity.async_flip_next()

    assert entity._flip_index_a == 2

    # Check that the attribute is exposed (used by RestoreEntity for persistence)
    state = hass.states.get("select.flip_test")
    assert state.attributes[ATTR_FLIP_INDEX_A] == 2
    assert state.attributes[ATTR_FLIP_INDEX_B] == 0


async def test_options_flow_saves_flip_lists(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test that the options flow saves flip list configuration."""
    entry = await _setup_with_flip_lists(hass, [], [])

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_SCENE_A: "scene.daylight",
            CONF_SCENE_B: "scene.all_lights_off",
            CONF_FLIP_LIST_A: ["scene.day_mode", "scene.night_mode"],
            CONF_FLIP_LIST_B: ["scene.movie_time"],
        },
    )

    assert result["type"] == "create_entry"
    assert entry.options[CONF_FLIP_LIST_A] == ["scene.day_mode", "scene.night_mode"]
    assert entry.options[CONF_FLIP_LIST_B] == ["scene.movie_time"]
