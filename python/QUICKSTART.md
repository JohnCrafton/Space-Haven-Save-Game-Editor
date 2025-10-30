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
~/.steam/steam/steamapps/common/SpaceHaven/savegames/[YourSaveGameName]
```

Alternative location:
```
~/.local/share/Steam/steamapps/common/SpaceHaven/savegames/[YourSaveGameName]
```

## 🔧 Usage

1. **File → Open Save File**
2. Navigate to your save location
3. Select the save folder you want to update
4. Edit your settings
5. Click "Update Global Settings" for global changes
6. **File → Save** to write changes

## 💡 Tips

- It helps to have the game running in the background to avoid Steam overwriting your save from cloud data
- Automatic backups are created by default
- Never hurts to make manual backups too!
- Use Steam+X for virtual keyboard

## May Not Work Right Now

- Assigning skills (TODO:  "Max Learning/Max Value" button)
- Some items in the storage lists don't appear correctly (yet)
- Some storage elements (such as corpse lockers) register as "small/large storage"

## 🆘 Help

See the full `README_PYTHON.md` for detailed instructions and troubleshooting.
