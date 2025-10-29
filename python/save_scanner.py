"""
Save file scanner for detecting unknown IDs in Space Haven save files
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from reference_data import ReferenceData


@dataclass
class UnknownItem:
    """Represents an unknown item found in a save file"""
    id_value: int
    id_type: str  # attribute, skill, trait, storage_item, condition, research, craft, or generic
    xml_path: str  # XPath to the element containing this ID
    xml_tag: str  # The XML tag name
    xml_attributes: Dict[str, str] = field(default_factory=dict)
    occurrences: int = 1
    
    def __str__(self):
        return f"Unknown {self.id_type} ID {self.id_value} in <{self.xml_tag}> at {self.xml_path}"


@dataclass
class ScanResult:
    """Results from scanning a save file"""
    file_path: str
    scan_timestamp: str
    total_ids_found: int = 0
    known_ids_count: int = 0
    unknown_ids_count: int = 0
    unknown_items: List[UnknownItem] = field(default_factory=list)
    id_summary: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    def add_unknown_item(self, item: UnknownItem):
        """Add an unknown item to the results"""
        # Check if we already have this item
        for existing in self.unknown_items:
            if existing.id_value == item.id_value and existing.id_type == item.id_type:
                existing.occurrences += 1
                return
        
        self.unknown_items.append(item)
        self.unknown_ids_count += 1
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the scan results"""
        summary = [
            f"Scan Results for: {Path(self.file_path).name}",
            f"Scanned at: {self.scan_timestamp}",
            f"",
            f"Total IDs found: {self.total_ids_found}",
            f"Known IDs: {self.known_ids_count}",
            f"Unknown IDs: {self.unknown_ids_count}",
            f"",
        ]
        
        if self.unknown_items:
            summary.append("Unknown Items Detected:")
            summary.append("-" * 80)
            for item in sorted(self.unknown_items, key=lambda x: (x.id_type, x.id_value)):
                summary.append(f"  {item}")
                summary.append(f"    Attributes: {item.xml_attributes}")
                summary.append(f"    Occurrences: {item.occurrences}")
                summary.append("")
        else:
            summary.append("✓ No unknown IDs detected!")
        
        return "\n".join(summary)


