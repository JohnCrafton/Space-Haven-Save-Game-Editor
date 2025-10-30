"""
Settings Dialog

UI for configuring save folder and backup options.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QLineEdit, QSpinBox, QGroupBox, QFileDialog,
    QMessageBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from pathlib import Path
from save_manager import SaveFolderConfig, BackupManager
import logging


class SettingsDialog(QDialog):
    """Settings dialog for save folder and backup configuration"""

    def __init__(self, config: SaveFolderConfig, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.backup_manager = BackupManager(Path(config.config["backup_folder"]))

        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Save Folder Settings
        folder_group = QGroupBox("Save Folder")
        folder_layout = QVBoxLayout(folder_group)

        # Steam folder option
        self.use_steam_check = QCheckBox("Use Steam saves folder")
        self.use_steam_check.setChecked(self.config.config["use_steam_folder"])
        self.use_steam_check.stateChanged.connect(self.on_steam_toggle)
        folder_layout.addWidget(self.use_steam_check)

        # Show detected Steam path
        steam_path = self.config.get_steam_saves_folder()
        if steam_path:
            steam_label = QLabel(f"Detected: {steam_path}")
            steam_label.setStyleSheet("color: green; margin-left: 20px;")
            folder_layout.addWidget(steam_label)
        else:
            steam_label = QLabel("Steam folder not detected on this system")
            steam_label.setStyleSheet("color: orange; margin-left: 20px;")
            folder_layout.addWidget(steam_label)
            self.use_steam_check.setEnabled(False)

        # Last used folder display
        last_folder = self.config.config.get("last_used_folder")
        if last_folder:
            last_label = QLabel(f"Last used: {last_folder}")
            last_label.setStyleSheet("color: gray; margin-left: 20px; font-size: 10px;")
            folder_layout.addWidget(last_label)

        layout.addWidget(folder_group)

        # Backup Settings
        backup_group = QGroupBox("Backup Settings")
        backup_layout = QVBoxLayout(backup_group)

        # Backup mode
        backup_mode_label = QLabel("Backup mode:")
        backup_layout.addWidget(backup_mode_label)

        self.backup_button_group = QButtonGroup()

        self.auto_backup_radio = QRadioButton("Automatic (create backups automatically)")
        self.manual_backup_radio = QRadioButton("Manual (ask before backup)")
        self.no_backup_radio = QRadioButton("None (no backups)")

        self.backup_button_group.addButton(self.auto_backup_radio, 1)
        self.backup_button_group.addButton(self.manual_backup_radio, 2)
        self.backup_button_group.addButton(self.no_backup_radio, 3)

        # Set current mode
        auto_backup = self.config.config.get("auto_backup", False)
        if auto_backup == "auto":
            self.auto_backup_radio.setChecked(True)
        elif auto_backup == "manual":
            self.manual_backup_radio.setChecked(True)
        else:
            self.no_backup_radio.setChecked(True)

        backup_layout.addWidget(self.auto_backup_radio)
        backup_layout.addWidget(self.manual_backup_radio)
        backup_layout.addWidget(self.no_backup_radio)

        # Backup count
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Keep last"))
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setMinimum(1)
        self.backup_count_spin.setMaximum(30)
        self.backup_count_spin.setValue(self.config.config.get("backup_count", 3))
        count_layout.addWidget(self.backup_count_spin)
        count_layout.addWidget(QLabel("days of backups"))
        count_layout.addStretch()
        backup_layout.addLayout(count_layout)

        # Backup folder
        folder_select_layout = QHBoxLayout()
        folder_select_layout.addWidget(QLabel("Backup folder:"))
        self.backup_folder_edit = QLineEdit(self.config.config.get("backup_folder", ""))
        self.backup_folder_edit.setReadOnly(True)
        folder_select_layout.addWidget(self.backup_folder_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_backup_folder)
        folder_select_layout.addWidget(browse_btn)
        backup_layout.addLayout(folder_select_layout)

        # Backup info
        total_size = self.backup_manager.get_total_backup_size()
        size_mb = total_size / (1024 * 1024)
        backup_count = len(self.backup_manager.get_all_backups())
        info_text = f"Current: {backup_count} backups, {size_mb:.1f} MB"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: gray; font-size: 10px; margin-top: 5px;")
        backup_layout.addWidget(info_label)

        # Manage backups button
        manage_btn = QPushButton("Manage Backups...")
        manage_btn.clicked.connect(self.manage_backups)
        backup_layout.addWidget(manage_btn)

        layout.addWidget(backup_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def on_steam_toggle(self, state):
        """Handle Steam folder toggle"""
        if state == Qt.CheckState.Checked.value:
            steam_path = self.config.get_steam_saves_folder()
            if not steam_path:
                QMessageBox.warning(
                    self,
                    "Steam Folder Not Found",
                    "Could not find Steam saves folder on this system."
                )
                self.use_steam_check.setChecked(False)

    def browse_backup_folder(self):
        """Browse for backup folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Folder",
            self.backup_folder_edit.text()
        )
        if folder:
            self.backup_folder_edit.setText(folder)

    def manage_backups(self):
        """Show backup management dialog"""
        dialog = BackupManagementDialog(self.backup_manager, self)
        dialog.exec()

    def accept(self):
        """Save settings and close"""
        # Save folder settings
        self.config.set_use_steam_folder(self.use_steam_check.isChecked())

        # Backup mode
        if self.auto_backup_radio.isChecked():
            self.config.set_auto_backup(True)
        elif self.manual_backup_radio.isChecked():
            self.config.set_auto_backup(False, manual_ok=True)
        else:
            self.config.set_auto_backup(False, manual_ok=False)

        # Backup count
        self.config.config["backup_count"] = self.backup_count_spin.value()

        # Backup folder
        backup_folder = self.backup_folder_edit.text()
        if backup_folder:
            self.config.set_backup_folder(backup_folder)

        self.config.save_config()

        super().accept()


