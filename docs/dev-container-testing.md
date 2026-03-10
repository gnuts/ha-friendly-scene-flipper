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
- **Entity State** — live dropdown for `select.testflip` plus its `active_slot`, `scene_a`, and `scene_b` attributes
- **Core Actions** — Toggle, Activate A, and Activate B buttons
- **Set Scene** — 8 buttons to assign any test scene to either slot
- **Available Scenes** — quick-reference list of all four test scenes

Use this dashboard for rapid click-through testing instead of Developer Tools.

The dashboard YAML lives at `config/dashboards/testing.yaml` and is version-controlled.

## 3. Verify Test Scenes Exist

**Developer Tools → States** → filter for `scene.`

You should see: `scene.day_mode`, `scene.night_mode`, `scene.movie_time`, `scene.bright_lights`

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
| `friendly_scene_flipper.toggle` | entity_id: `select.living_room_lights` | Dropdown flips between A ↔ B |
| `friendly_scene_flipper.activate` | entity_id + slot: `a` or `b` | Explicitly activates that slot |
| `friendly_scene_flipper.set_scene` | entity_id + slot + scene_entity_id: `scene.movie_time` | Replaces a slot's scene, dropdown options update |

## 7. Test Options Flow (Reconfigure)

**Settings → Devices & Services → Friendly Scene Flipper → Configure**

- Change Scene A or Scene B to different test scenes
- Verify the dropdown options update accordingly

## 8. Test Restart Persistence

```bash
docker compose restart
```

After restart, verify:
- The entity still exists with its previous state
- The active slot is restored **without** triggering `scene.turn_on` (check logs — no activation on startup)

## 9. View Logs

```bash
docker compose logs -f home-assistant | grep friendly_scene_flipper
```

Debug logging is enabled by default in `config/configuration.yaml`.

## 10. Code Change Workflow

Edit files in `custom_components/friendly_scene_flipper/`, then:
```bash
docker compose restart
```
The bind mount means your changes are picked up on restart — no rebuild needed.

## 11. Stop

```bash
docker compose down
```
