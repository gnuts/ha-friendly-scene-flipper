# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Primary hosting switched from GitLab to GitHub for HACS compatibility
- Makefile push targets updated for new remote layout

## [0.2.1] - 2026-03-10

### Changed

- Primary remote switched to GitLab; all project URLs updated
- Added `push`, `push-gitlab`, and `push-origin` Makefile targets

## [0.2.0] - 2026-03-10

### Added

- **Skipper**: one-shot skip of next automatic scene activation per slot
  (`friendly_scene_flipper.skip` service)
- **Flipper**: cycle through a configurable list of scenes per slot
  (`friendly_scene_flipper.flip_next` and `friendly_scene_flipper.flip_prev` services)
- Flip lists configurable via the options flow
- YAML configuration support with automatic config entry provisioning
- Security scanning with Trivy and Bandit

### Changed

- Renamed from "Friendly Scene Flip" to "Friendly Scene Flipper"
- Domain changed from `friendly_scene_flip` to `friendly_scene_flipper`

### Fixed

- Service schemas now accept extra keys for HA target selector compatibility
- `entity_id` made optional in service schemas for proper target support

## [0.1.0] - 2026-03-09

### Added

- Initial release
- Select entity with two scene slots (A and B)
- `toggle` service to switch between slots
- `set_scene` service to assign a scene to a slot (activates if currently active)
- `activate` service to explicitly activate a specific slot
- Config flow with name, Scene A, and Scene B entity pickers
- RestoreEntity support — state survives HA restarts without triggering scenes
- Dropdown displays scene friendly names
- Per-entity concurrency safety with asyncio.Lock

[Unreleased]: https://github.com/gnuts/ha-friendly-scene-flipper/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/gnuts/ha-friendly-scene-flipper/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/gnuts/ha-friendly-scene-flipper/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/gnuts/ha-friendly-scene-flipper/releases/tag/v0.1.0
