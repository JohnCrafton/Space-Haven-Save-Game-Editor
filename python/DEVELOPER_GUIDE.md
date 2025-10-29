# Developer Guide - Save File Scanner

## Architecture

The save file scanner consists of three main components:

### 1. ReferenceData (`reference_data.py`)
Contains all known game IDs ported from the VB.NET `IdCollection.vb`:
- Character attributes (Bravery, Zest, Intelligence, Perception)
- Skills (Piloting, Mining, Botany, etc.)
- Traits (Hero, Smart, Fast Learner, etc.)
- Storage items (resources, weapons, equipment)
- Conditions (injuries, moods, status effects)
- Research/Technology IDs
- Craft types

**Key Methods:**
- `is_known_id(id_value, category=None)` - Check if an ID is known
- `get_id_name(id_value, category=None)` - Get the name for an ID
- `get_all_known_ids()` - Return all ID collections

### 2. SaveFileScanner (`save_scanner.py`)
Scans XML save files and detects unknown IDs.

**Key Classes:**
- `UnknownItem` - Represents a single unknown ID with metadata
- `ScanResult` - Contains results from a scan
- `SaveFileScanner` - Main scanner class

**Scanning Process:**
1. Parse XML save file
2. Scan character data (attributes, skills, traits, conditions)
3. Scan storage items
4. Scan research/technology
5. Scan crafts
6. Generic ID scan as catch-all
7. Generate results with detailed information

**Key Methods:**
- `scan_file(file_path)` - Scan a save file
- `generate_bug_report(result)` - Generate markdown bug report
- `save_report_to_file(result, output_path)` - Save report to file

### 3. UI Integration (`space_haven_editor.py`)
Integrated into the main editor application.

**Menu Actions:**
- Tools → Scan for Unknown IDs (Ctrl+Shift+S)
- Tools → View Last Scan Results
- Tools → Export Bug Report

**Key Methods:**
- `scan_save_file()` - Initiate scan
- `show_scan_results(result)` - Display results in dialog
- `view_last_scan_results()` - View cached results
- `export_bug_report()` - Export and optionally open report

## Adding New Reference Data

When Space Haven updates add new items:

1. Update `reference_data.py` with new IDs:
```python
SKILLS: Dict[int, str] = {
    1: "Piloting",
    # ... existing entries ...
    99: "New Skill Name",  # Add new entry
}
```

2. If a new category is needed:
```python
NEW_CATEGORY: Dict[int, str] = {
    1: "Item 1",
    2: "Item 2",
}

@classmethod
def get_all_known_ids(cls) -> Dict[str, Dict[int, str]]:
    return {
        # ... existing categories ...
        "new_category": cls.NEW_CATEGORY,
    }
```

3. Update scanner if the new category requires special XML parsing:
```python
def _scan_new_category(self, root: ET.Element, result: ScanResult):
    """Scan new category elements"""
    for elem in root.findall(".//new_element"):
        if 'id' in elem.attrib:
            item_id = int(elem.get("id", "0"))
            # ... check and record ...
```

## Testing

### Unit Tests (`test_scanner.py`)
Tests individual components:
- Reference data loading and lookup
- ScanResult functionality
- Scanner initialization
- Bug report generation

Run: `python3 test_scanner.py`

### Integration Tests (`test_integration.py`)
Tests with sample save file:
- Full scan workflow
- Detection of all unknown ID types
- Bug report generation

Run: `python3 test_integration.py`

### Adding Tests
```python
def test_new_feature():
    """Test description"""
    # Arrange
    scanner = SaveFileScanner()
    
    # Act
    result = scanner.new_method()
    
    # Assert
    assert result == expected, "Error message"
```

## Performance Considerations

- XML parsing is the main bottleneck
- Typical save files scan in under 1 second
- Results are cached to avoid re-scanning
- Memory usage is minimal (< 10 MB for large saves)

## Future Enhancements

### Auto-Update Reference Data
Download latest reference data from a remote source:
```python
def update_reference_data(self):
    """Download latest reference data"""
    response = requests.get(REFERENCE_DATA_URL)
    data = response.json()
    # Update local reference data
```

### GitHub Issue Integration
Automatically create GitHub issues:
```python
def submit_to_github(self, result: ScanResult):
    """Submit bug report as GitHub issue"""
    # Use GitHub API to create issue
    # Requires authentication token
```

### Pattern Detection
Guess what unknown IDs might be:
```python
def guess_id_type(self, unknown_item: UnknownItem) -> str:
    """Attempt to guess what an unknown ID represents"""
    # Analyze XML context, attributes, nearby IDs
    # Return educated guess
```

### Batch Processing
Scan multiple save files at once:
```python
def scan_directory(self, directory: str) -> List[ScanResult]:
    """Scan all save files in a directory"""
    results = []
    for save_file in Path(directory).glob("**/game"):
        results.append(self.scan_file(str(save_file)))
    return results
```

## Troubleshooting Development

### Import Errors
Ensure all dependencies are installed:
```bash
pip install PyQt6
```

### XML Parsing Issues
Space Haven save files should be valid XML. If parsing fails:
1. Check file encoding (should be UTF-8)
2. Validate XML structure
3. Check for special characters

### Unknown IDs Not Detected
1. Verify reference data is up to date
2. Check scanner is looking in correct XML paths
3. Add debug logging to scanner methods

### UI Not Responding
1. Scanning runs in main thread - consider threading for large files
2. Progress dialog updates with `QApplication.processEvents()`

## Code Style

Follow existing patterns:
- PEP 8 style guide
- Type hints for function parameters and returns
- Docstrings for all public methods
- Logging for important operations
- Error handling with try/except

## Contributing

1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request

See main README for contribution guidelines.
