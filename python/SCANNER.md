# Save File Scanner Feature

## Overview

The Save File Scanner is a diagnostic tool that scans Space Haven save files to detect unknown item IDs that are not present in the reference data. This is particularly useful during Space Haven's Early Access period when new items, skills, traits, or other game elements are added in updates.

## Why This Feature Exists

Space Haven is in Early Access and regularly receives updates that add new content. When new items, skills, traits, or other game elements are added, they may not be present in the editor's reference data. This scanner helps:

1. **Detect New Content**: Automatically identify when a save file contains IDs not in our reference data
2. **Version Compatibility**: Help users understand if their save file has content from a newer game version
3. **Developer Feedback**: Generate bug reports that can be submitted to help developers update the reference data

## How to Use

### Scanning a Save File

1. **Open a save file** in the editor (File → Open Save File)
2. **Start the scan** using one of these methods:
   - Menu: Tools → Scan for Unknown IDs
   - Keyboard: Press `Ctrl+Shift+S`
3. **Review the results** in the scan results dialog

### Understanding Scan Results

The scan results show:
- **Total IDs Found**: Total number of IDs detected in the save file
- **Known IDs**: IDs that match the reference data
- **Unknown IDs**: IDs not found in the reference data (potential new items)

For each unknown ID, you'll see:
- **ID Value**: The numeric ID
- **Type**: Category (attribute, skill, trait, storage_item, condition, research, craft, or generic)
- **XML Location**: Where in the save file the ID was found
- **Occurrences**: How many times it appears
- **Attributes**: XML attributes associated with the ID

### Exporting a Bug Report

If unknown IDs are detected:

1. Click **"Export Report"** in the scan results dialog, or
2. Use **Tools → Export Bug Report**
3. Choose where to save the Markdown file
4. Optionally open the report to review it

### Submitting to GitHub

To help improve the editor:

1. Export the bug report
2. Go to https://github.com/JohnCrafton/Space-Haven-Save-Game-Editor/issues
3. Click "New Issue"
4. Copy and paste the contents of the bug report
5. Add any additional context (game version, when you created the save, etc.)
6. Submit the issue

## What Gets Scanned

The scanner checks these categories of IDs:

### Character Data
- **Attributes**: Bravery, Zest, Intelligence, Perception
- **Skills**: Mining, Botany, Piloting, Medical, etc.
- **Traits**: Hero, Smart, Fast Learner, etc.
- **Conditions**: Status effects like injuries, moods, etc.

### Items and Storage
- **Storage Items**: Resources, weapons, equipment, food, etc.

### Technology
- **Research**: Technology/facility IDs
- **Crafts**: Ship craft types (shuttles, miners, fighters)

### Generic IDs
- Any other numeric IDs found in common ID attributes (`id`, `type`, `objId`, `itemId`, `typeId`)

## Technical Details

### Reference Data Source

The reference data is ported from the original VB.NET editor's `IdCollection.vb` file and includes:
- 4 Attributes
- 14 Skills
- 24 Traits
- 87 Storage Items
- 169 Conditions
- 45 Research/Technology IDs
- 3 Craft Types

### Scanner Implementation

The scanner:
1. Parses the XML save file
2. Traverses all elements looking for ID attributes
3. Compares found IDs against the reference data
4. Collects unknown IDs with context information
5. Generates a detailed report

### Performance

- Scanning is fast (typically completes in under 1 second)
- Results are cached - you can view results multiple times without re-scanning
- Safe - scanning is read-only and never modifies the save file

## Troubleshooting

### "No File Loaded" Error
You need to open a save file before scanning. Use File → Open Save File first.

### No Unknown IDs Found
This is good! It means all IDs in your save file are known. This typically happens when:
- Your game version matches the editor's reference data version
- You haven't installed mods that add new items
- The save doesn't contain recently added content

### Many Unknown IDs
This can happen when:
- You're using a newer game version than the reference data supports
- You have mods installed that add custom items
- The game received a major content update

If you see many unknown IDs, consider:
1. Checking if there's an editor update available
2. Submitting a bug report to help update the reference data
3. Using the editor carefully - unknown items may not be fully supported

## Future Enhancements

Potential improvements for this feature:
- Automatic GitHub issue submission (with user approval)
- Checking for editor updates
- Downloading latest reference data from a remote source
- Community-contributed reference data
- Pattern detection to guess what unknown IDs might be

## Contributing

Help improve the reference data:
1. When you find unknown IDs, submit a bug report
2. If you know what an unknown ID represents, include that in the issue
3. Check the Space Haven game files or wiki for ID information
4. Submit pull requests with updated reference data

## Related Files

- `reference_data.py` - Contains all known ID mappings
- `save_scanner.py` - Scanner implementation
- `IdCollection.vb` - Original VB.NET reference data (in parent directory)

## License

This feature is part of the Space Haven Save Editor and is licensed under the MIT License.