class SaveFileScanner:
    """Scanner for detecting unknown IDs in Space Haven save files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reference = ReferenceData()
        
    def scan_file(self, file_path: str) -> ScanResult:
        """
        Scan a save file for unknown IDs
        
        Args:
            file_path: Path to the Space Haven save file
            
        Returns:
            ScanResult object containing detected unknown items
        """
        self.logger.info(f"Starting scan of file: {file_path}")
        
        result = ScanResult(
            file_path=file_path,
            scan_timestamp=datetime.now().isoformat()
        )
        
        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Scan different sections
            self._scan_characters(root, result)
            self._scan_storage(root, result)
            self._scan_research(root, result)
            self._scan_crafts(root, result)
            self._scan_generic_ids(root, result)
            
            self.logger.info(f"Scan complete: {result.unknown_ids_count} unknown IDs found")
            
        except Exception as e:
            self.logger.error(f"Error scanning file: {str(e)}", exc_info=True)
            raise
        
        return result
    
    def _get_element_path(self, element: ET.Element, root: ET.Element) -> str:
        """Get a simplified XPath for an element"""
        # This is a simplified approach - actual XPath would be more complex
        return f"//{element.tag}[@{list(element.attrib.keys())[0]}='{list(element.attrib.values())[0]}']" if element.attrib else f"//{element.tag}"
    
    def _scan_characters(self, root: ET.Element, result: ScanResult):
        """Scan character elements for unknown attribute, skill, trait, and condition IDs"""
        self.logger.info("Scanning character data...")
        
        for char_elem in root.findall(".//c"):
            char_id = char_elem.get("entId", "unknown")
            self.logger.debug(f"Scanning character {char_id}")
            
            # Scan attributes
            pers_elem = char_elem.find("pers")
            if pers_elem is not None:
                attr_elem = pers_elem.find("attr")
                if attr_elem is not None:
                    for a_elem in attr_elem.findall("a"):
                        attr_id = int(a_elem.get("id", "0"))
                        result.total_ids_found += 1
                        
                        if not self.reference.is_known_id(attr_id, "attributes"):
                            item = UnknownItem(
                                id_value=attr_id,
                                id_type="attribute",
                                xml_path=f"//c[@entId='{char_id}']/pers/attr/a",
                                xml_tag="a",
                                xml_attributes=dict(a_elem.attrib)
                            )
                            result.add_unknown_item(item)
                            self.logger.warning(f"Unknown attribute ID: {attr_id}")
                        else:
                            result.known_ids_count += 1
                
                # Scan skills
                skills_elem = pers_elem.find("skills")
                if skills_elem is not None:
                    for s_elem in skills_elem.findall("s"):
                        skill_id = int(s_elem.get("id", "0"))
                        result.total_ids_found += 1
                        
                        if not self.reference.is_known_id(skill_id, "skills"):
                            item = UnknownItem(
                                id_value=skill_id,
                                id_type="skill",
                                xml_path=f"//c[@entId='{char_id}']/pers/skills/s",
                                xml_tag="s",
                                xml_attributes=dict(s_elem.attrib)
                            )
                            result.add_unknown_item(item)
                            self.logger.warning(f"Unknown skill ID: {skill_id}")
                        else:
                            result.known_ids_count += 1
                
                # Scan traits
                traits_elem = pers_elem.find("traits")
                if traits_elem is not None:
                    for t_elem in traits_elem.findall("t"):
                        trait_id = int(t_elem.get("id", "0"))
                        result.total_ids_found += 1
                        
                        if not self.reference.is_known_id(trait_id, "traits"):
                            item = UnknownItem(
                                id_value=trait_id,
                                id_type="trait",
                                xml_path=f"//c[@entId='{char_id}']/pers/traits/t",
                                xml_tag="t",
                                xml_attributes=dict(t_elem.attrib)
                            )
                            result.add_unknown_item(item)
                            self.logger.warning(f"Unknown trait ID: {trait_id}")
                        else:
                            result.known_ids_count += 1
                
                # Scan conditions
                conditions_elem = pers_elem.find("conditions")
                if conditions_elem is not None:
                    for cond_elem in conditions_elem.findall("c"):
                        cond_id = int(cond_elem.get("id", "0"))
                        result.total_ids_found += 1
                        
                        if not self.reference.is_known_id(cond_id, "conditions"):
                            item = UnknownItem(
                                id_value=cond_id,
                                id_type="condition",
                                xml_path=f"//c[@entId='{char_id}']/pers/conditions/c",
                                xml_tag="c",
                                xml_attributes=dict(cond_elem.attrib)
                            )
                            result.add_unknown_item(item)
                            self.logger.warning(f"Unknown condition ID: {cond_id}")
                        else:
                            result.known_ids_count += 1
    
    def _scan_storage(self, root: ET.Element, result: ScanResult):
        """Scan storage elements for unknown item IDs"""
        self.logger.info("Scanning storage data...")
        
        # Try multiple patterns for storage items
        # Pattern 1: items with 'id' attribute
        for item_elem in root.findall(".//item"):
            if 'id' in item_elem.attrib:
                item_id_str = item_elem.get("id", "")
                try:
                    item_id = int(item_id_str)
                    result.total_ids_found += 1
                    
                    if not self.reference.is_known_id(item_id, "storage_items"):
                        item = UnknownItem(
                            id_value=item_id,
                            id_type="storage_item",
                            xml_path="//item",
                            xml_tag="item",
                            xml_attributes=dict(item_elem.attrib)
                        )
                        result.add_unknown_item(item)
                        self.logger.warning(f"Unknown storage item ID: {item_id}")
                    else:
                        result.known_ids_count += 1
                except ValueError:
                    # Non-numeric ID, skip
                    pass
        
        # Pattern 2: Look for other storage-related elements
        for storage_elem in root.findall(".//s"):
            if 'objId' in storage_elem.attrib:
                obj_id_str = storage_elem.get("objId", "")
                try:
                    obj_id = int(obj_id_str)
                    result.total_ids_found += 1
                    
                    if not self.reference.is_known_id(obj_id, "storage_items"):
                        item = UnknownItem(
                            id_value=obj_id,
                            id_type="storage_item",
                            xml_path="//s[@objId]",
                            xml_tag="s",
                            xml_attributes=dict(storage_elem.attrib)
                        )
                        result.add_unknown_item(item)
                        self.logger.warning(f"Unknown storage object ID: {obj_id}")
                    else:
                        result.known_ids_count += 1
                except ValueError:
                    pass
    
    def _scan_research(self, root: ET.Element, result: ScanResult):
        """Scan research/technology elements for unknown IDs"""
        self.logger.info("Scanning research data...")
        
        for research_elem in root.findall(".//research"):
            if 'id' in research_elem.attrib:
                research_id = int(research_elem.get("id", "0"))
                result.total_ids_found += 1
                
                if not self.reference.is_known_id(research_id, "research"):
                    item = UnknownItem(
                        id_value=research_id,
                        id_type="research",
                        xml_path="//research",
                        xml_tag="research",
                        xml_attributes=dict(research_elem.attrib)
                    )
                    result.add_unknown_item(item)
                    self.logger.warning(f"Unknown research ID: {research_id}")
                else:
                    result.known_ids_count += 1
    
    def _scan_crafts(self, root: ET.Element, result: ScanResult):
        """Scan craft elements for unknown craft IDs"""
        self.logger.info("Scanning craft data...")
        
        for craft_elem in root.findall(".//craft"):
            if 'type' in craft_elem.attrib:
                craft_id = int(craft_elem.get("type", "0"))
                result.total_ids_found += 1
                
                if not self.reference.is_known_id(craft_id, "crafts"):
                    item = UnknownItem(
                        id_value=craft_id,
                        id_type="craft",
                        xml_path="//craft",
                        xml_tag="craft",
                        xml_attributes=dict(craft_elem.attrib)
                    )
                    result.add_unknown_item(item)
                    self.logger.warning(f"Unknown craft ID: {craft_id}")
                else:
                    result.known_ids_count += 1
    
    def _scan_generic_ids(self, root: ET.Element, result: ScanResult):
        """
        Scan for generic ID attributes that might contain unknown IDs
        This is a catch-all for any IDs we haven't explicitly checked
        """
        self.logger.info("Scanning for generic IDs...")
        
        # Common attribute names that often contain IDs
        id_attributes = ['id', 'type', 'objId', 'itemId', 'typeId']
        
        for elem in root.iter():
            for attr_name in id_attributes:
                if attr_name in elem.attrib:
                    attr_value = elem.get(attr_name, "")
                    try:
                        id_value = int(attr_value)
                        
                        # Skip if we already checked this in specific scans
                        if elem.tag in ['c', 'a', 's', 't', 'item', 'research', 'craft']:
                            continue
                        
                        result.total_ids_found += 1
                        
                        # Check if this ID is known in any category
                        if not self.reference.is_known_id(id_value):
                            item = UnknownItem(
                                id_value=id_value,
                                id_type="generic",
                                xml_path=f"//{elem.tag}",
                                xml_tag=elem.tag,
                                xml_attributes=dict(elem.attrib)
                            )
                            result.add_unknown_item(item)
                            self.logger.debug(f"Unknown generic ID: {id_value} in <{elem.tag}>")
                        else:
                            result.known_ids_count += 1
                            
                    except ValueError:
                        # Not a numeric ID, skip
                        pass
    
    def generate_bug_report(self, result: ScanResult) -> str:
        """
        Generate a bug report for unknown IDs found in the scan
        
        Args:
            result: ScanResult from scanning a save file
            
        Returns:
            Formatted bug report text suitable for GitHub issue
        """
        if not result.unknown_items:
            return "No unknown IDs detected - no bug report needed."
        
        report = [
            "# Unknown IDs Detected in Save File",
            "",
            f"**Save File:** `{Path(result.file_path).name}`",
            f"**Scan Date:** {result.scan_timestamp}",
            f"**Unknown IDs Found:** {result.unknown_ids_count}",
            "",
            "## Summary",
            "",
            f"During analysis of a Space Haven save file, {result.unknown_ids_count} unknown ID(s) were detected that are not present in the reference data. These may be new items added in a recent game update.",
            "",
            "## Unknown IDs Detected",
            ""
        ]
        
        # Group by type
        by_type: Dict[str, List[UnknownItem]] = {}
        for item in result.unknown_items:
            if item.id_type not in by_type:
                by_type[item.id_type] = []
            by_type[item.id_type].append(item)
        
        for id_type, items in sorted(by_type.items()):
            report.append(f"### {id_type.title()}s")
            report.append("")
            for item in sorted(items, key=lambda x: x.id_value):
                report.append(f"- **ID {item.id_value}**")
                report.append(f"  - XML Tag: `<{item.xml_tag}>`")
                report.append(f"  - Attributes: `{item.xml_attributes}`")
                report.append(f"  - Occurrences: {item.occurrences}")
                report.append(f"  - Location: `{item.xml_path}`")
                report.append("")
        
        report.extend([
            "## Next Steps",
            "",
            "Please investigate these IDs and update the reference data if they are valid new game items.",
            "",
            "---",
            "*This report was automatically generated by Space Haven Save Editor*"
        ])
        
        return "\n".join(report)
    
    def save_report_to_file(self, result: ScanResult, output_path: str = None) -> str:
        """
        Save a bug report to a file
        
        Args:
            result: ScanResult from scanning
            output_path: Optional path to save report. If None, generates a default name.
            
        Returns:
            Path to the saved report file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"unknown_ids_report_{timestamp}.md"
        
        report_content = self.generate_bug_report(result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Bug report saved to: {output_path}")
        return output_path
