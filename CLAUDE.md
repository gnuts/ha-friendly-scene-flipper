# Friendly Scene Flipper — Project Conventions

## Overview
Home Assistant custom integration (`friendly_scene_flipper`) that toggles between two scene slots (A and B). A `select` entity provides the UI dropdown; services enable automation control.

## Structure
- `custom_components/friendly_scene_flipper/` — integration code
- `tests/` — pytest test suite using `pytest-homeassistant-custom-component`

## Code Style
- Follow Home Assistant development guidelines
- Use `from __future__ import annotations` in every module
- Type hints on all public functions
- Use `_LOGGER = logging.getLogger(__name__)` per module

## Git & Versioning
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- SemVer in `manifest.json` (0.x.0 during development, 1.0.0 at first release)
- Each functional set of changes gets its own commit

## Testing
- Run tests: `pytest tests/`
- Framework: `pytest-homeassistant-custom-component`

## Key Design Decisions
- `SelectEntity + RestoreEntity` — state = active scene friendly name, options = both scene names
- `RestoreEntity` restores slot state on restart **without** triggering `scene.turn_on`
- `asyncio.Lock()` per entity for safe concurrent service calls
- Services registered once per domain in `__init__.py`, not per config entry
