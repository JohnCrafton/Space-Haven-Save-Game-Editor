"""
Space Haven Save File Version Analyzer

This module analyzes Space Haven save files to:
1. Extract version information
2. Compare structures across different game versions
3. Identify ID mappings and missing elements
4. Generate version compatibility documentation
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging


@dataclass
class SaveFileInfo:
    """Information about a save file"""
    file_path: Path
    version: Optional[str] = None
    game_mode: Optional[str] = None
    id_counter: Optional[int] = None
    sector_count: Optional[int] = None
    root_attributes: Dict[str, str] = field(default_factory=dict)
    gamedata_attributes: Dict[str, str] = field(default_factory=dict)
    xml_structure: Dict[str, Any] = field(default_factory=dict)
    entity_types: Set[str] = field(default_factory=set)
    facility_types: Set[str] = field(default_factory=set)
    item_ids: Dict[str, str] = field(default_factory=dict)  # id -> name mapping


@dataclass
class VersionComparison:
    """Comparison between two save file versions"""
    baseline_file: str
    comparison_file: str
    baseline_version: Optional[str]
    comparison_version: Optional[str]
    missing_elements: List[str] = field(default_factory=list)
    new_elements: List[str] = field(default_factory=list)
    id_changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (name, old_id, new_id)
    structural_differences: List[str] = field(default_factory=list)
    compatibility_notes: List[str] = field(default_factory=list)


class SaveFileVersionAnalyzer:
    """Analyzes and compares Space Haven save files across versions"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.analyzed_saves: Dict[str, SaveFileInfo] = {}

    def analyze_save_file(self, file_path: Path) -> SaveFileInfo:
        """
        Analyze a single save file and extract version/structure information

        Args:
            file_path: Path to the save file

        Returns:
            SaveFileInfo with extracted information
        """
        self.logger.info(f"Analyzing save file: {file_path}")

        info = SaveFileInfo(file_path=file_path)

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract root-level information
            info.root_attributes = dict(root.attrib)
            info.game_mode = root.attrib.get('mode')

            # Try to extract idCounter (useful for understanding save age)
            id_counter_str = root.attrib.get('idCounter')
            if id_counter_str:
                info.id_counter = int(id_counter_str)

            # Look for version information in various places
            info.version = self._extract_version(root)

            # Extract gamedata attributes
            gamedata = root.find('gamedata')
            if gamedata is not None:
                info.gamedata_attributes = dict(gamedata.attrib)
                sector_count_str = gamedata.attrib.get('sectorCount')
                if sector_count_str:
                    info.sector_count = int(sector_count_str)

            # Analyze XML structure
            info.xml_structure = self._analyze_structure(root)

            # Extract entity types from sectors
            info.entity_types = self._extract_entity_types(root)

            # Extract facility types and IDs
            info.facility_types, info.item_ids = self._extract_facilities_and_items(root)

            self.logger.info(f"Analysis complete. Version: {info.version}, Mode: {info.game_mode}")
            self.logger.info(f"  Entity types found: {len(info.entity_types)}")
            self.logger.info(f"  Facility types found: {len(info.facility_types)}")
            self.logger.info(f"  Item IDs found: {len(info.item_ids)}")

        except Exception as e:
            self.logger.error(f"Error analyzing save file: {e}", exc_info=True)
            raise

        # Cache the analysis
        self.analyzed_saves[str(file_path)] = info

        return info

    def _extract_version(self, root: ET.Element) -> Optional[str]:
        """
        Try to extract version information from the save file

        The version might be in:
        - Root attributes (version, gameVersion, etc.)
        - Gamedata section
        - Metadata section
        """
        # Check root attributes
        for attr in ['version', 'gameVersion', 'saveVersion', 'alpha']:
            if attr in root.attrib:
                return root.attrib[attr]

        # Check for gamedata/metadata
        gamedata = root.find('gamedata')
        if gamedata is not None:
            for attr in ['version', 'gameVersion']:
                if attr in gamedata.attrib:
                    return gamedata.attrib[attr]

        # If no explicit version, try to infer from structure
        # (e.g., presence/absence of certain elements)
        return self._infer_version_from_structure(root)

    def _infer_version_from_structure(self, root: ET.Element) -> Optional[str]:
        """
        Infer game version based on structural elements

        Different Alpha versions have different XML structures
        """
        # Check for specific attributes that indicate version
        gamedata = root.find('gamedata')
        if gamedata is not None:
            # Alpha 20 has galaxyCount attribute
            if 'galaxyCount' in gamedata.attrib:
                return "Alpha 20+"

        # Check for system generation markers
        starmap = root.find('starmap')
        if starmap is not None:
            systems = starmap.find('systems')
            if systems is not None:
                for system in systems.findall('l'):
                    # Alpha 20 has 'gen' attribute in systems
                    if 'gen' in system.attrib:
                        return "Alpha 20+"

        return "Alpha <20 (inferred)"

    def _analyze_structure(self, root: ET.Element, max_depth: int = 3) -> Dict[str, Any]:
        """
        Recursively analyze XML structure up to a certain depth

        Returns a dict representing the tree structure
        """
        def _analyze_node(node: ET.Element, depth: int) -> Dict[str, Any]:
            if depth > max_depth:
                return {"_truncated": True}

            result = {
                "_tag": node.tag,
                "_attributes": list(node.attrib.keys()),
                "_children": []
            }

            # Group children by tag
            children_by_tag: Dict[str, int] = {}
            for child in node:
                tag = child.tag
                children_by_tag[tag] = children_by_tag.get(tag, 0) + 1

            result["_child_counts"] = children_by_tag

            # Analyze first child of each type
            seen_tags = set()
            for child in node:
                if child.tag not in seen_tags:
                    result["_children"].append(_analyze_node(child, depth + 1))
                    seen_tags.add(child.tag)

            return result

        return _analyze_node(root, 0)

    def _extract_entity_types(self, root: ET.Element) -> Set[str]:
        """Extract all entity types found in the save"""
        entity_types = set()

        # Look in sectors for entities
        for sector in root.findall('.//sector'):
            for entity in sector.findall('.//entity'):
                entity_type = entity.attrib.get('type')
                if entity_type:
                    entity_types.add(entity_type)

        # Look for ship entities
        for ship in root.findall('.//ship'):
            entity_types.add('Ship')

        # Look for character entities
        for char in root.findall('.//character'):
            entity_types.add('Character')

        return entity_types

    def _extract_facilities_and_items(self, root: ET.Element) -> Tuple[Set[str], Dict[str, str]]:
        """
        Extract facility types and item ID mappings

        Returns:
            Tuple of (facility_types, item_id_mappings)
        """
        facility_types = set()
        item_ids = {}

        # Look for facilities in sectors/ships
        for facility in root.findall('.//facility'):
            fac_type = facility.attrib.get('type')
            fac_id = facility.attrib.get('id')
            if fac_type:
                facility_types.add(fac_type)
            if fac_id and fac_type:
                item_ids[fac_id] = fac_type

        # Look for items in storage
        for item in root.findall('.//item'):
            item_id = item.attrib.get('id')
            item_type = item.attrib.get('type') or item.attrib.get('name')
            if item_id and item_type:
                item_ids[item_id] = item_type

        return facility_types, item_ids

    def compare_saves(self, baseline_path: Path, comparison_path: Path) -> VersionComparison:
        """
        Compare two save files and identify differences

        Args:
            baseline_path: Path to the newer/reference save file
            comparison_path: Path to the older save file to compare

        Returns:
            VersionComparison with detailed differences
        """
        self.logger.info(f"Comparing save files:")
        self.logger.info(f"  Baseline: {baseline_path}")
        self.logger.info(f"  Comparison: {comparison_path}")

        # Analyze both saves
        baseline_info = self.analyze_save_file(baseline_path)
        comparison_info = self.analyze_save_file(comparison_path)

        comparison = VersionComparison(
            baseline_file=str(baseline_path),
            comparison_file=str(comparison_path),
            baseline_version=baseline_info.version,
            comparison_version=comparison_info.version
        )

        # Compare root attributes
        baseline_attrs = set(baseline_info.root_attributes.keys())
        comparison_attrs = set(comparison_info.root_attributes.keys())

        missing_attrs = baseline_attrs - comparison_attrs
        new_attrs = comparison_attrs - baseline_attrs

        if missing_attrs:
            comparison.missing_elements.extend([f"Root attribute: {attr}" for attr in missing_attrs])
        if new_attrs:
            comparison.new_elements.extend([f"Root attribute: {attr}" for attr in new_attrs])

        # Compare entity types
        missing_entities = baseline_info.entity_types - comparison_info.entity_types
        new_entities = comparison_info.entity_types - baseline_info.entity_types

        if missing_entities:
            comparison.missing_elements.extend([f"Entity type: {entity}" for entity in missing_entities])
        if new_entities:
            comparison.new_elements.extend([f"Entity type: {entity}" for entity in new_entities])

        # Compare facility types
        missing_facilities = baseline_info.facility_types - comparison_info.facility_types
        new_facilities = comparison_info.facility_types - baseline_info.facility_types

        if missing_facilities:
            comparison.missing_elements.extend([f"Facility type: {fac}" for fac in missing_facilities])
        if new_facilities:
            comparison.new_elements.extend([f"Facility type: {fac}" for fac in new_facilities])

        # Compare item IDs
        baseline_ids = set(baseline_info.item_ids.keys())
        comparison_ids = set(comparison_info.item_ids.keys())
        common_ids = baseline_ids & comparison_ids

        for item_id in common_ids:
            baseline_name = baseline_info.item_ids[item_id]
            comparison_name = comparison_info.item_ids[item_id]
            if baseline_name != comparison_name:
                comparison.id_changes.append((item_id, comparison_name, baseline_name))

        # Compare XML structure
        self._compare_structures(
            baseline_info.xml_structure,
            comparison_info.xml_structure,
            comparison,
            path="root"
        )

        # Generate compatibility notes
        self._generate_compatibility_notes(comparison)

        self.logger.info(f"Comparison complete:")
        self.logger.info(f"  Missing elements: {len(comparison.missing_elements)}")
        self.logger.info(f"  New elements: {len(comparison.new_elements)}")
        self.logger.info(f"  ID changes: {len(comparison.id_changes)}")
        self.logger.info(f"  Structural differences: {len(comparison.structural_differences)}")

        return comparison

    def _compare_structures(
        self,
        baseline: Dict[str, Any],
        comparison: Dict[str, Any],
        result: VersionComparison,
        path: str
    ):
        """Recursively compare XML structures"""
        # Compare child counts
        baseline_children = baseline.get('_child_counts', {})
        comparison_children = comparison.get('_child_counts', {})

        baseline_tags = set(baseline_children.keys())
        comparison_tags = set(comparison_children.keys())

        missing_tags = baseline_tags - comparison_tags
        new_tags = comparison_tags - baseline_tags

        for tag in missing_tags:
            result.structural_differences.append(
                f"Missing element at {path}: <{tag}> (present in baseline)"
            )

        for tag in new_tags:
            result.structural_differences.append(
                f"New element at {path}: <{tag}> (not in baseline)"
            )

    def _generate_compatibility_notes(self, comparison: VersionComparison):
        """Generate human-readable compatibility notes"""
        if comparison.missing_elements:
            comparison.compatibility_notes.append(
                f"The older save is missing {len(comparison.missing_elements)} elements present in the newer version."
            )

        if comparison.id_changes:
            comparison.compatibility_notes.append(
                f"Found {len(comparison.id_changes)} item/facility ID changes between versions."
            )

        if comparison.structural_differences:
            comparison.compatibility_notes.append(
                f"Detected {len(comparison.structural_differences)} structural differences in the XML format."
            )

        if not comparison.missing_elements and not comparison.id_changes and not comparison.structural_differences:
            comparison.compatibility_notes.append(
                "Save files appear to be structurally compatible."
            )

    def generate_comparison_report(
        self,
        comparison: VersionComparison,
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate a detailed comparison report in Markdown format

        Args:
            comparison: The VersionComparison to report on
            output_path: Optional path to write the report to

        Returns:
            The report as a string
        """
        lines = [
            f"# Space Haven Save File Version Comparison Report",
            f"",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## Files Compared",
            f"",
            f"- **Baseline (newer):** `{Path(comparison.baseline_file).name}`",
            f"  - Version: {comparison.baseline_version or 'Unknown'}",
            f"- **Comparison (older):** `{Path(comparison.comparison_file).name}`",
            f"  - Version: {comparison.comparison_version or 'Unknown'}",
            f"",
            f"## Summary",
            f"",
        ]

        for note in comparison.compatibility_notes:
            lines.append(f"- {note}")

        lines.append("")

        # Missing elements
        if comparison.missing_elements:
            lines.extend([
                f"## Missing Elements in Older Save",
                f"",
                f"The following elements are present in the newer version but missing in the older save:",
                f"",
            ])
            for element in sorted(comparison.missing_elements):
                lines.append(f"- {element}")
            lines.append("")

        # New elements
        if comparison.new_elements:
            lines.extend([
                f"## Elements Only in Older Save",
                f"",
                f"These elements exist in the older save but not in the newer version (possibly deprecated):",
                f"",
            ])
            for element in sorted(comparison.new_elements):
                lines.append(f"- {element}")
            lines.append("")

        # ID changes
        if comparison.id_changes:
            lines.extend([
                f"## Item/Facility ID Changes",
                f"",
                f"The following IDs map to different items between versions:",
                f"",
                f"| ID | Old Version | New Version |",
                f"|----|-------------|-------------|",
            ])
            for item_id, old_name, new_name in sorted(comparison.id_changes):
                lines.append(f"| `{item_id}` | {old_name} | {new_name} |")
            lines.append("")

        # Structural differences
        if comparison.structural_differences:
            lines.extend([
                f"## Structural Differences",
                f"",
                f"XML structure differences detected:",
                f"",
            ])
            for diff in sorted(comparison.structural_differences):
                lines.append(f"- {diff}")
            lines.append("")

        # Migration recommendations
        lines.extend([
            f"## Migration Recommendations",
            f"",
        ])

        if comparison.missing_elements or comparison.structural_differences:
            lines.extend([
                f"### Caution Required",
                f"",
                f"This older save file has significant differences from the current game version. Consider:",
                f"",
                f"1. **Backup First:** Always keep the original save file",
                f"2. **Test Carefully:** Load the save and verify all systems work",
                f"3. **Expect Issues:** Some features may not work correctly",
                f"4. **Manual Fixes:** You may need to manually add/fix elements",
                f"",
            ])
        else:
            lines.extend([
                f"The save files appear compatible. Migration should be relatively safe, but always backup first.",
                f"",
            ])

        report = "\n".join(lines)

        # Write to file if requested
        if output_path:
            output_path.write_text(report, encoding='utf-8')
            self.logger.info(f"Report written to: {output_path}")

        return report

    def analyze_all_saves(
        self,
        save_dir: Path,
        baseline_save: Optional[Path] = None
    ) -> Dict[str, VersionComparison]:
        """
        Analyze all save files in a directory and compare them to a baseline

        Args:
            save_dir: Directory containing save folders
            baseline_save: Optional path to baseline save (defaults to newest)

        Returns:
            Dictionary mapping save names to their comparisons
        """
        self.logger.info(f"Analyzing all saves in: {save_dir}")

        # Find all save files
        save_files = []
        for path in save_dir.rglob('game'):
            # Skip if it's in a backup folder
            if 'backup' not in str(path).lower():
                save_files.append(path)

        self.logger.info(f"Found {len(save_files)} save files")

        if not save_files:
            return {}

        # Determine baseline
        if baseline_save is None:
            # Use the most recently modified as baseline
            baseline_save = max(save_files, key=lambda p: p.stat().st_mtime)
            self.logger.info(f"Using most recent save as baseline: {baseline_save}")

        # Compare all saves to baseline
        comparisons = {}
        for save_file in save_files:
            if save_file != baseline_save:
                try:
                    comparison = self.compare_saves(baseline_save, save_file)
                    comparisons[str(save_file)] = comparison
                except Exception as e:
                    self.logger.error(f"Error comparing {save_file}: {e}")

        return comparisons

    def save_analysis_cache(self, cache_path: Path):
        """Save analyzed save information to a JSON cache file"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'saves': {}
        }

        for path_str, info in self.analyzed_saves.items():
            cache_data['saves'][path_str] = {
                'version': info.version,
                'game_mode': info.game_mode,
                'id_counter': info.id_counter,
                'sector_count': info.sector_count,
                'root_attributes': info.root_attributes,
                'gamedata_attributes': info.gamedata_attributes,
                'entity_types': list(info.entity_types),
                'facility_types': list(info.facility_types),
                'item_ids': info.item_ids,
            }

        cache_path.write_text(json.dumps(cache_data, indent=2), encoding='utf-8')
        self.logger.info(f"Analysis cache saved to: {cache_path}")

    def load_analysis_cache(self, cache_path: Path):
        """Load previously analyzed save information from cache"""
        if not cache_path.exists():
            self.logger.warning(f"Cache file not found: {cache_path}")
            return

        cache_data = json.loads(cache_path.read_text(encoding='utf-8'))
        self.logger.info(f"Loading analysis cache from: {cache_path}")
        self.logger.info(f"  Cache timestamp: {cache_data.get('timestamp')}")

        for path_str, data in cache_data.get('saves', {}).items():
            info = SaveFileInfo(
                file_path=Path(path_str),
                version=data.get('version'),
                game_mode=data.get('game_mode'),
                id_counter=data.get('id_counter'),
                sector_count=data.get('sector_count'),
                root_attributes=data.get('root_attributes', {}),
                gamedata_attributes=data.get('gamedata_attributes', {}),
                entity_types=set(data.get('entity_types', [])),
                facility_types=set(data.get('facility_types', [])),
                item_ids=data.get('item_ids', {}),
            )
            self.analyzed_saves[path_str] = info

        self.logger.info(f"Loaded {len(self.analyzed_saves)} cached analyses")


