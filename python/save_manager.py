"""
Save Folder and Backup Management

Handles Steam folder detection, automatic backups, and version tracking.
"""

import os
import sys
import platform
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
import logging


class SaveFolderConfig:
    """Manages save folder configuration and Steam detection"""

    def __init__(self, config_file: Path = None):
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file or Path.home() / ".space_haven_editor_config.json"
        self.is_first_run = not self.config_file.exists()
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return self.default_config()
        return self.default_config()

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info(f"Config saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def default_config(self) -> dict:
        """Get default configuration"""
        return {
            "use_steam_folder": False,
            "steam_folder_path": None,
            "last_used_folder": None,
            "auto_backup": False,
            "backup_count": 3,
            "backup_folder": str(Path.home() / "SpaceHavenBackups")
        }

    def get_steam_saves_folder(self) -> Optional[Path]:
        """Detect Steam saves folder based on OS"""
        system = platform.system()

        if system == "Darwin":  # macOS
            path = Path.home() / "Library/Application Support/Spacehaven/savegames"
        elif system == "Windows":
            # Try both possible locations
            appdata = os.getenv('APPDATA')
            if appdata:
                path = Path(appdata) / "Spacehaven" / "savegames"
            else:
                path = Path.home() / "AppData/Roaming/Spacehaven/savegames"
        elif system == "Linux":
            path = Path.home() / ".local/share/Spacehaven/savegames"
        else:
            self.logger.warning(f"Unknown OS: {system}")
            return None

        if path.exists():
            self.logger.info(f"Found Steam saves folder: {path}")
            return path
        else:
            self.logger.warning(f"Steam saves folder not found: {path}")
            return None

    def set_use_steam_folder(self, use_steam: bool):
        """Set whether to use Steam folder"""
        self.config["use_steam_folder"] = use_steam
        if use_steam:
            steam_path = self.get_steam_saves_folder()
            if steam_path:
                self.config["steam_folder_path"] = str(steam_path)
            else:
                self.logger.error("Cannot use Steam folder - not found")
                self.config["use_steam_folder"] = False
        self.save_config()

    def set_last_used_folder(self, folder_path: str):
        """Remember last used folder"""
        self.config["last_used_folder"] = folder_path
        self.save_config()

    def get_default_folder(self) -> Optional[Path]:
        """Get the default folder to use (Steam or last used)"""
        if self.config["use_steam_folder"] and self.config["steam_folder_path"]:
            return Path(self.config["steam_folder_path"])
        elif self.config["last_used_folder"]:
            return Path(self.config["last_used_folder"])
        return None

    def set_auto_backup(self, auto: bool, manual_ok: bool = True):
        """Set automatic backup mode"""
        self.config["auto_backup"] = "auto" if auto else ("manual" if manual_ok else "none")
        self.save_config()

    def set_backup_folder(self, folder: str):
        """Set backup folder location"""
        self.config["backup_folder"] = folder
        self.save_config()


class BackupManager:
    """Manages save file backups with versioning"""

    def __init__(self, backup_folder: Path, max_days: int = 3):
        self.logger = logging.getLogger(__name__)
        self.backup_folder = Path(backup_folder)
        self.max_days = max_days
        self.backup_folder.mkdir(parents=True, exist_ok=True)

    def create_backup(self, source_folder: Path, force_new: bool = False) -> Optional[Path]:
        """
        Create a ZIP backup of the save folder

        Format: yyyymmdd_N-savegames-v{version}.zip
        where N is incremented for multiple backups on same day

        Args:
            source_folder: Folder to backup
            force_new: Force new backup even if one exists today

        Returns:
            Path to created backup or None if skipped
        """
        if not source_folder.exists():
            self.logger.error(f"Source folder doesn't exist: {source_folder}")
            return None

        # Read version from info file if available
        version = self._get_save_version(source_folder)

        # Get today's date
        today = datetime.now().strftime("%Y%m%d")

        # Find existing backups for today
        existing_today = self._find_backups_for_date(today)

        if existing_today and not force_new:
            self.logger.info(f"Backup already exists for today: {existing_today[0].name}")
            return existing_today[0]

        # Determine next N value
        next_n = len(existing_today) + 1

        # Create backup filename
        version_str = f"-v{version}" if version else ""
        backup_name = f"{today}_{next_n}-savegames{version_str}.zip"
        backup_path = self.backup_folder / backup_name

        try:
            # Create ZIP backup
            self.logger.info(f"Creating backup: {backup_name}")
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_folder):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(source_folder.parent)
                        zipf.write(file_path, arcname)

            self.logger.info(f"Backup created: {backup_path}")
            return backup_path

        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None

    def _get_save_version(self, save_folder: Path) -> Optional[str]:
        """Read version from info file"""
        info_file = save_folder / "save" / "info"
        if not info_file.exists():
            info_file = save_folder / "info"

        if info_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(info_file)
                root = tree.getroot()
                version = root.get("version")
                self.logger.debug(f"Save version: {version}")
                return version
            except Exception as e:
                self.logger.warning(f"Failed to read version from info: {e}")

        return None

    def _find_backups_for_date(self, date_str: str) -> List[Path]:
        """Find all backups for a specific date"""
        pattern = f"{date_str}_*-savegames*.zip"
        backups = sorted(self.backup_folder.glob(pattern))
        return backups

    def get_all_backups(self) -> List[Tuple[str, Path, int]]:
        """
        Get all backups grouped by date

        Returns:
            List of (date, path, size_bytes)
        """
        backups = []
        for backup_file in sorted(self.backup_folder.glob("*-savegames*.zip")):
            date_str = backup_file.name[:8]  # yyyymmdd
            size = backup_file.stat().st_size
            backups.append((date_str, backup_file, size))
        return backups

    def get_backup_dates(self) -> List[str]:
        """Get list of unique backup dates"""
        backups = self.get_all_backups()
        dates = sorted(set(date for date, _, _ in backups), reverse=True)
        return dates

    def get_total_backup_size(self) -> int:
        """Get total size of all backups in bytes"""
        total = sum(size for _, _, size in self.get_all_backups())
        return total

    def prune_old_backups(self, keep_days: int = None, dry_run: bool = False) -> List[Path]:
        """
        Remove backups older than keep_days

        Args:
            keep_days: Number of recent days to keep (default: self.max_days)
            dry_run: If True, return what would be deleted without deleting

        Returns:
            List of deleted (or would-be-deleted) paths
        """
        if keep_days is None:
            keep_days = self.max_days

        dates = self.get_backup_dates()

        if len(dates) <= keep_days:
            self.logger.info(f"Only {len(dates)} backup dates, keeping all")
            return []

        # Dates to delete (older than keep_days most recent)
        dates_to_delete = dates[keep_days:]

        deleted = []
        for date_str in dates_to_delete:
            backups = self._find_backups_for_date(date_str)
            for backup_path in backups:
                if not dry_run:
                    try:
                        backup_path.unlink()
                        self.logger.info(f"Deleted old backup: {backup_path.name}")
                        deleted.append(backup_path)
                    except Exception as e:
                        self.logger.error(f"Failed to delete {backup_path}: {e}")
                else:
                    self.logger.info(f"Would delete: {backup_path.name}")
                    deleted.append(backup_path)

        return deleted

    def restore_backup(self, backup_path: Path, target_folder: Path) -> bool:
        """
        Restore a backup to target folder

        Args:
            backup_path: Path to ZIP backup
            target_folder: Where to extract

        Returns:
            True if successful
        """
        if not backup_path.exists():
            self.logger.error(f"Backup doesn't exist: {backup_path}")
            return False

        try:
            self.logger.info(f"Restoring backup: {backup_path.name}")
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(target_folder)
            self.logger.info(f"Backup restored to: {target_folder}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False


class SaveFolderInfo:
    """Parse and store save folder metadata"""

    def __init__(self, folder_path: Path):
        self.logger = logging.getLogger(__name__)
        self.folder_path = Path(folder_path)
        self.save_path = self.folder_path / "save"

        # Parsed info
        self.version = None
        self.date = None
        self.real_time_date = None
        self.game_file_exists = False
        self.info_file_exists = False
        self.balanced_bin_exists = False
        self.stats_bin_exists = False

        self._parse_folder()

    def _parse_folder(self):
        """Parse folder structure and info file"""
        # Check for game file
        game_file = self.save_path / "game"
        self.game_file_exists = game_file.exists()

        # Check for bin files
        self.balanced_bin_exists = (self.save_path / "balanced.bin").exists()
        self.stats_bin_exists = (self.save_path / "stats.bin").exists()

        # Parse info file
        info_file = self.save_path / "info"
        self.info_file_exists = info_file.exists()

        if self.info_file_exists:
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(info_file)
                root = tree.getroot()

                self.version = root.get("version")
                self.date = root.get("date")
                self.real_time_date = root.get("realTimeDate")

                self.logger.info(f"Save info: version={self.version}, date={self.date}")
            except Exception as e:
                self.logger.error(f"Failed to parse info file: {e}")

    def is_valid_save(self) -> bool:
        """Check if this is a valid save folder"""
        return self.game_file_exists and self.info_file_exists

    def get_version_number(self) -> Optional[int]:
        """Get version as integer"""
        if self.version:
            try:
                return int(self.version)
            except ValueError:
                return None
        return None

    def get_display_name(self) -> str:
        """Get display name for this save"""
        name = self.folder_path.name
        if self.version:
            name += f" (v{self.version})"
        return name

    def __str__(self) -> str:
        return f"SaveFolder({self.folder_path.name}, v{self.version}, valid={self.is_valid_save()})"
