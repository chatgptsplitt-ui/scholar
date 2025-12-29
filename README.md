# Alien Orchard Lab

Cozy sci-fi farming prototype built in **Godot 4**. Grow aliens in incubators, harvest them for credits, and expand your lab.

## How to run
1. Install Godot 4.x.
2. Open the project folder (`/workspace/scholar`) in Godot.
3. Run the project (default scene is `scenes/MainMenu.tscn`).

### Play in Chrome via HTML5 export (double-click)
1. In Godot’s Project Manager, open this folder and go to **Project → Export**.
2. Select the **HTML5** preset (provided in `export_presets.cfg`), choose an export path like `build/web/AlienOrchardLab.html`, and click **Export Project**.
3. Open the exported `AlienOrchardLab.html` in Chrome by double-clicking it. If your browser blocks local file access, run `python -m http.server 8000` inside `build/web` and open `http://localhost:8000/AlienOrchardLab.html`.

## Controls
- **WASD / Arrow Keys**: Move
- **E**: Interact (incubators, shop terminal, doors)
- **1–5**: Select seed slot
- **ESC**: Quick save

## Gameplay loop
1. Walk to an incubator and press **E** to plant the selected seed (requires inventory).
2. Check incubators while growing to see stage and remaining time.
3. Harvest when ready to automatically sell for credits (with mutation bonus chance).
4. Buy more seeds at the shop terminal.
5. Purchase doors to unlock new rooms and more incubators.

## Editing data
- **Seed catalog**: `data/seeds.json` (grow time, buy cost, sell value, traits).
- **Room prices**: `scripts/Game.gd` (`room_prices` dictionary).
- **Incubator layouts**: `scenes/Room_01.tscn`, `scenes/Room_02.tscn`, `scenes/Room_03.tscn`.

## Save/Load
- Save file stored at `user://alien_orchard_save.json` (auto-save with **ESC**, loaded on start/continue).

## Assets
No binary art assets are needed; visuals use simple ColorRect nodes and scene colors so everything stays text-based.
