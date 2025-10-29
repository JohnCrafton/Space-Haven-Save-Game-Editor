#!/usr/bin/env python3
"""
Space Haven Save Editor - Python Version
A cross-platform save editor for Space Haven, optimized for Steam Deck

Original VB.NET version by Moragar
Python port for cross-platform compatibility
"""

import sys
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QGroupBox,
    QSpinBox, QHeaderView, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction

from models import Character, Ship, DataProp, RelationshipInfo, StorageContainer, StorageItem


def setup_logging():
    """Configure logging to write to a dated log file adjacent to the script"""
    # Get the directory where the script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"space_haven_editor_{timestamp}.log"
    log_path = script_dir / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_path, mode='w', encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("Space Haven Save Editor - Logging Started")
    logger.info(f"Log file: {log_path}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Script directory: {script_dir}")
    logger.info("="*80)
    
    return logger


class IdCollection:
    """Collection of game item IDs and names"""
    def __init__(self):
        self.items = {}
        self.load_default_items()
    
    def load_default_items(self):
        """Load default game items - can be expanded based on game data"""
        self.items = {
            "food": "Food",
            "water": "Water",
            "oxygen": "Oxygen",
            "energy": "Energy Cells",
            "metal": "Metal",
            "chemicals": "Chemicals",
            "electronics": "Electronics",
            "fabric": "Fabric",
        }
    
    def get_name(self, item_id: str) -> str:
        return self.items.get(item_id, item_id)


