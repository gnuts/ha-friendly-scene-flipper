# TimePoints — Scheduled Scene Changes with HA Automations

TimePoints are scheduled moments when your Scene Flipper automatically changes scenes. Rather than building a custom scheduler, Friendly Scene Flipper relies on Home Assistant's built-in automation engine — which is already great at this.

## The Idea

You have a Scene Flipper that toggles between "Day Mode" and "Night Mode". You want it to automatically switch to Day Mode at 7:00 AM and Night Mode at 9:00 PM. Each of those scheduled times is a **TimePoint**.

## Basic Example: Morning and Evening Switch

```yaml
automation:
  - alias: "Living Room — Day Mode at 7 AM"
    trigger:
      - trigger: time
        at: "07:00:00"
    action:
      - action: friendly_scene_flipper.set_scene
        data:
          entity_id: select.living_room_lights
          slot: a
          scene_entity_id: scene.daylight
      - action: friendly_scene_flipper.activate
        data:
          entity_id: select.living_room_lights
          slot: a

  - alias: "Living Room — Night Mode at 9 PM"
    trigger:
      - trigger: time
        at: "21:00:00"
    action:
      - action: friendly_scene_flipper.activate
        data:
          entity_id: select.living_room_lights
          slot: b
```

The first automation both assigns a scene _and_ activates — handy if you want the TimePoint to also update what scene is in the slot. The second just activates whatever scene is already in slot B.

## Weekday-Only Schedule

Use conditions to restrict when TimePoints fire:

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
        data:
          entity_id: select.office
          slot: a
          scene_entity_id: scene.bright_office
      - action: friendly_scene_flipper.activate
        data:
          entity_id: select.office
          slot: a
```

## Combining with Skipper: "Don't Auto-Switch Tonight"

The Skipper feature pairs nicely with TimePoints. Say you're watching a movie and don't want the 9 PM automation to switch your lights:

```yaml
# Manual trigger (e.g., from a button or voice assistant)
automation:
  - alias: "Skip Tonight's Auto-Switch"
    trigger:
      - trigger: event
        event_type: mobile_app_notification_action
        event_data:
          action: SKIP_TONIGHT
    action:
      - action: friendly_scene_flipper.skip
        data:
          entity_id: select.living_room_lights
          slot: b
          enable: true
```

When the 9 PM TimePoint fires and calls `activate`, the skip flag suppresses `scene.turn_on` for that one activation. The flag resets automatically — tomorrow evening works normally.

## Combining with Flipper: Rotate Through Scenes

Use a TimePoint to cycle through scenes daily:

```yaml
automation:
  - alias: "Bedroom — New Scene Each Evening"
    trigger:
      - trigger: time
        at: "20:00:00"
    action:
      - action: friendly_scene_flipper.flip_next
        data:
          entity_id: select.bedroom
```

This advances through the flip list configured in the options flow, wrapping around when it reaches the end.

## Tips

- **One automation per TimePoint** keeps things simple and easy to debug.
- **Name your automations clearly** — "Room — What happens at when" is a good pattern.
- Use `set_scene` + `activate` when the TimePoint should change _which_ scene is in a slot. Use just `activate` when the slot already has the right scene.
- The HA automation editor has a great visual mode for time triggers — you don't need to write YAML by hand.
- TimePoints respect Skipper flags, so users always have a manual override.