def main():
    """Command-line interface for version analysis"""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    analyzer = SaveFileVersionAnalyzer()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python version_analyzer.py <save_directory>")
        print("  python version_analyzer.py <baseline_save> <comparison_save>")
        sys.exit(1)

    if len(sys.argv) == 2:
        # Analyze all saves in directory
        save_dir = Path(sys.argv[1])
        comparisons = analyzer.analyze_all_saves(save_dir)

        # Generate reports
        reports_dir = save_dir / 'version_reports'
        reports_dir.mkdir(exist_ok=True)

        for save_path, comparison in comparisons.items():
            save_name = Path(save_path).parent.parent.name
            report_path = reports_dir / f"{save_name}_comparison.md"
            analyzer.generate_comparison_report(comparison, report_path)

        # Save cache
        cache_path = save_dir / 'version_analysis_cache.json'
        analyzer.save_analysis_cache(cache_path)

        print(f"\nGenerated {len(comparisons)} comparison reports in: {reports_dir}")
        print(f"Analysis cache saved to: {cache_path}")

    else:
        # Compare two specific saves
        baseline = Path(sys.argv[1])
        comparison = Path(sys.argv[2])

        result = analyzer.compare_saves(baseline, comparison)
        report = analyzer.generate_comparison_report(result)
        print(report)


if __name__ == '__main__':
    main()