class SpaceHavenEditor(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing SpaceHavenEditor main window")
        
        self.setWindowTitle("Space Haven Save Editor - Python Edition")
        self.setMinimumSize(1000, 700)
        
        # Data storage
        self.current_file_path: str = ""
        self.xml_tree: Optional[ET.ElementTree] = None
        self.xml_root: Optional[ET.Element] = None
        self.characters: List[Character] = []
        self.ships: List[Ship] = []
        self.id_collection = IdCollection()
        
        # Settings
        self.settings = QSettings("SpaceHavenEditor", "SaveEditor")
        self.backup_enabled = self.settings.value("backup_on_open", True, type=bool)
        self.logger.info(f"Backup on open: {self.backup_enabled}")
        
        # Setup UI
        self.init_ui()
        self.logger.info("SpaceHavenEditor initialization complete")
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Global settings section
        global_group = self.create_global_settings_group()
        main_layout.addWidget(global_group)
        
        # Ship selection
        ship_layout = QHBoxLayout()
        ship_layout.addWidget(QLabel("Selected Ship:"))
        self.ship_combo = QComboBox()
        self.ship_combo.currentIndexChanged.connect(self.on_ship_selected)
        ship_layout.addWidget(self.ship_combo)
        ship_layout.addStretch()
        main_layout.addLayout(ship_layout)
        
        # Tab widget for different sections
        self.tabs = QTabWidget()
        
        # Ship info tab
        self.ship_tab = self.create_ship_tab()
        self.tabs.addTab(self.ship_tab, "Ship Info")
        
        # Crew tab
        self.crew_tab = self.create_crew_tab()
        self.tabs.addTab(self.crew_tab, "Crew")
        
        # Storage tab
        self.storage_tab = self.create_storage_tab()
        self.tabs.addTab(self.storage_tab, "Storage")
        
        main_layout.addWidget(self.tabs)
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Save File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("S&ettings...", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_global_settings_group(self) -> QGroupBox:
        """Create the global settings group"""
        group = QGroupBox("Global Settings")
        layout = QHBoxLayout()
        
        # Credits
        layout.addWidget(QLabel("Credits:"))
        self.credits_input = QLineEdit()
        self.credits_input.setMaximumWidth(150)
        layout.addWidget(self.credits_input)
        
        # Prestige Points
        layout.addWidget(QLabel("Prestige Points:"))
        self.prestige_input = QLineEdit()
        self.prestige_input.setMaximumWidth(150)
        layout.addWidget(self.prestige_input)
        
        # Sandbox mode
        self.sandbox_check = QCheckBox("Sandbox Mode")
        layout.addWidget(self.sandbox_check)
        
        # Update button
        update_btn = QPushButton("Update Global Settings")
        update_btn.clicked.connect(self.update_global_settings)
        layout.addWidget(update_btn)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
        
    def create_ship_tab(self) -> QWidget:
        """Create the ship information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Ship dimensions
        dim_layout = QHBoxLayout()
        dim_layout.addWidget(QLabel("Ship Dimensions:"))
        
        dim_layout.addWidget(QLabel("Width:"))
        self.ship_width = QSpinBox()
        self.ship_width.setRange(1, 100)
        dim_layout.addWidget(self.ship_width)
        
        dim_layout.addWidget(QLabel("Height:"))
        self.ship_height = QSpinBox()
        self.ship_height.setRange(1, 100)
        dim_layout.addWidget(self.ship_height)
        
        update_size_btn = QPushButton("Update Ship Size")
        update_size_btn.clicked.connect(self.update_ship_size)
        dim_layout.addWidget(update_size_btn)
        
        dim_layout.addStretch()
        layout.addLayout(dim_layout)
        
        # Ship info display
        self.ship_info = QLabel("Select a ship to view details")
        layout.addWidget(self.ship_info)
        
        layout.addStretch()
        return widget
        
    def create_crew_tab(self) -> QWidget:
        """Create the crew management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Crew list
        crew_list_layout = QHBoxLayout()
        crew_list_layout.addWidget(QLabel("Crew Members:"))
        self.crew_list = QComboBox()
        self.crew_list.currentIndexChanged.connect(self.on_crew_selected)
        crew_list_layout.addWidget(self.crew_list)
        
        add_crew_btn = QPushButton("Add Crew Member")
        add_crew_btn.clicked.connect(self.add_crew_member)
        crew_list_layout.addWidget(add_crew_btn)
        
        crew_list_layout.addStretch()
        layout.addLayout(crew_list_layout)
        
        # Crew details table
        self.crew_table = QTableWidget()
        self.crew_table.setColumnCount(3)
        self.crew_table.setHorizontalHeaderLabels(["Property", "Value", "Max"])
        self.crew_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.crew_table)
        
        return widget
        
    def create_storage_tab(self) -> QWidget:
        """Create the storage management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Container selection
        container_layout = QHBoxLayout()
        container_layout.addWidget(QLabel("Storage Container:"))
        self.container_combo = QComboBox()
        self.container_combo.currentIndexChanged.connect(self.on_container_selected)
        container_layout.addWidget(self.container_combo)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        # Storage items table
        self.storage_table = QTableWidget()
        self.storage_table.setColumnCount(3)
        self.storage_table.setHorizontalHeaderLabels(["Item ID", "Item Name", "Quantity"])
        self.storage_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.storage_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.add_storage_item)
        btn_layout.addWidget(add_item_btn)
        
        remove_item_btn = QPushButton("Remove Item")
        remove_item_btn.clicked.connect(self.remove_storage_item)
        btn_layout.addWidget(remove_item_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return widget
        
    def open_file(self):
        """Open a save file"""
        self.logger.info("Opening file dialog")
        
        # Determine initial directory
        home = str(Path.home())
        initial_dir = home
        
        # Try to find Steam's common save location
        possible_paths = [
            Path.home() / ".steam" / "steam" / "steamapps" / "common" / "SpaceHaven" / "savegames",
            Path.home() / ".local" / "share" / "Steam" / "steamapps" / "common" / "SpaceHaven" / "savegames",
            Path.home() / "Documents" / "My Games" / "SpaceHaven" / "savegames",
        ]
        
        for path in possible_paths:
            if path.exists():
                initial_dir = str(path)
                self.logger.info(f"Found Steam save directory: {initial_dir}")
                break
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Space Haven Save File",
            initial_dir,
            "Space Haven Save (game);;All Files (*.*)"
        )
        
        if not file_path:
            self.logger.info("File dialog cancelled by user")
            return
        
        self.logger.info(f"Selected file: {file_path}")
            
        # Backup if enabled
        if self.backup_enabled:
            self.logger.info("Creating backup...")
            self.create_backup(file_path)
        
        # Reset application state
        self.logger.info("Resetting application state")
        self.reset_application_state()
        
        # Load the file
        try:
            self.current_file_path = file_path
            self.logger.info(f"Loading save file from: {file_path}")
            self.load_save_file(file_path)
            self.setWindowTitle(f"Space Haven Save Editor - {Path(file_path).name}")
            self.logger.info("Save file loaded successfully")
            QMessageBox.information(self, "Success", "Save file loaded successfully!")
        except Exception as e:
            self.logger.error(f"Failed to load save file: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load save file:\n{str(e)}")
            self.reset_application_state()
            
    def create_backup(self, file_path: str):
        """Create a backup of the save file"""
        try:
            source_dir = Path(file_path).parent
            parent_dir = source_dir.parent
            savegames_dir = parent_dir.parent
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{parent_dir.name}_{source_dir.name}_backup_{timestamp}"
            backup_path = savegames_dir / backup_name
            
            self.logger.info(f"Creating backup from {source_dir} to {backup_path}")
            shutil.copytree(source_dir, backup_path)
            self.logger.info("Backup created successfully")
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}", exc_info=True)
            QMessageBox.warning(
                self,
                "Backup Failed",
                f"Failed to create backup:\n{str(e)}\n\nContinuing to load original file."
            )
            
    def load_save_file(self, file_path: str):
        """Load and parse the save file"""
        self.logger.info("="*60)
        self.logger.info("Starting to load save file")
        self.logger.info(f"File path: {file_path}")
        self.logger.info(f"File size: {Path(file_path).stat().st_size} bytes")
        
        # Parse XML
        self.logger.info("Parsing XML...")
        try:
            self.xml_tree = ET.parse(file_path)
            self.xml_root = self.xml_tree.getroot()
            self.logger.info(f"XML root tag: {self.xml_root.tag}")
            self.logger.info(f"XML root attributes: {self.xml_root.attrib}")
        except Exception as e:
            self.logger.error(f"XML parsing failed: {str(e)}", exc_info=True)
            raise
        
        if self.xml_root.tag != "game":
            error_msg = f"Invalid save file: root element is '{self.xml_root.tag}', expected 'game'"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Log XML structure overview
        self.logger.info("XML structure overview:")
        for child in self.xml_root:
            self.logger.info(f"  - {child.tag} (attributes: {list(child.attrib.keys())})")
        
        # Load different sections
        self.logger.info("Loading global settings...")
        self.load_global_settings()
        
        self.logger.info("Loading ships...")
        self.load_ships()
        
        self.logger.info("Loading characters...")
        self.load_characters()
        
        # Populate UI
        if self.ships:
            self.logger.info(f"Populating ship combo with {len(self.ships)} ships")
            self.ship_combo.clear()
            for ship in self.ships:
                self.ship_combo.addItem(str(ship), ship)
                self.logger.debug(f"  Added ship: {ship}")
            self.ship_combo.setCurrentIndex(0)
        else:
            self.logger.warning("No ships found in save file!")
        
        self.logger.info("="*60)
            
    def load_global_settings(self):
        """Load global settings from XML"""
        if self.xml_root is None:
            self.logger.warning("load_global_settings: xml_root is None")
            return
        
        self.logger.info("Loading global settings...")
            
        # Load credits
        bank_elem = self.xml_root.find("playerBank")
        if bank_elem is not None:
            credits = bank_elem.get("ca", "0")
            self.credits_input.setText(credits)
            self.logger.info(f"  Credits: {credits}")
            self.logger.debug(f"  playerBank attributes: {bank_elem.attrib}")
        else:
            self.logger.warning("  playerBank element not found")
        
        # Load prestige points
        try:
            quest_lines1 = self.xml_root.find("questLines")
            if quest_lines1 is not None:
                self.logger.debug(f"  Found questLines (outer)")
                quest_lines2 = quest_lines1.find("questLines")
                if quest_lines2 is not None:
                    self.logger.debug(f"  Found questLines (inner)")
                    exodus_fleet_found = False
                    for elem in quest_lines2.findall("l"):
                        elem_type = elem.get("type")
                        self.logger.debug(f"    Quest line type: {elem_type}")
                        if elem_type == "ExodusFleet":
                            prestige = elem.get("playerPrestigePoints", "0")
                            self.prestige_input.setText(prestige)
                            self.logger.info(f"  Prestige Points: {prestige}")
                            exodus_fleet_found = True
                            break
                    if not exodus_fleet_found:
                        self.logger.warning("  ExodusFleet quest line not found")
                else:
                    self.logger.warning("  Inner questLines element not found")
            else:
                self.logger.warning("  Outer questLines element not found")
        except Exception as e:
            self.logger.error(f"  Error loading prestige points: {str(e)}", exc_info=True)
            self.prestige_input.setText("0")
        
        # Load sandbox mode
        settings_elem = self.xml_root.find("settings")
        if settings_elem is not None:
            self.logger.debug("  Found settings element")
            diff_elem = settings_elem.find("diff")
            if diff_elem is not None:
                sandbox = diff_elem.get("sandbox", "false").lower() == "true"
                self.sandbox_check.setChecked(sandbox)
                self.logger.info(f"  Sandbox Mode: {sandbox}")
                self.logger.debug(f"  diff attributes: {diff_elem.attrib}")
            else:
                self.logger.warning("  diff element not found")
        else:
            self.logger.warning("  settings element not found")
                
    def load_ships(self):
        """Load ships from XML"""
        self.ships.clear()
        
        if self.xml_root is None:
            self.logger.warning("load_ships: xml_root is None")
            return
        
        self.logger.info("Searching for ship elements...")
        ship_elements = self.xml_root.findall(".//ship")
        self.logger.info(f"Found {len(ship_elements)} ship elements")
        
        for idx, ship_elem in enumerate(ship_elements):
            self.logger.info(f"Processing ship {idx + 1}/{len(ship_elements)}")
            self.logger.debug(f"  Ship element attributes: {ship_elem.attrib}")
            
            ship = Ship()
            ship.sid = int(ship_elem.get("sid", "0"))
            ship.sname = ship_elem.get("sname", "Unknown Ship")
            ship.sx = int(ship_elem.get("sx", "0"))
            ship.sy = int(ship_elem.get("sy", "0"))
            
            self.logger.info(f"  Ship ID: {ship.sid}, Name: {ship.sname}, Size: {ship.sx}x{ship.sy}")
            
            # Load storage containers
            self.logger.info(f"  Loading storage for ship {ship.sname}...")
            self.load_ship_storage(ship, ship_elem)
            
            self.ships.append(ship)
            self.logger.info(f"  Ship {ship.sname} loaded with {len(ship.storage_containers)} storage containers")
        
        self.logger.info(f"Total ships loaded: {len(self.ships)}")
            
    def load_ship_storage(self, ship: Ship, ship_elem: ET.Element):
        """Load storage containers and items for a ship"""
        self.logger.debug(f"    Searching for storage containers in ship {ship.sname}")
        
        # Log the structure of the ship element
        self.logger.debug(f"    Ship element has {len(list(ship_elem))} children")
        for child in ship_elem:
            self.logger.debug(f"      Child element: {child.tag} (attributes: {list(child.attrib.keys())})")
        
        # Look for storage-related elements (this is a placeholder - need actual XML structure)
        # Common patterns: "storage", "containers", "items", "inventory"
        storage_found = False
        
        # Try finding storage containers
        for storage_elem in ship_elem.findall(".//storage"):
            storage_found = True
            self.logger.debug(f"    Found storage element with attributes: {storage_elem.attrib}")
            container = StorageContainer()
            container.container_id = int(storage_elem.get("id", "0"))
            container.container_name = storage_elem.get("name", f"Container {container.container_id}")
            
            # Load items in this container
            for item_elem in storage_elem.findall(".//item"):
                item = StorageItem()
                item.item_id = item_elem.get("id", "unknown")
                item.item_name = self.id_collection.get_name(item.item_id)
                item.quantity = int(item_elem.get("quantity", "0"))
                container.items.append(item)
                self.logger.debug(f"      Found item: {item.item_id} x{item.quantity}")
            
            ship.storage_containers.append(container)
            self.logger.info(f"    Loaded container {container.container_name} with {len(container.items)} items")
        
        # Try alternative patterns
        for container_elem in ship_elem.findall(".//container"):
            storage_found = True
            self.logger.debug(f"    Found container element with attributes: {container_elem.attrib}")
            container = StorageContainer()
            container.container_id = int(container_elem.get("id", "0"))
            container.container_name = container_elem.get("name", f"Container {container.container_id}")
            ship.storage_containers.append(container)
        
        if not storage_found:
            self.logger.warning(f"    No storage containers found for ship {ship.sname}")
            self.logger.debug(f"    Available sub-elements: {[child.tag for child in ship_elem.iter()]}")
        
    def load_characters(self):
        """Load characters from XML"""
        self.characters.clear()
        
        if self.xml_root is None:
            self.logger.warning("load_characters: xml_root is None")
            return
        
        self.logger.info("Searching for character elements...")
        char_elements = self.xml_root.findall(".//c")
        self.logger.info(f"Found {len(char_elements)} character elements")
        
        for idx, char_elem in enumerate(char_elements):
            self.logger.info(f"Processing character {idx + 1}/{len(char_elements)}")
            self.logger.debug(f"  Character element attributes: {char_elem.attrib}")
            
            character = Character()
            character.character_entity_id = int(char_elem.get("entId", "0"))
            character.ship_sid = int(char_elem.get("shipSid", "0"))
            
            self.logger.debug(f"  Entity ID: {character.character_entity_id}, Ship SID: {character.ship_sid}")
            
            # Load character name
            pers_elem = char_elem.find("pers")
            if pers_elem is not None:
                first_name = pers_elem.get("fn", "Unknown")
                last_name = pers_elem.get("ln", "")
                character.character_name = f"{first_name} {last_name}".strip()
                self.logger.info(f"  Name: {character.character_name}")
                self.logger.debug(f"  pers element attributes: {pers_elem.attrib}")
                
                # Load attributes
                attr_elem = pers_elem.find("attr")
                if attr_elem is not None:
                    self.logger.debug(f"  Found attr element")
                    attr_count = 0
                    for a_elem in attr_elem.findall("a"):
                        prop = DataProp()
                        prop.id = int(a_elem.get("id", "0"))
                        prop.value = int(a_elem.get("points", "0"))
                        character.character_attributes.append(prop)
                        attr_count += 1
                        self.logger.debug(f"    Attribute {prop.id}: {prop.value} points")
                    self.logger.info(f"  Loaded {attr_count} attributes")
                else:
                    self.logger.warning(f"  attr element not found for {character.character_name}")
                
                # Load skills
                skills_elem = pers_elem.find("skills")
                if skills_elem is not None:
                    self.logger.debug(f"  Found skills element")
                    skill_count = 0
                    for s_elem in skills_elem.findall("s"):
                        prop = DataProp()
                        prop.id = int(s_elem.get("id", "0"))
                        prop.value = int(s_elem.get("level", "0"))
                        prop.max_value = int(s_elem.get("mxn", "0"))
                        character.character_skills.append(prop)
                        skill_count += 1
                        self.logger.debug(f"    Skill {prop.id}: level {prop.value}/{prop.max_value}")
                    self.logger.info(f"  Loaded {skill_count} skills")
                else:
                    self.logger.warning(f"  skills element not found for {character.character_name}")
            else:
                self.logger.warning(f"  pers element not found for character {character.character_entity_id}")
                character.character_name = f"Unknown Character {character.character_entity_id}"
                        
            self.characters.append(character)
            self.logger.info(f"  Character {character.character_name} loaded successfully")
        
        self.logger.info(f"Total characters loaded: {len(self.characters)}")
            
    def update_global_settings(self):
        """Update global settings in memory"""
        if self.xml_root is None:
            QMessageBox.warning(self, "Error", "No save file loaded")
            return
            
        settings_updated = False
        
        try:
            # Update credits
            bank_elem = self.xml_root.find("playerBank")
            if bank_elem is not None:
                new_credits = self.credits_input.text()
                if new_credits != bank_elem.get("ca", ""):
                    bank_elem.set("ca", new_credits)
                    settings_updated = True
            
            # Update prestige points
            try:
                new_prestige = int(self.prestige_input.text())
                quest_lines1 = self.xml_root.find("questLines")
                if quest_lines1 is not None:
                    quest_lines2 = quest_lines1.find("questLines")
                    if quest_lines2 is not None:
                        for elem in quest_lines2.findall("l"):
                            if elem.get("type") == "ExodusFleet":
                                if elem.get("playerPrestigePoints") != str(new_prestige):
                                    elem.set("playerPrestigePoints", str(new_prestige))
                                    settings_updated = True
                                break
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid prestige points value")
                return
            
            # Update sandbox mode
            settings_elem = self.xml_root.find("settings")
            if settings_elem is not None:
                diff_elem = settings_elem.find("diff")
                if diff_elem is not None:
                    new_sandbox = "true" if self.sandbox_check.isChecked() else "false"
                    if diff_elem.get("sandbox") != new_sandbox:
                        diff_elem.set("sandbox", new_sandbox)
                        settings_updated = True
            
            if settings_updated:
                QMessageBox.information(
                    self,
                    "Success",
                    "Global settings updated in memory.\nUse File -> Save to make changes permanent."
                )
            else:
                QMessageBox.information(self, "Info", "No changes detected in global settings")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update settings:\n{str(e)}")
            
    def save_file(self):
        """Save changes to file"""
        if not self.current_file_path or self.xml_tree is None:
            QMessageBox.warning(self, "Error", "No file loaded to save")
            return
            
        try:
            # Write the XML tree to file with pretty printing
            self.xml_tree.write(self.current_file_path, encoding="utf-8", xml_declaration=True)
            QMessageBox.information(self, "Success", "File saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
            
    def on_ship_selected(self, index: int):
        """Handle ship selection change"""
        self.logger.info(f"Ship selection changed to index {index}")
        
        if index < 0:
            self.logger.debug("Invalid index, returning")
            return
            
        ship = self.ship_combo.itemData(index)
        if ship:
            self.logger.info(f"Selected ship: {ship.sname} (ID: {ship.sid})")
            self.ship_width.setValue(ship.sx)
            self.ship_height.setValue(ship.sy)
            self.ship_info.setText(f"Ship: {ship.sname}\nDimensions: {ship.sx}x{ship.sy}")
            
            # Update crew list for this ship
            self.logger.info(f"Updating crew list for ship {ship.sid}")
            self.update_crew_list(ship.sid)
            
            # Update storage containers
            self.logger.info(f"Updating storage containers for ship {ship.sname}")
            self.update_storage_containers(ship)
        else:
            self.logger.warning(f"No ship data for index {index}")
            
    def update_ship_size(self):
        """Update the selected ship's size"""
        current_ship = self.ship_combo.currentData()
        if not current_ship or self.xml_root is None:
            return
            
        new_width = self.ship_width.value()
        new_height = self.ship_height.value()
        
        # Find and update ship in XML
        for ship_elem in self.xml_root.findall(".//ship"):
            if int(ship_elem.get("sid", "0")) == current_ship.sid:
                ship_elem.set("sx", str(new_width))
                ship_elem.set("sy", str(new_height))
                current_ship.sx = new_width
                current_ship.sy = new_height
                QMessageBox.information(
                    self,
                    "Success",
                    f"Ship size updated to {new_width}x{new_height}\nRemember to save!"
                )
                break
                
    def update_crew_list(self, ship_sid: int):
        """Update the crew list for the selected ship"""
        self.logger.info(f"Updating crew list for ship SID {ship_sid}")
        self.crew_list.clear()
        
        crew_count = 0
        for char in self.characters:
            if char.ship_sid == ship_sid:
                self.crew_list.addItem(char.character_name, char)
                crew_count += 1
                self.logger.debug(f"  Added crew: {char.character_name}")
        
        self.logger.info(f"Added {crew_count} crew members to list")
        
        if crew_count == 0:
            self.logger.warning(f"No crew found for ship SID {ship_sid}")
                
    def on_crew_selected(self, index: int):
        """Handle crew member selection"""
        if index < 0:
            return
            
        character = self.crew_list.itemData(index)
        if character:
            self.display_crew_details(character)
            
    def display_crew_details(self, character: Character):
        """Display details for a crew member"""
        self.crew_table.setRowCount(0)
        
        # Display attributes
        for attr in character.character_attributes:
            row = self.crew_table.rowCount()
            self.crew_table.insertRow(row)
            self.crew_table.setItem(row, 0, QTableWidgetItem(f"Attribute {attr.id}"))
            self.crew_table.setItem(row, 1, QTableWidgetItem(str(attr.value)))
            self.crew_table.setItem(row, 2, QTableWidgetItem(str(attr.max_value)))
            
        # Display skills
        for skill in character.character_skills:
            row = self.crew_table.rowCount()
            self.crew_table.insertRow(row)
            self.crew_table.setItem(row, 0, QTableWidgetItem(f"Skill {skill.id}"))
            self.crew_table.setItem(row, 1, QTableWidgetItem(str(skill.value)))
            self.crew_table.setItem(row, 2, QTableWidgetItem(str(skill.max_value)))
            
    def add_crew_member(self):
        """Add a new crew member"""
        QMessageBox.information(
            self,
            "Not Implemented",
            "Adding crew members is not yet implemented in this version"
        )
        
    def update_storage_containers(self, ship: Ship):
        """Update storage container list for the selected ship"""
        self.logger.info(f"Updating storage containers for ship {ship.sname}")
        self.container_combo.clear()
        
        container_count = 0
        for container in ship.storage_containers:
            self.container_combo.addItem(container.container_name, container)
            container_count += 1
            self.logger.debug(f"  Added container: {container.container_name} with {len(container.items)} items")
        
        self.logger.info(f"Added {container_count} storage containers to list")
        
        if container_count == 0:
            self.logger.warning(f"No storage containers found for ship {ship.sname}")
            
    def on_container_selected(self, index: int):
        """Handle storage container selection"""
        if index < 0:
            return
            
        container = self.container_combo.itemData(index)
        if container:
            self.display_storage_items(container)
            
    def display_storage_items(self, container: StorageContainer):
        """Display items in a storage container"""
        self.storage_table.setRowCount(0)
        
        for item in container.items:
            row = self.storage_table.rowCount()
            self.storage_table.insertRow(row)
            self.storage_table.setItem(row, 0, QTableWidgetItem(item.item_id))
            self.storage_table.setItem(row, 1, QTableWidgetItem(item.item_name))
            self.storage_table.setItem(row, 2, QTableWidgetItem(str(item.quantity)))
            
    def add_storage_item(self):
        """Add a new storage item"""
        QMessageBox.information(
            self,
            "Not Implemented",
            "Adding storage items is not yet implemented in this version"
        )
        
    def remove_storage_item(self):
        """Remove a storage item"""
        current_row = self.storage_table.currentRow()
        if current_row >= 0:
            self.storage_table.removeRow(current_row)
            
    def reset_application_state(self):
        """Reset the application to initial state"""
        self.current_file_path = ""
        self.xml_tree = None
        self.xml_root = None
        self.characters.clear()
        self.ships.clear()
        
        self.credits_input.setText("")
        self.prestige_input.setText("")
        self.sandbox_check.setChecked(False)
        self.ship_combo.clear()
        self.crew_list.clear()
        self.crew_table.setRowCount(0)
        self.container_combo.clear()
        self.storage_table.setRowCount(0)
        
        self.setWindowTitle("Space Haven Save Editor - Python Edition")
        
    def show_settings(self):
        """Show settings dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Settings")
        msg.setText("Backup on Open:")
        msg.setCheckBox(QCheckBox("Create backup when opening save files"))
        msg.checkBox().setChecked(self.backup_enabled)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        
        if msg.exec() == QMessageBox.StandardButton.Ok:
            self.backup_enabled = msg.checkBox().isChecked()
            self.settings.setValue("backup_on_open", self.backup_enabled)
            QMessageBox.information(
                self,
                "Settings Updated",
                f"Backup on open: {'Enabled' if self.backup_enabled else 'Disabled'}"
            )
            
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Space Haven Save Editor",
            "<h3>Space Haven Save Editor - Python Edition</h3>"
            "<p>A cross-platform save editor for Space Haven</p>"
            "<p>Original VB.NET version by <a href='https://github.com/moragar360'>Moragar</a></p>"
            "<p>Python port for Steam Deck compatibility</p>"
            "<p>Supports Space Haven Alpha 20</p>"
            "<p>License: MIT</p>"
        )
        
    def closeEvent(self, event):
        """Handle application close"""
        self.settings.setValue("backup_on_open", self.backup_enabled)
        event.accept()


def main():
    """Main entry point"""
    # Setup logging first
    logger = setup_logging()
    logger.info("Starting Space Haven Save Editor")
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Space Haven Save Editor")
        app.setOrganizationName("SpaceHavenEditor")
        
        logger.info("Creating main window")
        window = SpaceHavenEditor()
        window.show()
        
        logger.info("Application ready, entering event loop")
        exit_code = app.exec()
        logger.info(f"Application exiting with code {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
