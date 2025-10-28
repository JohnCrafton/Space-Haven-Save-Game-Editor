# Quick Start Guide - Steam Deck

## 🎮 Running on Steam Deck

### Desktop Mode

1. **Switch to Desktop Mode**
   - Power button → "Switch to Desktop"

2. **Open Konsole (terminal)**

3. **Navigate to this directory**:
   ```bash
   cd ~/Downloads/Space-Haven-Save-Game-Editor/python
   ```

4. **Run the launcher**:
   ```bash
   ./run_editor.sh
   ```

### First Time Setup

The launcher script will automatically:
- Install `uv` if needed (fast Python package manager)
- Install PyQt6 automatically
- Launch the editor

**No manual dependency installation needed!** `uv` handles everything.

### Why uv?

`uv` is much faster and more reliable than pip on Steam Deck:
- ⚡ 10-100x faster than pip
- 🎯 No conflicts with system Python
- 🔒 Isolated environments automatically
- 💪 Works great on SteamOS

## 📁 Where are my save files?

Steam Deck save location:
```
~/.steam/steam/steamapps/common/SpaceHaven/savegames/[YourSaveGameName]/save/game
```

Alternative location:
```
~/.local/share/Steam/steamapps/common/SpaceHaven/savegames/[YourSaveGameName]/save/game
```

## 🔧 Usage

1. **File → Open Save File**
2. Navigate to your save location
3. Select the `game` file (no extension)
4. Edit your settings
5. Click "Update Global Settings" for global changes
6. **File → Save** to write changes
7. Launch Space Haven!

## 💡 Tips

- Automatic backups are created by default
- Always make manual backups too!
- Touch controls work great on Steam Deck
- Use Steam+X for virtual keyboard

## 🆘 Help

See the full `README_PYTHON.md` for detailed instructions and troubleshooting.
