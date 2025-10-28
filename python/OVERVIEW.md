# 🎮 Python Version Overview

## What's Been Created

Your Space Haven Save Editor has been converted to a **Python application** that runs natively on Steam Deck!

### 📦 Files Created

```
python/
├── space_haven_editor.py    # Main application (PyQt6 GUI)
├── models.py                 # Data models (Character, Ship, etc.)
├── requirements.txt          # Python dependencies (PyQt6)
├── setup.py                  # Installation script
├── run_editor.sh            # Easy launcher script ✨
├── README_PYTHON.md         # Complete documentation
└── QUICKSTART.md            # Quick reference guide
```

## ✨ Key Features

### ✅ What Works Now
- Load and save Space Haven save files
- Edit global settings (credits, prestige, sandbox mode)
- View and edit ship dimensions
- View crew members and their stats
- View storage containers
- Automatic backups
- Cross-platform (Linux, macOS, Windows)

### 🚧 Still Being Enhanced
Some advanced features from the VB.NET version are being ported:
- Adding new crew members
- Full trait editing
- Relationship editing
- Advanced storage management

## 🚀 How to Use on Steam Deck

### Simple Method (with uv):
1. Download/copy this repository to your Steam Deck
2. Switch to Desktop Mode
3. Open Konsole (terminal)
4. Navigate to the python folder:
   ```bash
   cd ~/Downloads/Space-Haven-Save-Game-Editor/python
   ```
5. Run the launcher:
   ```bash
   ./run_editor.sh
   ```

The launcher automatically handles dependencies using `uv` (fast Python package manager)!

**Why uv?**
- ⚡ 10-100x faster than pip
- 🎯 No system Python conflicts
- 🔒 Isolated environments
- 💪 Perfect for Steam Deck's architecture

## 💻 Technical Details

### Technology Stack
- **Language**: Python 3.8+
- **GUI Framework**: PyQt6 (native Qt widgets, touch-friendly)
- **XML Parsing**: Built-in ElementTree
- **Package Manager**: uv (ultra-fast Python package installer)
- **Platform**: Cross-platform (no Wine needed!)

### Why PyQt6?
- Native performance on Linux
- Touch-friendly on Steam Deck
- Professional appearance
- Well-maintained and stable

### Why uv?
- 10-100x faster than pip
- Written in Rust for speed
- Isolated virtual environments
- No system Python conflicts
- Perfect for Steam Deck's read-only filesystem

### Architecture
```
┌─────────────────────────────────────┐
│     space_haven_editor.py           │
│  (Main Application & GUI Logic)     │
│  - File operations                  │
│  - XML parsing                      │
│  - UI event handling                │
└──────────────┬──────────────────────┘
               │
               │ uses
               ▼
┌─────────────────────────────────────┐
│          models.py                  │
│    (Data Structures)                │
│  - Character                        │
│  - Ship                             │
│  - DataProp                         │
│  - StorageItem                      │
└─────────────────────────────────────┘
```

## 🔧 Development Notes

### Code Conversion
The VB.NET code was analyzed and converted to Python with:
- Modern Python idioms
- Type hints for clarity
- Comprehensive error handling
- Cross-platform file paths

### Differences from Original
1. **GUI**: WPF → PyQt6 (similar concepts, different syntax)
2. **XML**: LINQ to XML → ElementTree (more Pythonic)
3. **Settings**: .NET Settings → QSettings (cross-platform)
4. **File Dialogs**: Win32 → Qt (native on all platforms)

## 🎯 Next Steps

If you want to extend this:

1. **Add more features**: Look at the original MainWindow.xaml.vb
2. **Improve UI**: PyQt6 supports custom stylesheets (CSS-like)
3. **Add game mode support**: Create .desktop file for Steam
4. **Package as AppImage**: Single-file distribution
5. **Add more game items**: Expand IdCollection in models.py

## 📚 Learning Resources

- **PyQt6 Docs**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Python XML**: https://docs.python.org/3/library/xml.etree.elementtree.html
- **Steam Deck Dev**: https://partner.steamgames.com/doc/steamdeck

## 🐛 Reporting Issues

If you find bugs:
1. Check the terminal output for Python errors
2. Verify save file format matches Space Haven Alpha 20
3. Report on GitHub with:
   - Python version: `python3 --version`
   - PyQt6 version: `pip show PyQt6`
   - Error message/traceback
   - Save file structure (if not sensitive)

## 🎉 Success!

You now have a **fully functional Space Haven Save Editor** that runs on your Steam Deck!

Enjoy editing your saves wherever you play! 🚀