class BackupManagementDialog(QDialog):
    """Dialog for managing existing backups"""

    def __init__(self, backup_manager: BackupManager, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.backup_manager = backup_manager

        self.setWindowTitle("Manage Backups")
        self.setMinimumSize(500, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem

        layout = QVBoxLayout(self)

        # Info
        total_size = self.backup_manager.get_total_backup_size()
        size_mb = total_size / (1024 * 1024)
        backup_count = len(self.backup_manager.get_all_backups())
        info_label = QLabel(f"Total: {backup_count} backups using {size_mb:.1f} MB")
        info_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(info_label)

        # Backup list
        self.backup_list = QListWidget()

        # Group by date
        dates = self.backup_manager.get_backup_dates()
        for date in dates:
            # Add date header
            date_item = QListWidgetItem(f"--- {date} ---")
            date_item.setFlags(Qt.ItemFlag.NoItemFlags)
            date_item.setBackground(Qt.GlobalColor.lightGray)
            self.backup_list.addItem(date_item)

            # Add backups for this date
            backups = self.backup_manager._find_backups_for_date(date)
            for backup_path in backups:
                size = backup_path.stat().st_size
                size_mb = size / (1024 * 1024)
                item_text = f"  {backup_path.name} ({size_mb:.1f} MB)"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, backup_path)
                self.backup_list.addItem(item)

        layout.addWidget(self.backup_list)

        # Buttons
        button_layout = QHBoxLayout()

        prune_btn = QPushButton("Prune Old Backups...")
        prune_btn.clicked.connect(self.prune_backups)
        button_layout.addWidget(prune_btn)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def prune_backups(self):
        """Prune old backups with confirmation"""
        from PyQt6.QtWidgets import QInputDialog

        keep_days, ok = QInputDialog.getInt(
            self,
            "Prune Backups",
            "Keep how many days of backups?",
            value=3,
            min=1,
            max=30
        )

        if not ok:
            return

        # Dry run to see what would be deleted
        to_delete = self.backup_manager.prune_old_backups(keep_days, dry_run=True)

        if not to_delete:
            QMessageBox.information(
                self,
                "Prune Backups",
                f"No backups older than {keep_days} days found."
            )
            return

        # Calculate size
        total_size = sum(p.stat().st_size for p in to_delete)
        size_mb = total_size / (1024 * 1024)

        # Confirm
        msg = f"Delete {len(to_delete)} backups ({size_mb:.1f} MB)?\n\n"
        msg += "Files to delete:\n"
        for path in to_delete[:10]:  # Show first 10
            msg += f"  {path.name}\n"
        if len(to_delete) > 10:
            msg += f"  ... and {len(to_delete) - 10} more"

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            deleted = self.backup_manager.prune_old_backups(keep_days, dry_run=False)
            QMessageBox.information(
                self,
                "Backups Pruned",
                f"Deleted {len(deleted)} old backups."
            )
            self.init_ui()  # Refresh list

    def delete_selected(self):
        """Delete selected backup"""
        item = self.backup_list.currentItem()
        if not item:
            return

        backup_path = item.data(Qt.ItemDataRole.UserRole)
        if not backup_path:
            QMessageBox.warning(self, "Delete", "Please select a backup file to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete backup:\n{backup_path.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                backup_path.unlink()
                QMessageBox.information(self, "Deleted", "Backup deleted successfully.")
                self.init_ui()  # Refresh list
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete backup:\n{e}")
