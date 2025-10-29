#!/usr/bin/env python3
"""
Example script showing how to use the Save File Scanner programmatically

This script demonstrates:
1. Scanning a save file
2. Checking for unknown IDs
3. Generating and saving a bug report
"""

import sys
from pathlib import Path

# Add the python directory to the path if running from elsewhere
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from save_scanner import SaveFileScanner


def main():
    """Main function demonstrating scanner usage"""
    
    # Check for command line argument
    if len(sys.argv) < 2:
        print("Usage: python example_scanner_usage.py <path_to_save_file>")
        print()
        print("Example:")
        print("  python example_scanner_usage.py ~/.steam/steam/steamapps/common/SpaceHaven/savegames/MySave/save/game")
        print()
        print("To test with the sample file:")
        print("  python example_scanner_usage.py test_save.xml")
        sys.exit(1)
    
    save_file_path = sys.argv[1]
    
    # Verify file exists
    if not Path(save_file_path).exists():
        print(f"Error: File not found: {save_file_path}")
        sys.exit(1)
    
    print("="*70)
    print("Space Haven Save File Scanner - Example Usage")
    print("="*70)
    print()
    
    # Create scanner instance
    print("1. Initializing scanner...")
    scanner = SaveFileScanner()
    print("   ✓ Scanner ready")
    print()
    
    # Scan the file
    print(f"2. Scanning file: {Path(save_file_path).name}")
    try:
        result = scanner.scan_file(save_file_path)
        print("   ✓ Scan complete")
    except Exception as e:
        print(f"   ✗ Error scanning file: {e}")
        sys.exit(1)
    print()
    
    # Display results
    print("3. Scan Results:")
    print(f"   Total IDs found: {result.total_ids_found}")
    print(f"   Known IDs: {result.known_ids_count}")
    print(f"   Unknown IDs: {result.unknown_ids_count}")
    print()
    
    # Check if unknown IDs were found
    if result.unknown_ids_count == 0:
        print("   ✓ No unknown IDs detected!")
        print("   ✓ All IDs in this save file are recognized.")
        print()
        print("="*70)
        return
    
    # Display unknown IDs
    print("4. Unknown IDs Detected:")
    print()
    for item in sorted(result.unknown_items, key=lambda x: (x.id_type, x.id_value)):
        print(f"   • {item.id_type.upper()}: ID {item.id_value}")
        print(f"     Location: {item.xml_path}")
        print(f"     Occurrences: {item.occurrences}")
        print()
    
    # Generate bug report
    print("5. Generating bug report...")
    report_filename = f"bug_report_{Path(save_file_path).stem}.md"
    report_path = scanner.save_report_to_file(result, report_filename)
    print(f"   ✓ Bug report saved to: {report_path}")
    print()
    
    # Show next steps
    print("6. Next Steps:")
    print()
    print("   To submit this bug report to the developers:")
    print("   a. Review the bug report file")
    print("   b. Go to: https://github.com/JohnCrafton/Space-Haven-Save-Game-Editor/issues")
    print("   c. Click 'New Issue'")
    print("   d. Copy the contents of the bug report")
    print("   e. Add any additional context (game version, mods, etc.)")
    print("   f. Submit the issue")
    print()
    print("="*70)
    print()
    print("Full scan summary:")
    print("="*70)
    print(result.get_summary())
    print("="*70)


if __name__ == "__main__":
    main()
