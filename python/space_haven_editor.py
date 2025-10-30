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


from version_analyzer import SaveFileVersionAnalyzer, SaveFileInfo

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
        self.load_default_ids()

    def load_default_ids(self):
        """Load default game IDs - based on Space Haven Alpha 20"""

        self.attributes = {
            210: "Bravery",
            212: "Zest",
            213: "Intelligence",
            214: "Perception"
        }

        self.skills = {
            1: "Piloting",
            2: "Mining",
            3: "Botany",
            4: "Construct",
            5: "Industry",
            6: "Medical",
            7: "Gunner",
            8: "Shielding",
            9: "Operations",
            10: "Weapons",
            12: "Logistics",
            13: "Maintenance",
            14: "Navigation",
            16: "Research"
        }

        self.traits = {
            191: "Hero",
            655: "Wimp",
            656: "Clumsy",
            1034: "Suicidal",
            1035: "Smart",
            1036: "Bloodlust",
            1037: "Antisocial",
            1038: "Needy",
            1039: "Fast Learner",
            1040: "Lazy",
            1041: "Hard Working",
            1042: "Psychopath",
            1043: "Peace-loving",
            1044: "Iron-willed",
            1045: "Spacefarer",
            1046: "Confident",
            1047: "Neurotic",
            1048: "Charming",
            1533: "Iron Stomach",
            1534: "Nyctophilia",
            1535: "Minimalist",
            1560: "Talkative",
            1562: "Gourmand",
            2082: "Alien lover"
        }

        self.conditions = {
            193: "Panicked",
            194: "Scared",
            713: "Frostbite",
            714: "First-degree burn",
            715: "Wound",
            751: "Blast injury",
            1003: "Crawler bite",
            1033: "Ate without table",
            1053: "Feeling a little hungry",
            1058: "Feeling a little unsafe",
            1059: "Slept on the floor",
            1060: "Holding it in",
            1061: "It's so dark on this spaceship",
            1062: "Ate the meat of a human being",
            1063: "Wearing spacesuit",
            1064: "Feeling adventurous",
            1065: "Feeling meaningful",
            1066: "Feeling loved",
            # Add more as needed
        }

        # Complete storage items list from VB.NET IdCollection
        self.storage_items = {
            15: "Root vegetables",
            16: "Water",
            40: "Ice",
            71: "Bio Matter",
            127: "Rubble",
            157: "Base Metals",
            158: "Energium",
            162: "Infrablock",
            169: "Noble Metals",
            170: "Carbon",
            171: "Raw Chemicals",
            172: "Hyperium",
            173: "Electronic Component",
            174: "Energy Rod",
            175: "Plastics",
            176: "Chemicals",
            177: "Fabrics",
            178: "Hyperfuel",
            179: "Processed Food",
            706: "Fruits",
            707: "Artificial Meat",
            712: "Space Food",
            725: "Assault Rifle",
            728: "SMG",
            729: "Shotgun",
            760: "Five-Seven Pistol",
            930: "Techblock",
            984: "Monster Meat",
            985: "Human Meat",
            1152: "Sentry Gun X1",
            1759: "Hull Block",
            1873: "Infra Scrap",
            1874: "Soft Scrap",
            1886: "Hull Scrap",
            1919: "Energy Block",
            1920: "Superblock",
            1921: "Soft Block",
            1922: "Steel Plates",
            1924: "Optronics Component",
            1925: "Quantronics Component",
            1926: "Energy Cell",
            1932: "Fibers",
            1946: "Tech Scrap",
            1947: "Energy Scrap",
            1954: "Human Corpse",
            1955: "Monster Corpse",
            2053: "Medical Supplies",
            2058: "IV Fluid",
            2475: "Fertilizer",
            2657: "Nuts and Seeds",
            2715: "Explosive Ammunition",
            3069: "Laser Rifle",
            3070: "Laser Pistol",
            3071: "Plasma Cuttergun",
            3072: "Plasma Rifle",
            3378: "Grain and Hops",
            3384: "Armored Vest",
            3386: "Remote Control",
            3388: "Oxygen Tank",
            3419: "Augmentation Parts",
            3960: "Flamethrower (Weapon Attachment)",
            3961: "Stun Rifle",
            3962: "Stun Pistol",
            3967: "Explosive Grenade Launcher (Weapon Attachment)",
            3968: "Basic Scope (Weapon Attachment)",
            3969: "Tactical Grip (Weapon Attachment)",
            4005: "Painkillers",
            4006: "Combat Stimulant",
            4007: "Bandage",
            4030: "Nano Wound Dressing",
            4040: "Small Breach Charge",
            4065: "Space Suit Oxygen Extender",
            4076: "Incendiary Grenade Launcher (Weapon Attachment)",
        }

    def get_attribute_name(self, attr_id: int) -> str:
        return self.attributes.get(attr_id, f"Attribute {attr_id}")

    def get_skill_name(self, skill_id: int) -> str:
        return self.skills.get(skill_id, f"Skill {skill_id}")

    def get_trait_name(self, trait_id: int) -> str:
        return self.traits.get(trait_id, f"Trait {trait_id}")

    def get_condition_name(self, condition_id: int) -> str:
        return self.conditions.get(condition_id, f"Condition {condition_id}")

    def get_storage_item_name(self, item_id: int) -> str:
        return self.storage_items.get(item_id, f"Item {item_id}")


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
        self.current_folder_path: Optional[Path] = None  # NEW: Track folder
        self.xml_tree: Optional[ET.ElementTree] = None
        self.xml_root: Optional[ET.Element] = None
        self.characters: List[Character] = []
        self.ships: List[Ship] = []
        self.id_collection = IdCollection()

        # Version analyzer
        self.version_analyzer = SaveFileVersionAnalyzer(self.logger)
        self.current_save_info: Optional[SaveFileInfo] = None

        # Settings (legacy)
        self.settings = QSettings("SpaceHavenEditor", "SaveEditor")
        self.backup_enabled = self.settings.value("backup_on_open", True, type=bool)
        
        # NEW: Save folder and backup management
        from save_manager import SaveFolderConfig, BackupManager, SaveFolderInfo
        from pathlib import Path
        self.save_config = SaveFolderConfig()
        self.backup_manager = BackupManager(
            Path(self.save_config.config["backup_folder"]),
            max_days=self.save_config.config["backup_count"]
        )

        self.logger.info(f"Backup on open: {self.backup_enabled}")
        self.logger.info(f"Steam folder enabled: {self.save_config.config['use_steam_folder']}")

        # Setup UI
        self.init_ui()

        # Show first-run setup if needed
        if self.save_config.is_first_run:
            self.show_first_run_setup()

        self.logger.info("SpaceHavenEditor initialization complete")

        # Storage editing state
        self.current_storage_container: Optional[StorageContainer] = None
        
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
        from PyQt6.QtWidgets import QFrame
        
        group = QGroupBox("Global Settings")
        layout = QHBoxLayout()

        # Version info
        layout.addWidget(QLabel("Version:"))
        self.version_label = QLabel("Unknown")
        self.version_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        self.version_label.setMinimumWidth(100)
        layout.addWidget(self.version_label)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

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
        from PyQt6.QtWidgets import QListWidget, QSplitter, QScrollArea
        from PyQt6.QtCore import Qt

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create a horizontal splitter for crew list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Crew list
        crew_list_widget = QWidget()
        crew_list_layout = QVBoxLayout(crew_list_widget)

        crew_list_layout.addWidget(QLabel("Crew Members:"))

        self.crew_list = QListWidget()
        self.crew_list.currentRowChanged.connect(self.on_crew_selected)
        crew_list_layout.addWidget(self.crew_list)

        add_crew_btn = QPushButton("Add Crew Member")
        add_crew_btn.clicked.connect(self.add_crew_member)
        crew_list_layout.addWidget(add_crew_btn)

        splitter.addWidget(crew_list_widget)

        # Right side: Crew details in scrollable area
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(10)

        # Header with crew name editor
        header_layout = QHBoxLayout()

        name_label = QLabel("Name:")
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(name_label)

        self.crew_name_edit = QLineEdit()
        self.crew_name_edit.setPlaceholderText("Select a crew member")
        self.crew_name_edit.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.crew_name_edit.setMaximumWidth(300)
        self.crew_name_edit.setReadOnly(True)  # Start as read-only until crew selected
        self.crew_name_edit.textChanged.connect(self.on_crew_name_changed)
        header_layout.addWidget(self.crew_name_edit)

        header_layout.addStretch()
        details_layout.addLayout(header_layout)

        # Attributes section
        attr_header_layout = QHBoxLayout()
        attr_label = QLabel("Attributes")
        attr_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0066cc;")
        attr_header_layout.addWidget(attr_label)
        attr_header_layout.addStretch()

        self.max_all_attr_btn = QPushButton("\u2308 Max All Attributes")
        self.max_all_attr_btn.clicked.connect(self.max_all_attributes)
        attr_header_layout.addWidget(self.max_all_attr_btn)

        details_layout.addLayout(attr_header_layout)

        self.attributes_container = QWidget()
        self.attributes_layout = QVBoxLayout(self.attributes_container)
        self.attributes_layout.setSpacing(2)
        self.attributes_layout.setContentsMargins(10, 0, 0, 0)
        details_layout.addWidget(self.attributes_container)

        # Skills section
        skills_header_layout = QHBoxLayout()
        skills_label = QLabel("Skills")
        skills_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0066cc;")
        skills_header_layout.addWidget(skills_label)
        skills_header_layout.addStretch()

        # Note: Only "Max All Skills" button - learning values are calculated, not editable
        self.max_all_skills_btn = QPushButton("\u2308 Max All Skills to Learning")
        self.max_all_skills_btn.setToolTip("Set all skills to their maximum learning potential")
        self.max_all_skills_btn.clicked.connect(self.max_all_skills_to_learning)
        skills_header_layout.addWidget(self.max_all_skills_btn)

        details_layout.addLayout(skills_header_layout)

        self.skills_container = QWidget()
        self.skills_layout = QVBoxLayout(self.skills_container)
        self.skills_layout.setSpacing(2)
        self.skills_layout.setContentsMargins(10, 0, 0, 0)
        details_layout.addWidget(self.skills_container)

        # Traits section
        traits_label = QLabel("Traits")
        traits_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0066cc;")
        details_layout.addWidget(traits_label)

        self.traits_container = QWidget()
        self.traits_layout = QVBoxLayout(self.traits_container)
        self.traits_layout.setSpacing(2)
        self.traits_layout.setContentsMargins(10, 0, 0, 0)
        details_layout.addWidget(self.traits_container)

        # Conditions section
        conditions_label = QLabel("Conditions")
        conditions_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0066cc;")
        details_layout.addWidget(conditions_label)

        self.conditions_container = QWidget()
        self.conditions_layout = QVBoxLayout(self.conditions_container)
        self.conditions_layout.setSpacing(2)
        self.conditions_layout.setContentsMargins(10, 0, 0, 0)
        details_layout.addWidget(self.conditions_container)

        details_layout.addStretch()

        # Wrap details in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(details_widget)
        scroll_area.setWidgetResizable(True)
        splitter.addWidget(scroll_area)

        # Set splitter proportions (30% list, 70% details)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

        # Store reference to current character
        self.current_character: Optional[Character] = None
        self.attribute_editors = {}
        self.skill_editors = {}

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

        # Storage info label
        self.storage_info_label = QLabel("")
        self.storage_info_label.setStyleSheet("font-size: 11px;")
        container_layout.addWidget(self.storage_info_label)

        container_layout.addStretch()
        layout.addLayout(container_layout)

        # Storage items table
        self.storage_table = QTableWidget()
        self.storage_table.setColumnCount(4)
        self.storage_table.setHorizontalHeaderLabels(["Item ID", "Item Name", "Quantity", "Actions"])
        self.storage_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.storage_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.storage_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.storage_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.storage_table.itemChanged.connect(self.on_storage_item_changed)
        layout.addWidget(self.storage_table)

        # Add items section
        add_group = QGroupBox("Add Items")
        add_layout = QVBoxLayout(add_group)

        # Resupply presets
        resupply_layout = QHBoxLayout()
        resupply_layout.addWidget(QLabel("Resupply Presets:"))
        
        infra_1_btn = QPushButton("Infra +1")
        infra_1_btn.setToolTip("Add 1 of each: Infrablock, Soft Block, Techblock, Energy Block, Hull Block, Superblock")
        infra_1_btn.clicked.connect(lambda: self.resupply_preset("infra", 1))
        resupply_layout.addWidget(infra_1_btn)
        
        infra_5_btn = QPushButton("Infra +5")
        infra_5_btn.setToolTip("Add 5 of each: Infrablock, Soft Block, Techblock, Energy Block, Hull Block, Superblock")
        infra_5_btn.clicked.connect(lambda: self.resupply_preset("infra", 5))
        resupply_layout.addWidget(infra_5_btn)
        
        infra_10_btn = QPushButton("Infra +10")
        infra_10_btn.setToolTip("Add 10 of each: Infrablock, Soft Block, Techblock, Energy Block, Hull Block, Superblock")
        infra_10_btn.clicked.connect(lambda: self.resupply_preset("infra", 10))
        resupply_layout.addWidget(infra_10_btn)
        
        life_5_btn = QPushButton("Life Support +5")
        life_5_btn.setToolTip("Add 5 of each: Water, Ice, Root vegetables, Fruits, Artificial Meat, Nuts and Seeds")
        life_5_btn.clicked.connect(lambda: self.resupply_preset("life_support", 5))
        resupply_layout.addWidget(life_5_btn)
        
        life_10_btn = QPushButton("Life Support +10")
        life_10_btn.setToolTip("Add 10 of each: Water, Ice, Root vegetables, Fruits, Artificial Meat, Nuts and Seeds")
        life_10_btn.clicked.connect(lambda: self.resupply_preset("life_support", 10))
        resupply_layout.addWidget(life_10_btn)
        
        # TODO: Add Ship preset when we find Energium/Hyperium IDs
        # ship_btn = QPushButton("Ship")
        # ship_btn.setToolTip("Add Energium and Hyperium")
        # ship_btn.clicked.connect(lambda: self.resupply_preset("ship", 5))
        # resupply_layout.addWidget(ship_btn)
        
        resupply_layout.addStretch()
        add_layout.addLayout(resupply_layout)

        # Item selector
        item_select_layout = QHBoxLayout()
        item_select_layout.addWidget(QLabel("Individual Item:"))
        self.add_item_combo = QComboBox()
        self.populate_add_item_combo()
        item_select_layout.addWidget(self.add_item_combo, 1)
        add_layout.addLayout(item_select_layout)

        # Quick add buttons
        quick_add_layout = QHBoxLayout()
        quick_add_layout.addWidget(QLabel("Quick Add:"))

        add_1_btn = QPushButton("+1")
        add_1_btn.clicked.connect(lambda: self.quick_add_item(1))
        quick_add_layout.addWidget(add_1_btn)

        add_5_btn = QPushButton("+5")
        add_5_btn.clicked.connect(lambda: self.quick_add_item(5))
        quick_add_layout.addWidget(add_5_btn)

        add_10_btn = QPushButton("+10")
        add_10_btn.clicked.connect(lambda: self.quick_add_item(10))
        quick_add_layout.addWidget(add_10_btn)

        quick_add_layout.addStretch()
        add_layout.addLayout(quick_add_layout)

        layout.addWidget(add_group)

        return widget
        
    def open_file(self):
        """Open a save folder"""
        from save_manager import SaveFolderInfo
        from pathlib import Path
        
        self.logger.info("Opening folder dialog")
        
        # Determine initial directory
        initial_dir = self.save_config.get_default_folder()
        if not initial_dir or not initial_dir.exists():
            initial_dir = Path.home()
        
        self.logger.info(f"Initial directory: {initial_dir}")
        
        # Open folder dialog
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Space Haven Save Folder",
            str(initial_dir),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not folder_path:
            self.logger.info("Folder dialog cancelled by user")
            return
        
        folder_path = Path(folder_path)
        self.logger.info(f"Selected folder: {folder_path}")
        
        # Parse folder info
        folder_info = SaveFolderInfo(folder_path)
        
        if not folder_info.is_valid_save():
            QMessageBox.critical(
                self,
                "Invalid Save Folder",
                f"The selected folder does not contain a valid Space Haven save.\n\n"
                f"Expected files:\n"
                f"  save/game - {'Found' if folder_info.game_file_exists else 'Missing'}\n"
                f"  save/info - {'Found' if folder_info.info_file_exists else 'Missing'}"
            )
            return
        
        # Remember this folder
        self.save_config.set_last_used_folder(str(folder_path))
        
        # Handle backup based on mode
        backup_mode = self.save_config.config.get("auto_backup", False)
        
        if backup_mode == "auto":
            # Automatic backup
            self.logger.info("Creating automatic backup...")
            backup_path = self.backup_manager.create_backup(folder_path)
            if backup_path:
                self.logger.info(f"Backup created: {backup_path.name}")
                
                # Check if we should prune old backups
                dates = self.backup_manager.get_backup_dates()
                max_days = self.save_config.config.get("backup_count", 3)
                
                if len(dates) > max_days:
                    # Ask about pruning
                    to_delete = self.backup_manager.prune_old_backups(max_days, dry_run=True)
                    total_size = sum(p.stat().st_size for p in to_delete)
                    size_mb = total_size / (1024 * 1024)
                    
                    reply = QMessageBox.question(
                        self,
                        "Prune Old Backups?",
                        f"You have backups from {len(dates)} days.\n"
                        f"Delete {len(to_delete)} old backups ({size_mb:.1f} MB)?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        deleted = self.backup_manager.prune_old_backups(max_days)
                        self.logger.info(f"Pruned {len(deleted)} old backups")
            else:
                self.logger.warning("Backup creation failed")
                
        elif backup_mode == "manual":
            # Ask user
            reply = QMessageBox.question(
                self,
                "Create Backup?",
                f"Create a backup of this save before opening?\n\n"
                f"Save: {folder_info.get_display_name()}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Check if backup exists today
                from datetime import datetime
                today = datetime.now().strftime("%Y%m%d")
                existing = self.backup_manager._find_backups_for_date(today)
                
                force_new = False
                if existing:
                    reply2 = QMessageBox.question(
                        self,
                        "Backup Exists",
                        f"A backup already exists for today:\n{existing[0].name}\n\n"
                        f"Create another backup?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    force_new = (reply2 == QMessageBox.StandardButton.Yes)
                    if not force_new:
                        self.logger.info("Using existing backup")
                
                if force_new or not existing:
                    backup_path = self.backup_manager.create_backup(folder_path, force_new=force_new)
                    if backup_path:
                        self.logger.info(f"Manual backup created: {backup_path.name}")
        
        # Reset application state
        self.logger.info("Resetting application state")
        self.reset_application_state()
        
        # Load the folder
        try:
            self.current_folder_path = folder_path
            game_file = folder_path / "save" / "game"
            self.current_file_path = str(game_file)
            
            self.logger.info(f"Loading save from folder: {folder_path}")
            self.logger.info(f"Version: {folder_info.version}")
            
            self.load_save_file(str(game_file))
            self.current_save_info = folder_info  # Store folder info
            
            # Update version display
            if folder_info.version:
                self.version_label.setText(folder_info.version)
            
            self.setWindowTitle(f"Space Haven Save Editor - {folder_path.name} (v{folder_info.version})")
            self.logger.info("Save loaded successfully")
            QMessageBox.information(
                self,
                "Success",
                f"Save loaded successfully!\n\nVersion: {folder_info.version or 'Unknown'}"
            )
        except Exception as e:
            self.logger.error(f"Failed to load save: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load save:\n{str(e)}")
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

        # Analyze version information
        self.logger.info("Analyzing save file version...")
        try:
            self.current_save_info = self.version_analyzer.analyze_save_file(Path(file_path))
            version_str = self.current_save_info.version or "Unknown"
            self.version_label.setText(version_str)
            self.logger.info(f"Detected version: {version_str}")

            # Log additional info
            if self.current_save_info.id_counter:
                self.logger.info(f"  ID Counter: {self.current_save_info.id_counter}")
            if self.current_save_info.sector_count:
                self.logger.info(f"  Sector Count: {self.current_save_info.sector_count}")
        except Exception as e:
            self.logger.warning(f"Version analysis failed: {e}")
            self.version_label.setText("Unknown")

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
        """Load storage containers and items for a ship

        Storage containers are <feat> elements with an eatAllowed attribute,
        containing an <inv> element with <s> items inside.
        
        Storage size detection:
        - fi="20" → Medical Cabinet (capacity ~50)
        - Parent <l> with ind="0" → Small Storage (capacity 50)
        - Parent <l> with ind="3" → Large Storage (capacity 250)
        - Other → Default to Large Storage (250)
        """
        self.logger.debug(f"    Searching for storage containers (feat with eatAllowed) in ship {ship.sname}")

        # Find all <feat> elements with eatAllowed attribute
        feat_elements = ship_elem.findall(".//feat[@eatAllowed]")
        self.logger.debug(f"    Found {len(feat_elements)} feat elements with eatAllowed")

        container_index = 0
        for feat_elem in feat_elements:
            # Check if this feat has an inv element
            inv_elem = feat_elem.find("inv")
            if inv_elem is None:
                continue

            # Create storage container
            container = StorageContainer()
            container.container_id = container_index

            # Detect storage type from fi attribute and parent ind
            fi_attr = feat_elem.get("fi", "")
            eat_allowed = feat_elem.get("eatAllowed", "0")
            
            # Find parent element to check ind attribute
            parent_elem = None
            parent_ind = None
            for elem in ship_elem.iter():
                if feat_elem in list(elem):
                    parent_elem = elem
                    parent_ind = elem.get("ind", "")
                    break
            
            # Determine storage type and capacity
            if fi_attr == "20":
                # Medical cabinet
                storage_type = "Medical Cabinet"
                container.capacity = 50
            elif parent_ind == "0":
                # Small storage
                storage_type = "Small Storage"
                container.capacity = 50
            elif parent_ind == "3":
                # Large storage
                storage_type = "Large Storage"
                container.capacity = 250
            else:
                # Default to large storage
                storage_type = "Storage"
                container.capacity = 250
            
            # Generate descriptive name
            container.container_name = f"{storage_type} {container_index + 1}"

            self.logger.debug(f"    Processing {container.container_name} (fi={fi_attr}, ind={parent_ind}, capacity={container.capacity})")

            # Load items from <inv> -> <s> elements
            item_count = 0
            for item_elem in inv_elem.findall("s"):
                try:
                    item_id = int(item_elem.get("elementaryId", "0"))
                    quantity = int(item_elem.get("inStorage", "0"))

                    if item_id > 0 and quantity > 0:
                        item = StorageItem()
                        item.item_id = str(item_id)
                        item.item_name = self.id_collection.get_storage_item_name(item_id)
                        item.quantity = quantity
                        container.items.append(item)
                        item_count += 1
                        self.logger.debug(f"      Item: {item.item_name} (ID {item_id}) x{quantity}")
                except (ValueError, AttributeError) as e:
                    self.logger.warning(f"      Failed to parse item: {e}")
                    continue

            if item_count > 0 or True:  # Always add container even if empty
                ship.storage_containers.append(container)
                self.logger.info(f"    Loaded {container.container_name} with {item_count} items (capacity: {container.capacity})")
                container_index += 1

        if container_index == 0:
            self.logger.warning(f"    No storage containers found for ship {ship.sname}")
        
    def load_characters(self):
        """Load characters from XML"""
        self.characters.clear()

        if self.xml_root is None:
            self.logger.warning("load_characters: xml_root is None")
            return

        self.logger.info("Loading characters from ships...")

        # Find all ships
        ships_elem = self.xml_root.find("ships")
        if ships_elem is None:
            self.logger.warning("No ships element found in XML")
            return

        ship_list = list(ships_elem.findall("ship"))
        self.logger.info(f"Found {len(ship_list)} ships to check for characters")

        total_characters = 0
        for ship_elem in ship_list:
            ship_sid = int(ship_elem.get("sid", "0"))
            ship_name = ship_elem.get("sname", "Unknown Ship")
            self.logger.info(f"Checking ship: {ship_name} (SID: {ship_sid})")

            # Find characters element in this ship
            characters_elem = ship_elem.find("characters")
            if characters_elem is None:
                self.logger.debug(f"  No characters element in ship {ship_name}")
                continue

            char_elements = characters_elem.findall("c")
            self.logger.info(f"  Found {len(char_elements)} characters in ship {ship_name}")

            for idx, char_elem in enumerate(char_elements):
                self.logger.debug(f"  Processing character {idx + 1}/{len(char_elements)}")

                character = Character()

                # Get basic attributes from <c> element
                character.character_name = char_elem.get("name", "Unknown")
                character.character_entity_id = int(char_elem.get("entId", "0"))
                character.ship_sid = ship_sid  # From parent ship

                self.logger.info(f"    Loaded: {character.character_name} (Entity ID: {character.character_entity_id})")

                # Load personality data from <pers> element
                pers_elem = char_elem.find("pers")
                if pers_elem is not None:
                    self.logger.debug(f"    Found <pers> element")

                    # Load attributes from <pers>/<attr>
                    attr_elem = pers_elem.find("attr")
                    if attr_elem is not None:
                        attr_count = 0
                        for a_elem in attr_elem.findall("a"):
                            prop = DataProp()
                            prop.id = int(a_elem.get("id", "0"))
                            prop.value = int(a_elem.get("points", "0"))
                            # Get human-readable name
                            prop.name = self.id_collection.get_attribute_name(prop.id)
                            character.character_attributes.append(prop)
                            attr_count += 1
                            self.logger.debug(f"      Attribute: {prop.name} ({prop.id}) = {prop.value}")
                        self.logger.info(f"    Loaded {attr_count} attributes")

                    # Load skills from <pers>/<skills>
                    skills_elem = pers_elem.find("skills")
                    if skills_elem is not None:
                        skill_count = 0
                        for s_elem in skills_elem.findall("s"):
                            prop = DataProp()
                            # Note: skills use 'sk' attribute, not 'id'!
                            prop.id = int(s_elem.get("sk", "0"))
                            prop.value = int(s_elem.get("level", "0"))
                            prop.max_value = int(s_elem.get("mxn", "0"))
                            # Get human-readable name
                            prop.name = self.id_collection.get_skill_name(prop.id)
                            character.character_skills.append(prop)
                            skill_count += 1
                            self.logger.debug(f"      Skill: {prop.name} ({prop.id}) = {prop.value}/{prop.max_value}")
                        self.logger.info(f"    Loaded {skill_count} skills")

                    # Load traits from <pers>/<traits>
                    traits_elem = pers_elem.find("traits")
                    if traits_elem is not None:
                        trait_count = 0
                        for t_elem in traits_elem.findall("t"):
                            prop = DataProp()
                            prop.id = int(t_elem.get("id", "0"))
                            # Get human-readable name
                            prop.name = self.id_collection.get_trait_name(prop.id)
                            character.character_traits.append(prop)
                            trait_count += 1
                            self.logger.debug(f"      Trait: {prop.name} ({prop.id})")
                        self.logger.info(f"    Loaded {trait_count} traits")

                    # Load conditions from <pers>/<conditions>
                    conditions_elem = pers_elem.find("conditions")
                    if conditions_elem is not None:
                        condition_count = 0
                        for cond_elem in conditions_elem.findall("c"):
                            prop = DataProp()
                            prop.id = int(cond_elem.get("id", "0"))
                            # Get human-readable name
                            prop.name = self.id_collection.get_condition_name(prop.id)
                            character.character_conditions.append(prop)
                            condition_count += 1
                            self.logger.debug(f"      Condition: {prop.name} ({prop.id})")
                        self.logger.info(f"    Loaded {condition_count} conditions")
                else:
                    self.logger.warning(f"    No <pers> element found for {character.character_name}")

                self.characters.append(character)
                total_characters += 1

        self.logger.info(f"Total characters loaded: {total_characters}")
            
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
        """Save changes to file (preserving XML formatting)"""
        if not self.current_file_path or self.xml_tree is None:
            QMessageBox.warning(self, "Error", "No file loaded to save")
            return

        try:
            # Update XML with any character changes (in-place)
            self.update_characters_to_xml()

            # Update XML with any storage changes
            self.update_storage_to_xml()

            # Write the XML tree to file
            # Note: We update values in-place, so tree.write() should preserve structure
            # Use method='xml' to avoid reformatting, but ElementTree may still change whitespace
            self.logger.info("Writing modified XML to file...")

            # Convert to string to preserve formatting better
            from xml.etree.ElementTree import tostring
            xml_bytes = tostring(self.xml_root, encoding='utf-8')

            # Write directly to avoid ET.write() reformatting
            with open(self.current_file_path, 'wb') as f:
                # Write XML declaration
                f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
                # Write the XML content
                f.write(xml_bytes)

            self.logger.info("XML written successfully")

            # Update info file's realTimeDate (timestamp of last modification)
            if self.current_folder_path:
                info_file = self.current_folder_path / "save" / "info"
                if info_file.exists():
                    try:
                        import time
                        tree = ET.parse(info_file)
                        root = tree.getroot()
                        # Update real time date to current timestamp (milliseconds)
                        current_time_ms = int(time.time() * 1000)
                        root.set("realTimeDate", str(current_time_ms))

                        # Write info file the same way
                        info_bytes = tostring(root, encoding='utf-8')
                        with open(info_file, 'wb') as f:
                            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
                            f.write(info_bytes)

                        self.logger.info(f"Updated info file timestamp: {current_time_ms}")
                    except Exception as e:
                        self.logger.warning(f"Failed to update info file: {e}")

            # Remove [Modified] from title
            title = self.windowTitle().replace(" [Modified]", "")
            self.setWindowTitle(title)

            self.logger.info(f"File saved successfully: {self.current_file_path}")
            QMessageBox.information(self, "Success", "File saved successfully!")
        except Exception as e:
            self.logger.error(f"Failed to save file: {e}", exc_info=True)
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
                from PyQt6.QtWidgets import QListWidgetItem
                item = QListWidgetItem(char.character_name)
                item.setData(256, char)  # Store character object as item data (Qt.UserRole = 256)
                self.crew_list.addItem(item)
                crew_count += 1
                self.logger.debug(f"  Added crew: {char.character_name}")

        self.logger.info(f"Added {crew_count} crew members to list")

        if crew_count == 0:
            self.logger.warning(f"No crew found for ship SID {ship_sid}")
        elif crew_count > 0:
            # Select the first crew member
            self.crew_list.setCurrentRow(0)
                
    def on_crew_selected(self, row: int):
        """Handle crew member selection"""
        self.logger.info(f"Crew selection changed to row {row}")

        if row < 0:
            self.logger.debug("Invalid row, clearing crew details")
            # Clear crew details display
            self.crew_name_edit.clear()
            self.crew_name_edit.setPlaceholderText("Select a crew member")
            self.crew_name_edit.setReadOnly(True)
            self.clear_editor_layout(self.attributes_layout)
            self.clear_editor_layout(self.skills_layout)
            self.clear_editor_layout(self.traits_layout)
            self.clear_editor_layout(self.conditions_layout)
            self.current_character = None
            return

        item = self.crew_list.item(row)
        if item:
            character = item.data(256)  # Qt.UserRole = 256
            if character:
                self.logger.info(f"Selected crew: {character.character_name}")
                self.display_crew_details(character)
            else:
                self.logger.warning(f"No character data for row {row}")
        else:
            self.logger.warning(f"No item at row {row}")
            
    def display_crew_details(self, character: Character):
        """Display details for a crew member with interactive editors"""
        from crew_editors import NumericValueEditor, SkillEditor, TraitWidget, ConditionWidget

        self.logger.info(f"Displaying editable details for {character.character_name}")

        # Store current character
        self.current_character = character

        # Update header - temporarily disconnect signal to avoid triggering change
        self.crew_name_edit.textChanged.disconnect(self.on_crew_name_changed)
        self.crew_name_edit.setText(character.character_name)
        self.crew_name_edit.setReadOnly(False)  # Enable editing
        self.crew_name_edit.textChanged.connect(self.on_crew_name_changed)

        # Clear existing editors
        self.clear_editor_layout(self.attributes_layout)
        self.clear_editor_layout(self.skills_layout)
        self.clear_editor_layout(self.traits_layout)
        self.clear_editor_layout(self.conditions_layout)

        self.attribute_editors.clear()
        self.skill_editors.clear()

        # Add attribute editors
        self.logger.debug(f"  Creating {len(character.character_attributes)} attribute editors")
        for attr in character.character_attributes:
            # Attributes range from 1-5 in Space Haven
            editor = NumericValueEditor(
                item_id=attr.id,
                name=attr.name,
                current_value=attr.value,
                min_value=1,
                max_value=5
            )
            editor.valueChanged.connect(self.on_attribute_changed)
            self.attributes_layout.addWidget(editor)
            self.attribute_editors[attr.id] = editor

        # Add skill editors with visual bars
        self.logger.debug(f"  Creating {len(character.character_skills)} skill editors")
        for skill in character.character_skills:
            editor = SkillEditor(
                skill_id=skill.id,
                name=skill.name,
                current_level=skill.value,
                max_learning=skill.max_value if skill.max_value > 0 else 10
            )
            editor.valueChanged.connect(self.on_skill_changed)
            self.skills_layout.addWidget(editor)
            self.skill_editors[skill.id] = editor

        # Add trait widgets
        self.logger.debug(f"  Creating {len(character.character_traits)} trait widgets")
        for trait in character.character_traits:
            widget = TraitWidget(trait.id, trait.name)
            widget.traitRemoved.connect(self.on_trait_removed)
            self.traits_layout.addWidget(widget)

        # Add condition widgets
        self.logger.debug(f"  Creating {len(character.character_conditions)} condition widgets")
        for condition in character.character_conditions:
            widget = ConditionWidget(condition.id, condition.name)
            widget.conditionRemoved.connect(self.on_condition_removed)
            self.conditions_layout.addWidget(widget)

        self.logger.info(f"Crew details displayed with interactive editors")

    def clear_editor_layout(self, layout: QVBoxLayout):
        """Clear all widgets from a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def on_crew_name_changed(self, new_name: str):
        """Handle crew name change"""
        if self.current_character and new_name:
            self.current_character.character_name = new_name
            self.logger.info(f"Character name changed to: {new_name}")
            # Update the crew list item text
            for row in range(self.crew_list.count()):
                item = self.crew_list.item(row)
                if item.data(256) == self.current_character:
                    item.setText(new_name)
                    break
            # Mark as modified
            self.mark_as_modified()

    def on_attribute_changed(self, attr_id: int, new_value: int):
        """Handle attribute value change"""
        if self.current_character:
            for attr in self.current_character.character_attributes:
                if attr.id == attr_id:
                    attr.value = new_value
                    self.logger.info(f"Attribute {attr.name} changed to {new_value}")
                    # Mark as modified
                    self.mark_as_modified()
                    break

    def on_skill_changed(self, skill_id: int, current_level: int, max_learning: int):
        """Handle skill value change - updates both current level and max learning"""
        if self.current_character:
            for skill in self.current_character.character_skills:
                if skill.id == skill_id:
                    skill.value = current_level
                    skill.max_value = max_learning
                    self.logger.info(f"Skill {skill.name} changed to level={current_level}, learning={max_learning}")
                    # Mark as modified
                    self.mark_as_modified()
                    break

    def on_trait_removed(self, trait_id: int):
        """Handle trait removal"""
        if self.current_character:
            # Find and remove the trait
            for i, trait in enumerate(self.current_character.character_traits):
                if trait.id == trait_id:
                    removed_trait = self.current_character.character_traits.pop(i)
                    self.logger.info(f"Removed trait: {removed_trait.name}")
                    # Refresh display
                    self.display_crew_details(self.current_character)
                    self.mark_as_modified()
                    break

    def on_condition_removed(self, condition_id: int):
        """Handle condition removal"""
        if self.current_character:
            # Find and remove the condition
            for i, condition in enumerate(self.current_character.character_conditions):
                if condition.id == condition_id:
                    removed_condition = self.current_character.character_conditions.pop(i)
                    self.logger.info(f"Removed condition: {removed_condition.name}")
                    # Refresh display
                    self.display_crew_details(self.current_character)
                    self.mark_as_modified()
                    break

    def update_characters_to_xml(self):
        """Update XML tree with current character data"""
        if self.xml_root is None:
            return

        self.logger.info("Updating XML with character changes...")

        ships_elem = self.xml_root.find("ships")
        if ships_elem is None:
            self.logger.warning("No ships element in XML")
            return

        updated_count = 0

        for ship_elem in ships_elem.findall("ship"):
            ship_sid = int(ship_elem.get("sid", "0"))

            characters_elem = ship_elem.find("characters")
            if characters_elem is None:
                continue

            for char_elem in characters_elem.findall("c"):
                char_entity_id = int(char_elem.get("entId", "0"))

                # Find matching character in our data
                character = None
                for char in self.characters:
                    if char.character_entity_id == char_entity_id and char.ship_sid == ship_sid:
                        character = char
                        break

                if character is None:
                    continue

                # Update character name IN-PLACE
                char_elem.set("name", character.character_name)
                self.logger.debug(f"  Updated name: {character.character_name}")

                # Update personality data
                pers_elem = char_elem.find("pers")
                if pers_elem is None:
                    self.logger.warning(f"No pers element for character {character.character_name}")
                    continue

                # Update attributes IN-PLACE (don't remove/recreate to preserve order and formatting)
                attr_elem = pers_elem.find("attr")
                if attr_elem is not None:
                    # Update existing attribute elements by finding by ID
                    for attr in character.character_attributes:
                        found = False
                        for a_elem in attr_elem.findall("a"):
                            if int(a_elem.get("id", "0")) == attr.id:
                                # Update points in-place
                                a_elem.set("points", str(attr.value))
                                self.logger.debug(f"  Updated attribute {attr.name}: points={attr.value}")
                                found = True
                                break

                        # Only add new attribute if it doesn't exist (shouldn't happen normally)
                        if not found:
                            self.logger.warning(f"Attribute {attr.id} not found in XML, skipping")

                # Update skills - both level and max learning
                skills_elem = pers_elem.find("skills")
                if skills_elem is not None:
                    # Update existing skill elements
                    for s_elem in skills_elem.findall("s"):
                        skill_id = int(s_elem.get("sk", "0"))

                        # Find matching skill in character
                        for skill in character.character_skills:
                            if skill.id == skill_id:
                                s_elem.set("level", str(skill.value))
                                s_elem.set("mxn", str(skill.max_value))
                                self.logger.debug(f"  Updated skill {skill.name}: level={skill.value}, mxn={skill.max_value}")
                                break

                # Update traits (remove deleted ones)
                traits_elem = pers_elem.find("traits")
                if traits_elem is not None:
                    # Get current trait IDs
                    current_trait_ids = {trait.id for trait in character.character_traits}

                    # Remove traits that are no longer in the character
                    for t_elem in list(traits_elem.findall("t")):
                        trait_id = int(t_elem.get("id", "0"))
                        if trait_id not in current_trait_ids:
                            traits_elem.remove(t_elem)

                # Update conditions (remove deleted ones)
                conditions_elem = pers_elem.find("conditions")
                if conditions_elem is not None:
                    # Get current condition IDs
                    current_condition_ids = {cond.id for cond in character.character_conditions}

                    # Remove conditions that are no longer in the character
                    for c_elem in list(conditions_elem.findall("c")):
                        cond_id = int(c_elem.get("id", "0"))
                        if cond_id not in current_condition_ids:
                            conditions_elem.remove(c_elem)

                updated_count += 1

        self.logger.info(f"Updated {updated_count} characters in XML")

    def update_storage_to_xml(self):
        """Update XML tree with current storage data"""
        if self.xml_root is None:
            return
        
        self.logger.info("Updating XML with storage changes...")
        
        ships_elem = self.xml_root.find("ships")
        if ships_elem is None:
            self.logger.warning("No ships element in XML")
            return
        
        updated_count = 0
        
        for ship_elem in ships_elem.findall("ship"):
            ship_sid = int(ship_elem.get("sid", "0"))
            
            # Find matching ship in our data
            ship = None
            for s in self.ships:
                if s.sid == ship_sid:  # FIXED: was s.ship_sid
                    ship = s
                    break
            
            if ship is None or not ship.storage_containers:
                continue
            
            # Find all feat elements with eatAllowed (storage containers)
            feat_elements = ship_elem.findall(".//feat[@eatAllowed]")
            
            # Match feat elements to our containers (by index)
            for container_index, feat_elem in enumerate(feat_elements):
                if container_index >= len(ship.storage_containers):
                    break
                
                container = ship.storage_containers[container_index]
                
                # Find or create inv element
                inv_elem = feat_elem.find("inv")
                if inv_elem is None:
                    inv_elem = ET.SubElement(feat_elem, "inv")
                
                # Clear existing items
                for s_elem in list(inv_elem.findall("s")):
                    inv_elem.remove(s_elem)
                
                # Add current items
                for item in container.items:
                    if item.quantity > 0:  # Only add items with quantity > 0
                        s_elem = ET.SubElement(inv_elem, "s")
                        s_elem.set("elementaryId", item.item_id)
                        s_elem.set("inStorage", str(item.quantity))
                        s_elem.set("onTheWayIn", "0")
                        s_elem.set("onTheWayOut", "0")
                
                updated_count += 1
                self.logger.debug(f"  Updated storage container {container_index + 1} with {len(container.items)} items")
        
        self.logger.info(f"Updated {updated_count} storage containers in XML")

    def max_all_attributes(self):
        """Set all attributes to maximum"""
        if self.current_character:
            self.logger.info("Setting all attributes to maximum")
            for attr_id, editor in self.attribute_editors.items():
                editor.set_to_max()

    def max_all_skills(self):
        """Set all skills to absolute maximum (10)"""
        if self.current_character:
            self.logger.info("Setting all skills to absolute maximum (10)")
            for skill_id, editor in self.skill_editors.items():
                editor.set_to_max()

    def max_all_skills_to_learning(self):
        """Set all skills to their max learning potential"""
        if self.current_character:
            self.logger.info("Setting all skills to max learning potential")
            for skill_id, editor in self.skill_editors.items():
                editor.set_to_max_learning()

    def mark_as_modified(self):
        """Mark the save file as modified (needs saving)"""
        if self.current_file_path and "[Modified]" not in self.windowTitle():
            self.setWindowTitle(self.windowTitle() + " [Modified]")
            
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
            self.current_storage_container = None
            return
            
        container = self.container_combo.itemData(index)
        if container:
            self.current_storage_container = container
            self.display_storage_items(container)
            
    def display_storage_items(self, container: StorageContainer):
        """Display items in a storage container with editable quantities"""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtCore import Qt
        
        # Block signals during population to avoid triggering on_storage_item_changed
        self.storage_table.blockSignals(True)
        self.storage_table.setRowCount(0)
        
        # Calculate total quantity and update info label with capacity
        total_quantity = sum(item.quantity for item in container.items)
        capacity = container.capacity
        percentage = (total_quantity / capacity * 100) if capacity > 0 else 0
        
        # Color code based on capacity usage
        if percentage >= 90:
            color = "red"
        elif percentage >= 75:
            color = "orange"
        else:
            color = "gray"
        
        self.storage_info_label.setText(
            f'<span style="color: {color};">Total: {total_quantity}/{capacity} items ({percentage:.1f}% full)</span>'
        )
        
        for item in container.items:
            row = self.storage_table.rowCount()
            self.storage_table.insertRow(row)
            
            # ID column (read-only)
            id_item = QTableWidgetItem(item.item_id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.storage_table.setItem(row, 0, id_item)
            
            # Name column (read-only)
            name_item = QTableWidgetItem(item.item_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.storage_table.setItem(row, 1, name_item)
            
            # Quantity column (editable)
            quantity_item = QTableWidgetItem(str(item.quantity))
            quantity_item.setData(256, item)  # Store reference to item
            self.storage_table.setItem(row, 2, quantity_item)
            
            # Actions column (delete button)
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, i=item: self.delete_storage_item(i))
            self.storage_table.setCellWidget(row, 3, delete_btn)
        
        # Re-enable signals
        self.storage_table.blockSignals(False)

    def populate_add_item_combo(self):
        """Populate the add item dropdown with essential items"""
        # Essential items requested by user
        essential_items = [
            # Blocks
            (162, "Infrablock"),
            (1921, "Soft Block"),
            (930, "Techblock"),
            (1919, "Energy Block"),
            (1759, "Hull Block"),
            (1920, "Superblock"),
            # Steel
            (1922, "Steel Plates"),
            # Water and Ice
            (16, "Water"),
            (40, "Ice"),
            # Food
            (15, "Root vegetables"),
            (706, "Fruits"),
            (707, "Artificial Meat"),
            (2657, "Nuts and Seeds"),
            (3378, "Grain and Hops"),
            (712, "Space Food"),
        ]
        
        self.add_item_combo.clear()
        for item_id, item_name in essential_items:
            self.add_item_combo.addItem(item_name, item_id)
        
        self.logger.info(f"Populated add item combo with {len(essential_items)} essential items")
    
    def quick_add_item(self, quantity: int):
        """Add the selected item with the specified quantity to current storage"""
        if not self.current_storage_container:
            self.logger.warning("No storage container selected")
            return
        
        # Get selected item from combo
        item_id = self.add_item_combo.currentData()
        item_name = self.add_item_combo.currentText()
        
        if not item_id:
            self.logger.warning("No item selected in combo")
            return
        
        # Check capacity
        total_quantity = sum(item.quantity for item in self.current_storage_container.items)
        if total_quantity + quantity > self.current_storage_container.capacity:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Storage Capacity",
                f"Adding {quantity} items would exceed capacity!\n\n"
                f"Current: {total_quantity}/{self.current_storage_container.capacity}\n"
                f"After: {total_quantity + quantity}/{self.current_storage_container.capacity}\n\n"
                "Note: You can still add items, but the game may reject excess."
            )
        
        self.logger.info(f"Adding {quantity}x {item_name} (ID: {item_id}) to storage")
        
        # Check if item already exists in container
        existing_item = None
        for item in self.current_storage_container.items:
            if item.item_id == str(item_id):
                existing_item = item
                break
        
        if existing_item:
            # Update existing item quantity
            existing_item.quantity += quantity
            self.logger.info(f"Updated existing item to quantity {existing_item.quantity}")
        else:
            # Create new item
            from models import StorageItem
            new_item = StorageItem()
            new_item.item_id = str(item_id)
            new_item.item_name = item_name
            new_item.quantity = quantity
            self.current_storage_container.items.append(new_item)
            self.logger.info(f"Added new item with quantity {quantity}")
        
        # Refresh display
        self.display_storage_items(self.current_storage_container)
        self.mark_as_modified()

    def resupply_preset(self, preset_type: str, quantity: int):
        """Add multiple items based on preset type
        
        Args:
            preset_type: 'infra', 'life_support', or 'ship'
            quantity: Amount of each item to add
        """
        if not self.current_storage_container:
            self.logger.warning("No storage container selected")
            return
        
        # Define preset item sets
        presets = {
            "infra": [
                (162, "Infrablock"),
                (1921, "Soft Block"),
                (930, "Techblock"),
                (1919, "Energy Block"),
                (1759, "Hull Block"),
                (1920, "Superblock"),
            ],
            "life_support": [
                (16, "Water"),
                (40, "Ice"),
                (15, "Root vegetables"),
                (706, "Fruits"),
                (707, "Artificial Meat"),
                (2657, "Nuts and Seeds"),
            ],
            "ship": [
                # TODO: Add when we find item IDs
                # (???, "Energium"),
                # (???, "Hyperium"),
            ]
        }
        
        if preset_type not in presets:
            self.logger.error(f"Unknown preset type: {preset_type}")
            return
        
        items_to_add = presets[preset_type]
        if not items_to_add:
            self.logger.warning(f"Preset '{preset_type}' has no items defined yet")
            return
        
        # Calculate total space needed
        total_quantity = sum(item.quantity for item in self.current_storage_container.items)
        space_needed = len(items_to_add) * quantity
        space_available = self.current_storage_container.capacity - total_quantity
        
        if space_needed > space_available:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Storage Capacity Warning",
                f"This will add {space_needed} items, but only {space_available} slots are available.\n\n"
                f"Current: {total_quantity}/{self.current_storage_container.capacity}\n"
                f"After: {total_quantity + space_needed}/{self.current_storage_container.capacity}\n\n"
                "Continue anyway? (Game may reject excess items)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.logger.info(f"Resupplying with preset '{preset_type}' x{quantity}")

        # Add each item
        from models import StorageItem
        for item_id, item_name in items_to_add:
            # Check if item already exists
            existing_item = None
            for item in self.current_storage_container.items:
                if item.item_id == str(item_id):
                    existing_item = item
                    break
            
            if existing_item:
                existing_item.quantity += quantity
                self.logger.debug(f"  Updated {item_name}: +{quantity} (now {existing_item.quantity})")
            else:
                new_item = StorageItem()
                new_item.item_id = str(item_id)
                new_item.item_name = item_name
                new_item.quantity = quantity
                self.current_storage_container.items.append(new_item)
                self.logger.debug(f"  Added {item_name}: {quantity}")
        
        # Refresh display and mark modified
        self.display_storage_items(self.current_storage_container)
        self.mark_as_modified()
        
        self.logger.info(f"Resupply complete: added {space_needed} items")
    
    def on_storage_item_changed(self, item):
        """Handle manual quantity edits in the storage table"""
        if not item:
            return
        
        # Only handle quantity column changes (column 2)
        if item.column() != 2:
            return
        
        # Get the StorageItem reference
        storage_item = item.data(256)
        if not storage_item:
            return
        
        try:
            new_quantity = int(item.text())
            if new_quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            old_quantity = storage_item.quantity
            storage_item.quantity = new_quantity
            
            self.logger.info(f"Updated {storage_item.item_name} quantity: {old_quantity} → {new_quantity}")
            self.mark_as_modified()
            
            # Update info label
            if self.current_storage_container:
                total_quantity = sum(i.quantity for i in self.current_storage_container.items)
                self.storage_info_label.setText(f"Total items in storage: {total_quantity}")
        
        except ValueError as e:
            self.logger.error(f"Invalid quantity entered: {e}")
            # Restore original value
            item.setText(str(storage_item.quantity))
    
    def delete_storage_item(self, item: 'StorageItem'):
        """Delete an item from the current storage container"""
        if not self.current_storage_container:
            return
        
        self.logger.info(f"Deleting {item.item_name} from storage")
        
        # Remove item from container
        self.current_storage_container.items.remove(item)
        
        # Refresh display
        self.display_storage_items(self.current_storage_container)
        self.mark_as_modified()
            
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
        self.current_save_info = None

        self.version_label.setText("Unknown")
        self.credits_input.setText("")
        self.prestige_input.setText("")
        self.sandbox_check.setChecked(False)
        self.ship_combo.clear()
        self.crew_list.clear()
        
        # Clear crew editors
        self.current_character = None
        self.attribute_editors.clear()
        self.skill_editors.clear()
        self.clear_editor_layout(self.attributes_layout)
        self.clear_editor_layout(self.skills_layout)
        self.clear_editor_layout(self.traits_layout)
        self.clear_editor_layout(self.conditions_layout)
        self.crew_name_edit.clear()
        self.crew_name_edit.setPlaceholderText("Select a crew member")
        self.crew_name_edit.setReadOnly(True)
        
        # Clear storage
        self.container_combo.clear()
        self.storage_table.setRowCount(0)

        self.setWindowTitle("Space Haven Save Editor - Python Edition")
        
    def show_first_run_setup(self):
        """Show first-run setup dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QRadioButton, QButtonGroup, QPushButton, QGroupBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Welcome to Space Haven Save Editor")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        # Welcome message
        welcome_label = QLabel(
            "<h2>Welcome!</h2>"
            "<p>This appears to be your first time running the Space Haven Save Editor.</p>"
            "<p>Let's configure a few settings to get started.</p>"
        )
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)

        # Steam folder detection
        steam_group = QGroupBox("Save Folder Location")
        steam_layout = QVBoxLayout(steam_group)

        steam_folder = self.save_config.get_steam_saves_folder()
        if steam_folder:
            steam_check = QCheckBox(f"Use Steam saves folder")
            steam_check.setChecked(True)
            steam_layout.addWidget(steam_check)

            steam_path_label = QLabel(f"Detected: {steam_folder}")
            steam_path_label.setStyleSheet("color: green; margin-left: 20px; font-size: 10px;")
            steam_layout.addWidget(steam_path_label)

            steam_info = QLabel("You can change this later in Settings.")
            steam_info.setStyleSheet("color: gray; font-size: 10px; margin-left: 20px;")
            steam_layout.addWidget(steam_info)
        else:
            no_steam_label = QLabel("Steam saves folder not detected on this system.")
            no_steam_label.setStyleSheet("color: orange;")
            steam_layout.addWidget(no_steam_label)

            manual_label = QLabel("You'll use the file browser to select saves manually.")
            manual_label.setStyleSheet("font-size: 10px; color: gray;")
            steam_layout.addWidget(manual_label)
            steam_check = None

        layout.addWidget(steam_group)

        # Backup preferences
        backup_group = QGroupBox("Backup Preferences")
        backup_layout = QVBoxLayout(backup_group)

        backup_label = QLabel("Protect your saves with automatic backups:")
        backup_layout.addWidget(backup_label)

        backup_button_group = QButtonGroup(dialog)

        auto_backup_radio = QRadioButton("Automatic - Create backups automatically when loading saves (Recommended)")
        auto_backup_radio.setChecked(True)
        backup_button_group.addButton(auto_backup_radio, 1)
        backup_layout.addWidget(auto_backup_radio)

        manual_backup_radio = QRadioButton("Manual - Ask me before creating backups")
        backup_button_group.addButton(manual_backup_radio, 2)
        backup_layout.addWidget(manual_backup_radio)

        no_backup_radio = QRadioButton("None - Don't create backups")
        backup_button_group.addButton(no_backup_radio, 3)
        backup_layout.addWidget(no_backup_radio)

        backup_info = QLabel("Backups are stored as ZIP files. You can manage them in Settings.")
        backup_info.setStyleSheet("color: gray; font-size: 10px; margin-top: 5px;")
        backup_layout.addWidget(backup_info)

        layout.addWidget(backup_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("Get Started")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # Show dialog
        if dialog.exec():
            # Save Steam folder preference
            if steam_check and steam_check.isChecked():
                self.save_config.set_use_steam_folder(True)
                self.logger.info("First-run: Steam folder enabled")

            # Save backup preference
            if auto_backup_radio.isChecked():
                self.save_config.set_auto_backup(True)
                self.logger.info("First-run: Automatic backups enabled")
            elif manual_backup_radio.isChecked():
                self.save_config.set_auto_backup(False, manual_ok=True)
                self.logger.info("First-run: Manual backups enabled")
            else:
                self.save_config.set_auto_backup(False, manual_ok=False)
                self.logger.info("First-run: Backups disabled")

            # Save config (marks first run as complete)
            self.save_config.save_config()

            # Show welcome message
            QMessageBox.information(
                self,
                "Setup Complete",
                "Setup complete! You can change these settings anytime from the Settings menu.\n\n"
                "To get started, click File → Open Save File to load a Space Haven save."
            )

    def show_settings(self):
        """Show settings dialog"""
        from settings_dialog import SettingsDialog

        dialog = SettingsDialog(self.save_config, self)
        if dialog.exec():
            # Reload backup manager with new settings
            from pathlib import Path
            self.backup_manager = BackupManager(
                Path(self.save_config.config["backup_folder"]),
                max_days=self.save_config.config["backup_count"]
            )
            self.logger.info("Settings updated")
            
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
