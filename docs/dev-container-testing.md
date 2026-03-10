# Dev Container Testing Guide

No code changes needed — this is a reference for manual testing.

## 1. Start HA

```bash
docker compose up -d
```

Open http://localhost:8123. First run requires onboarding (create a user account).

## 2. Testing Dashboard

A dedicated **FSF Testing** dashboard appears in the sidebar automatically (registered via `configuration.yaml`).

It provides:
- **Entity State** — live dropdown for `select.testflip` plus all attributes (active_slot, scenes, skip flags, flip lists/indices)
- **Core Actions** — Toggle, Activate A, and Activate B buttons
- **Skipper** — Skip A/B/Both and Clear Skip buttons
- **Flipper** — Flip Prev and Flip Next buttons
- **Set Scene** — 12 buttons to assign any test scene to either slot
- **Available Scenes** — quick-reference list of all six test scenes

Use this dashboard for rapid click-through testing instead of Developer Tools.

The dashboard YAML lives at `config/dashboards/testing.yaml` and is version-controlled.

## 3. Verify Test Scenes Exist

**Developer Tools → States** → filter for `scene.`

You should see: `scene.day_mode`, `scene.night_mode`, `scene.movie_time`, `scene.bright_lights`, `scene.dim_lights`, `scene.cozy_evening`

## 4. Add the Integration

**Settings → Devices & Services → Add Integration → search "Friendly Scene Flipper"**

Config flow fields:
- **Name**: e.g. "Living Room Lights"
- **Scene A**: pick "Day Mode"
- **Scene B**: pick "Night Mode"

This creates a `select.living_room_lights` entity.

## 5. Test the Dropdown

**Settings → Devices & Services → Friendly Scene Flipper → entity row** (or add it to a dashboard)

- The dropdown shows two options: "Day Mode" and "Night Mode"
- Selecting one should switch the active scene (check logs for `scene.turn_on` calls)

## 6. Test Services

**Developer Tools → Services**:

| Service | Fields | What to verify |
|---|---|---|
| `friendly_scene_flipper.toggle` | entity_id: `select.living_room_lights` | Dropdown flips between A and B |
| `friendly_scene_flipper.activate` | entity_id + slot: `a` or `b` | Explicitly activates that slot |
| `friendly_scene_flipper.set_scene` | entity_id + slot + scene_entity_id: `scene.movie_time` | Replaces a slot's scene, dropdown options update |
| `friendly_scene_flipper.skip` | entity_id + slot: `a`/`b`/`both` + enable: true/false | Sets or clears skip flag, verify in attributes |
| `friendly_scene_flipper.flip_next` | entity_id | Advances to next scene in flip list, verify scene + index change |
| `friendly_scene_flipper.flip_prev` | entity_id | Goes to previous scene in flip list |

## 7. Test Options Flow (Reconfigure)

**Settings → Devices & Services → Friendly Scene Flipper → Configure**

- Change Scene A or Scene B to different test scenes
- Configure flip lists: add several scenes to Flip List A and/or B
- Verify the dropdown options update accordingly
- Verify flip_next/flip_prev cycle through the configured flip lists

## 8. Test Skipper

1. Call `friendly_scene_flipper.skip` with slot `a` and enable `true`
2. Verify `skip_a` attribute is `true` in the entity state card
3. Call `friendly_scene_flipper.set_scene` on slot A — scene should be assigned but `scene.turn_on` is NOT called (check logs)
4. Verify `skip_a` resets to `false` (one-shot)
5. Call `friendly_scene_flipper.toggle` — toggle always fires, skip has no effect

## 9. Test Flipper

1. Configure flip lists via the options flow (add 3+ scenes to Flip List A)
2. Call `friendly_scene_flipper.flip_next` — verify scene_a changes to the next scene in the list
3. Keep calling — verify it wraps around at the end
4. Call `friendly_scene_flipper.flip_prev` — verify it goes backward
5. Combine with Skipper: arm skip, then flip — scene changes in state but `scene.turn_on` is suppressed

## 10. Test Restart Persistence

```bash
docker compose restart
```

After restart, verify:
- The entity still exists with its previous state
- The active slot is restored **without** triggering `scene.turn_on` (check logs — no activation on startup)
- Skip flags and flip indices are restored

## 11. View Logs

```bash
docker compose logs -f home-assistant | grep friendly_scene_flipper
```

Debug logging is enabled by default in `config/configuration.yaml`.

## 12. Code Change Workflow

Edit files in `custom_components/friendly_scene_flipper/`, then:
```bash
docker compose restart
```
The bind mount means your changes are picked up on restart — no rebuild needed.

## 13. Stop

```bash
docker compose down
```
