# Friendly Scene Flipper

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![HA Version](https://img.shields.io/badge/HA-2024.1.0+-green.svg)](https://www.home-assistant.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Home Assistant custom integration that toggles between two scene "slots". Think of it as a smart light switch — but instead of just on/off, each side can hold any scene, and automations can swap scenes in the background without interrupting you.

## What Does It Do?

Imagine you have a button that controls your living room lights. You set it up with two slots:

- **Slot A** — the "on" scene (e.g., "Daylight")
- **Slot B** — the "off" scene (e.g., "All Lights Off")

Press the button, lights come on. Press again, lights go off. Simple.

Now here's where it gets interesting. At 7 PM, an automation quietly swaps Slot A from "Daylight" to "Evening". If your lights are currently on, they smoothly transition to the evening scene. If they're off, nothing happens — the new scene just waits in Slot A for the next time you press the button.

At 11:30 PM, another automation swaps Slot A to "Candlelight". Same deal — if lights are on, they fade over. If not, the scene is ready for when you want it.

You never have to think about it. Toggle just works, and the right scene is always there.

## Installation

### HACS (Recommended)

1. Open **HACS** in your Home Assistant instance
2. Click the three-dot menu in the top right and select **Custom repositories**
3. Paste `https://github.com/gnuts/ha-friendly-scene-flipper` and select **Integration** as the category
4. Search for **Friendly Scene Flipper** and click **Install**
5. Restart Home Assistant

### Manual Installation

1. Download the latest release from the repository
2. Copy the `custom_components/friendly_scene_flipper/` folder into your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Setup

### Adding a Scene Flipper

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration** and search for **Friendly Scene Flipper**
3. Fill in the form:
   - **Name** — A friendly name (e.g., "Living Room Lights"). This becomes the entity ID (`select.living_room_lights`).
   - **Scene A** — Pick the scene for slot A (the initial "on" scene)
   - **Scene B** — Pick the scene for slot B (the initial "off" scene)
4. Click **Submit** — your scene flipper entity is ready to use

You can create as many scene flippers as you need — one per room, one per mood, whatever works for you.

### YAML Configuration (Alternative)

If you prefer `configuration.yaml` over the UI, you can set up scene flippers there instead:

```yaml
friendly_scene_flipper:
  - name: "Living Room Lights"
    scene_a: scene.daylight
    scene_b: scene.all_lights_off
  - name: "Bedroom"
    scene_a: scene.bedroom_bright
    scene_b: scene.bedroom_off
```

Restart Home Assistant after adding entries. Each YAML entry automatically creates a config entry — you can then manage it normally through the UI.

### Reconfiguring

To change scenes or set up flip lists after initial setup:

1. Go to **Settings** > **Devices & Services**
2. Find **Friendly Scene Flipper** and click **Configure** on the entry you want to change
3. You can update:
   - **Scene A** / **Scene B** — Change which scenes are in each slot
   - **Flip List A** / **Flip List B** — Pick scenes to cycle through (see [Flipper](#flipper--cycle-through-scenes) below)

## Usage

### The Dropdown

The simplest way to use your scene flipper — just pick a scene from the dropdown in the HA dashboard. It shows the friendly names of the two scenes, and selecting one activates it immediately. No automations needed.

### Entity Attributes

Each scene flipper entity exposes these attributes, which you can use in templates and automations:

| Attribute | Description |
|-----------|-------------|
| `active_slot` | Which slot is currently active (`a` or `b`) |
| `scene_a` | Entity ID of the scene in slot A |
| `scene_b` | Entity ID of the scene in slot B |
| `skip_a` | Whether the next activation of slot A will be skipped |
| `skip_b` | Whether the next activation of slot B will be skipped |
| `flip_list_a` | Scenes configured for flipping when slot A is active |
| `flip_list_b` | Scenes configured for flipping when slot B is active |
| `flip_index_a` | Current position in flip list A |
| `flip_index_b` | Current position in flip list B |

## Services

These services let you control your scene flipper from automations, scripts, and buttons.

### Toggle

**`friendly_scene_flipper.toggle`** — Switch between slot A and B.

If A is active, switches to B. If B is active, switches to A. This always works — it's never affected by skip flags.

```yaml
automation:
  - alias: "Toggle living room lights on button press"
    trigger:
      - trigger: event
        event_type: zha_event
        event_data:
          command: toggle
    action:
      - action: friendly_scene_flipper.toggle
        target:
          entity_id: select.living_room_lights
```

### Set Scene

**`friendly_scene_flipper.set_scene`** — Assign a scene to a slot. If that slot is currently active, the new scene activates right away (unless a [skip flag](#skipper--not-right-now-thanks) is armed).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `slot` | Yes | `a` or `b` |
| `scene_entity_id` | Yes | The scene entity to assign |

```yaml
automation:
  - alias: "Switch to evening scene at 7 PM"
    trigger:
      - trigger: time
        at: "19:00:00"
    action:
      - action: friendly_scene_flipper.set_scene
        target:
          entity_id: select.living_room_lights
        data:
          slot: a
          scene_entity_id: scene.evening
```

### Activate

**`friendly_scene_flipper.activate`** — Explicitly activate a specific slot without toggling.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `slot` | Yes | `a` or `b` |

```yaml
automation:
  - alias: "Activate slot A in the morning"
    trigger:
      - trigger: time
        at: "07:00:00"
    action:
      - action: friendly_scene_flipper.activate
        target:
          entity_id: select.living_room_lights
        data:
          slot: a
```

### Skip

**`friendly_scene_flipper.skip`** — Arm a one-shot skip flag. The next automatic activation of that slot will be silently skipped, and the flag resets automatically. Does **not** affect toggle or dropdown selection.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `slot` | Yes | `a`, `b`, or `both` |
| `enable` | Yes | `true` to arm the skip, `false` to clear it |

```yaml
automation:
  - alias: "Skip tonight's auto-switch"
    trigger:
      - trigger: event
        event_type: mobile_app_notification_action
        event_data:
          action: SKIP_TONIGHT
    action:
      - action: friendly_scene_flipper.skip
        target:
          entity_id: select.living_room_lights
        data:
          slot: both
          enable: true
```

### Flip Next / Flip Previous

**`friendly_scene_flipper.flip_next`** — Advance to the next scene in the active slot's flip list.

**`friendly_scene_flipper.flip_prev`** — Go to the previous scene in the active slot's flip list.

Both wrap around at the ends. If the flip list is empty, nothing happens. Activations respect [skip flags](#skipper--not-right-now-thanks).

```yaml
automation:
  - alias: "Cycle scenes on double press"
    trigger:
      - trigger: event
        event_type: zha_event
        event_data:
          command: double
    action:
      - action: friendly_scene_flipper.flip_next
        target:
          entity_id: select.living_room_lights
```

## Features in Depth

### Skipper — "Not Right Now, Thanks"

Sometimes you don't want the next scheduled scene change to happen. Maybe you're watching a movie and don't want the 9 PM "Night Mode" automation to kick in.

The **skip** service lets you arm a one-shot flag for a slot. Here's how it works:

- Call `friendly_scene_flipper.skip` with `enable: true` for the slot you want to skip
- The next time that slot would be activated (via `activate`, `set_scene`, `flip_next`, or `flip_prev`), it silently does nothing
- The flag resets automatically — the following activation works normally
- **Toggle and dropdown selection are never affected** by skip flags

It's a simple "not right now" button. One skip, then back to normal.

### Flipper — Cycle Through Scenes

Want a button that cycles through different lighting moods? The **Flipper** feature lets you configure a list of scenes for each slot and step through them.

**Setting it up:**

1. Go to **Settings** > **Devices & Services** > **Friendly Scene Flipper** > **Configure**
2. Add scenes to **Flip List A** and/or **Flip List B**
3. Use the `flip_next` or `flip_prev` services to cycle through them

**How it works:**

- Each slot has its own flip list and tracks its position independently
- `flip_next` moves forward, `flip_prev` moves backward
- The list wraps around — after the last scene, it goes back to the first
- Each flip replaces the slot's scene and activates it
- Leave a flip list empty to disable flipping for that slot

### Restart Persistence

Your scene flipper remembers everything across Home Assistant restarts — the active slot, assigned scenes, skip flags, and flip list positions. It restores quietly without triggering any scenes, so your lights won't unexpectedly turn on when HA reboots.

## Automation Recipes

Here are some practical examples to get you started.

### Daily Light Schedule

Set up different scenes throughout the day:

```yaml
automation:
  - alias: "Living Room — Daylight at 7 AM"
    trigger:
      - trigger: time
        at: "07:00:00"
    action:
      - action: friendly_scene_flipper.set_scene
        target:
          entity_id: select.living_room_lights
        data:
          slot: a
          scene_entity_id: scene.daylight

  - alias: "Living Room — Evening at 7 PM"
    trigger:
      - trigger: time
        at: "19:00:00"
    action:
      - action: friendly_scene_flipper.set_scene
        target:
          entity_id: select.living_room_lights
        data:
          slot: a
          scene_entity_id: scene.evening

  - alias: "Living Room — Night Mode at 11:30 PM"
    trigger:
      - trigger: time
        at: "23:30:00"
    action:
      - action: friendly_scene_flipper.set_scene
        target:
          entity_id: select.living_room_lights
        data:
          slot: a
          scene_entity_id: scene.candlelight
```

If the lights are on (slot A active), each change transitions smoothly. If they're off, the new scene waits quietly for the next toggle.

### Weekday-Only Schedule

Use conditions to restrict automations to workdays:

```yaml
automation:
  - alias: "Office — Bright Lights on Workdays"
    trigger:
      - trigger: time
        at: "08:30:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - action: friendly_scene_flipper.set_scene
        target:
          entity_id: select.office
        data:
          slot: a
          scene_entity_id: scene.bright_office
```

### Skip + Scheduled Changes

Pair the skip service with timed automations for a manual override:

```yaml
automation:
  - alias: "Skip tonight's auto-switch (long press)"
    trigger:
      - trigger: event
        event_type: zha_event
        event_data:
          command: hold
    action:
      - action: friendly_scene_flipper.skip
        target:
          entity_id: select.living_room_lights
        data:
          slot: both
          enable: true
```

When the evening automation fires and calls `activate` or `set_scene`, the skip flag suppresses the scene change for that one time. Tomorrow works normally.

### Rotate Through Scenes on a Schedule

Use `flip_next` with a time trigger for daily variety:

```yaml
automation:
  - alias: "Bedroom — New Scene Each Evening"
    trigger:
      - trigger: time
        at: "20:00:00"
    action:
      - action: friendly_scene_flipper.flip_next
        target:
          entity_id: select.bedroom
```

This steps through the flip list one scene per day, wrapping around at the end.

## Compatibility

- Home Assistant **2024.1.0** or later
- Available via [HACS](https://hacs.xyz) (custom repository)

## License

MIT License — see [LICENSE](LICENSE) for details.
