# 🚀 Space Haven Save Editor - Python Edition

**A cross-platform save editor for Space Haven, optimized for Steam Deck!**

Take full control of your Space Haven adventure from anywhere - including your Steam Deck!

Original VB.NET version by [Moragar](https://github.com/moragar360)  
Python port for cross-platform compatibility

---

## ✨ Features

All the features of the original editor, now running on Linux/Steam Deck:

- 💰 **Global Save Settings**
  - Edit in-game credits
  - Adjust Exodus Fleet prestige points
  - Enable or disable Sandbox Mode

- 🚀 **Ship Management**
  - View and select ships from your save file
  - Edit ship dimensions (Width x Height grid squares)
  - Safely expand or resize ships

- 👨‍🚀 **Detailed Crew Editing**
  - View crew member details
  - Modify attributes and skills
  - Manage traits and conditions

- 📦 **Storage Management**
  - View and manage storage containers
  - Edit item quantities

- 💾 **Automatic Backups**
  - Automatically create timestamped backup folders when opening saves
  - Manual backup still strongly recommended

- 🎮 **Steam Deck Optimized**
  - Touch-friendly interface
  - Runs natively on SteamOS
  - No Windows compatibility layer needed!

---

## 📦 Installation

### On Steam Deck (Desktop Mode) - Recommended!

1. **Switch to Desktop Mode**
   - Hold the power button and select "Switch to Desktop"

2. **Open Konsole (Terminal)**
   - Find it in the application menu

3. **Download the editor**:
   ```bash
   cd ~/Downloads
   git clone https://github.com/JohnCrafton/Space-Haven-Save-Game-Editor.git
   cd Space-Haven-Save-Game-Editor/python
   ```
   
   OR download the ZIP from GitHub and extract it

4. **Make the launcher executable**:
   ```bash
   chmod +x run_editor.sh
   ```

5. **Run the editor**:
   ```bash
   ./run_editor.sh
   ```

**That's it!** The script will automatically:
- Install `uv` (fast Python package manager) if needed
- Install PyQt6 automatically using `uv`
- Launch the editor

**No manual Python/pip setup required!** The `uv` tool handles everything in an isolated environment.

### Why uv?

We use `uv` instead of pip because it's:
- ⚡ **10-100x faster** than pip
- 🎯 **No conflicts** with Steam Deck's system Python
- 🔒 **Isolated** - doesn't mess with system packages
- 💪 **Reliable** on SteamOS's read-only filesystem

6. **Make the launcher executable**:
   ```bash
   chmod +x run_editor.sh
   ```

7. **Run the editor**:
   ```bash
   ./run_editor.sh
   ```

### On Linux (Desktop)

**Option 1: Using uv (Recommended - Fast & Easy)**

```bash
# Download the editor
git clone https://github.com/JohnCrafton/Space-Haven-Save-Game-Editor.git
cd Space-Haven-Save-Game-Editor/python

# Make launcher executable and run
chmod +x run_editor.sh
./run_editor.sh
```

The script auto-installs `uv` and dependencies. No manual setup needed!

**Option 2: Traditional Python/pip method**

1. **Install Python 3.8 or higher**:
   ```bash
   # Debian/Ubuntu
   sudo apt install python3 python3-pip
   
   # Fedora
   sudo dnf install python3 python3-pip
   
   # Arch
   sudo pacman -S python python-pip
   ```

2. **Clone or download this repository**:
   ```bash
   git clone https://github.com/JohnCrafton/Space-Haven-Save-Game-Editor.git
   cd Space-Haven-Save-Game-Editor/python
   ```

3. **Install dependencies**:
   ```bash
   pip install --user -r requirements.txt
   # OR
   pip install --user PyQt6
   ```

4. **Run the editor**:
   ```bash
   python3 space_haven_editor.py
   ```

### Alternative: Install as a system command

```bash
cd ~/Downloads/Space-Haven-Save-Game-Editor/python
pip install --user .
```

Then you can run it from anywhere:
```bash
space-haven-editor
```

---

## 🎮 Usage

### Finding Your Save Files

**On Steam Deck / Linux:**
```
~/.steam/steam/steamapps/common/SpaceHaven/savegames/[YourSaveGameName]/save/
```

Or possibly:
```
~/.local/share/Steam/steamapps/common/SpaceHaven/savegames/[YourSaveGameName]/save/
```

The save file is named **`game`** (no extension).

### Using the Editor

1. **Launch the editor**:
   ```bash
   cd ~/Downloads/Space-Haven-Save-Game-Editor/python
   ./run_editor.sh
   ```

2. **Open a save file**:
   - Click **File → Open Save File**
   - Navigate to your Space Haven save directory
   - Select the `game` file

3. **Make your edits**:
   - **Global Settings**: Edit credits, prestige points, sandbox mode
     - Enter new values
     - Click "Update Global Settings"
   - **Ships**: Select a ship, modify dimensions
   - **Crew**: View and edit crew member stats
   - **Storage**: Manage storage containers and items

4. **Save your changes**:
   - Click **File → Save** (or press Ctrl+S)
   - Launch Space Haven and load your save!

### Tips for Steam Deck

- **Touch Controls**: The interface is designed to work with touch
- **Virtual Keyboard**: Use Steam's keyboard for text input (Steam+X)
- **Backups**: The editor creates automatic backups by default
- **Game Mode**: You can add the editor to Steam as a non-Steam game to launch it from Game Mode

---

## 🔧 Adding to Steam (Optional)

To launch the editor from Game Mode:

1. **In Desktop Mode**, open Steam
2. Click **Games → Add a Non-Steam Game to My Library**
3. Click **Browse** and navigate to:
   ```
   ~/Downloads/Space-Haven-Save-Game-Editor/python/run_editor.sh
   ```
4. Select the script and add it
5. Right-click the new game in your library → **Properties**
6. Change the name to "Space Haven Save Editor"
7. Set start in directory to:
   ```
   ~/Downloads/Space-Haven-Save-Game-Editor/python
   ```

Now you can launch it from Game Mode!

---

## ⚠️ Important Notes

### Backups
- **ALWAYS make manual backups** of your save files before editing
- The editor creates automatic backups, but manual backups are safer
- To restore: Copy backup folder contents back to original location

### Save File Location
The save file structure is:
```
savegames/
  └── YourSaveName/
      └── save/
          └── game  ← This is the file you edit
```

### Making Changes Permanent
1. Edit values in the interface
2. For global settings, click "Update Global Settings"
3. Click File → Save to write changes to disk
4. Changes take effect when you load the save in Space Haven

### Compatibility
- Tested with Space Haven Alpha 20
- Works on Steam Deck (SteamOS)
- Works on Linux desktop distributions
- Python 3.8+ required

---

## 🐛 Troubleshooting

### Using uv (Recommended Method)

If you're using the `run_editor.sh` script with `uv`, most issues are automatically handled!

**Script won't run:**
```bash
chmod +x run_editor.sh
```

**uv installation fails:**
```bash
# Manually install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Try running again
./run_editor.sh
```

**Editor won't start:**
```bash
# Check if uv is in PATH
which uv

# If not found, add it:
export PATH="$HOME/.cargo/bin:$PATH"
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
```

### Traditional pip Method

**"No module named 'PyQt6'":**
```bash
pip install --user PyQt6
# OR with uv:
uv pip install PyQt6
```

**"Permission denied" when running run_editor.sh:**
```bash
chmod +x run_editor.sh
```

**Can't find save files:**
Check both possible Steam directories:
```bash
ls ~/.steam/steam/steamapps/common/SpaceHaven/savegames/
ls ~/.local/share/Steam/steamapps/common/SpaceHaven/savegames/
```

**Editor won't start in Desktop Mode:**
```bash
# With uv (recommended):
./run_editor.sh

# Or check Python version:
python3 --version
# Should show Python 3.8 or higher
```

**Changes don't appear in game:**
- Make sure you clicked "Update Global Settings" before saving
- Verify the save file was actually modified (check timestamp)
- Make sure Space Haven isn't running when you save

**Steam Deck read-only filesystem issues:**
This is why we use `uv`! It handles everything in user space without needing `sudo` or modifying system files.

---

## 🆚 Differences from Windows Version

This Python version:
- ✅ Runs natively on Linux/Steam Deck
- ✅ No Wine or compatibility layer needed
- ✅ Open source and easily modifiable
- ✅ Cross-platform (Linux, macOS, Windows)
- ⚠️ Some advanced features still in development
- ⚠️ Interface slightly different but familiar

---

## 📝 Development

### Project Structure
```
python/
  ├── space_haven_editor.py  # Main application
  ├── models.py              # Data models
  ├── requirements.txt       # Python dependencies
  ├── setup.py              # Installation script
  ├── run_editor.sh         # Launch script
  └── README_PYTHON.md      # This file
```

### Contributing
Feel free to submit issues and pull requests!

### Testing
```bash
# Install in development mode
pip install --user -e .

# Run the editor
python3 space_haven_editor.py
```

---

## 📜 License

This project is licensed under the [MIT License](../LICENSE).

---

## 🙏 Credits

- **Original Editor**: [Moragar](https://github.com/moragar360)
- **Python Port**: Community contributors
- **Space Haven**: Bugbyte Ltd.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JohnCrafton/Space-Haven-Save-Game-Editor/issues)
- **Original Windows Version**: [Moragar's Repository](https://github.com/moragar360/Space-Haven-Save-Game-Editor)

---

## 🎮 Enjoy editing your Space Haven saves on your Steam Deck! 🚀
