"""
Crew Editor Widgets

Reusable components for editing character attributes, skills, and other numeric values
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSpinBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from typing import Optional
import logging


class NumericValueEditor(QWidget):
    """
    Reusable component for editing a single numeric value with constraints

    Features:
    - Display ID, name, and metadata
    - Min/Max/Current value tracking
    - Increment/Decrement buttons
    - Set to Min/Max buttons
    - Value changed signal for parent widgets
    """

    valueChanged = pyqtSignal(int, int)  # (item_id, new_value)

    def __init__(
        self,
        item_id: int,
        name: str,
        current_value: int,
        min_value: int = 0,
        max_value: int = 10,
        metadata: Optional[dict] = None,
        parent=None
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        self.item_id = item_id
        self.name = name
        self.current_value = current_value
        self.min_value = min_value
        self.max_value = max_value
        self.metadata = metadata or {}

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        # Name label (fixed width for alignment)
        name_label = QLabel(self.name)
        name_label.setMinimumWidth(150)
        layout.addWidget(name_label)

        # Min button
        self.min_btn = QPushButton("⌊")
        self.min_btn.setToolTip("Set to minimum")
        self.min_btn.setMaximumWidth(30)
        self.min_btn.clicked.connect(self.set_to_min)
        layout.addWidget(self.min_btn)

        # Decrease button
        self.dec_btn = QPushButton("-")
        self.dec_btn.setMaximumWidth(30)
        self.dec_btn.clicked.connect(self.decrement)
        layout.addWidget(self.dec_btn)

        # Value spinbox
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(self.min_value)
        self.spinbox.setMaximum(self.max_value)
        self.spinbox.setValue(self.current_value)
        self.spinbox.setMaximumWidth(60)
        self.spinbox.valueChanged.connect(self.on_value_changed)
        layout.addWidget(self.spinbox)

        # Increase button
        self.inc_btn = QPushButton("+")
        self.inc_btn.setMaximumWidth(30)
        self.inc_btn.clicked.connect(self.increment)
        layout.addWidget(self.inc_btn)

        # Max button
        self.max_btn = QPushButton("⌈")
        self.max_btn.setToolTip("Set to maximum")
        self.max_btn.setMaximumWidth(30)
        self.max_btn.clicked.connect(self.set_to_max)
        layout.addWidget(self.max_btn)

        # Range label
        range_label = QLabel(f"({self.min_value}-{self.max_value})")
        range_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(range_label)

        layout.addStretch()

        self.update_button_states()

    def increment(self):
        """Increment the value by 1"""
        new_value = min(self.current_value + 1, self.max_value)
        self.spinbox.setValue(new_value)

    def decrement(self):
        """Decrement the value by 1"""
        new_value = max(self.current_value - 1, self.min_value)
        self.spinbox.setValue(new_value)

    def set_to_min(self):
        """Set value to minimum"""
        self.spinbox.setValue(self.min_value)

    def set_to_max(self):
        """Set value to maximum"""
        self.spinbox.setValue(self.max_value)

    def on_value_changed(self, new_value: int):
        """Handle value change"""
        self.current_value = new_value
        self.update_button_states()
        self.valueChanged.emit(self.item_id, new_value)
        self.logger.debug(f"{self.name} changed to {new_value}")

    def update_button_states(self):
        """Enable/disable buttons based on current value"""
        self.dec_btn.setEnabled(self.current_value > self.min_value)
        self.min_btn.setEnabled(self.current_value > self.min_value)
        self.inc_btn.setEnabled(self.current_value < self.max_value)
        self.max_btn.setEnabled(self.current_value < self.max_value)

    def get_value(self) -> int:
        """Get the current value"""
        return self.current_value


class SkillBarWidget(QWidget):
    """
    Visual representation of a skill with bar display

    Shows:
    - Empty 10-slot bar
    - Max learning potential (darker fill)
    - Current skill level (lighter fill)
    """

    def __init__(self, current_level: int, max_learning: int, parent=None):
        super().__init__(parent)
        self.current_level = current_level
        self.max_learning = max_learning
        self.total_slots = 10

        self.setMinimumSize(120, 24)
        self.setMaximumSize(120, 24)

    def set_values(self, current_level: int, max_learning: int):
        """Update the skill values and repaint"""
        self.current_level = current_level
        self.max_learning = max_learning
        self.update()

    def paintEvent(self, event):
        """Custom paint to draw the skill bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        slot_width = self.width() / self.total_slots
        slot_height = self.height() - 4

        # Draw each slot
        for i in range(self.total_slots):
            x = i * slot_width

            # Determine fill color for this slot
            if i < self.current_level:
                # Current skill level - lighter color
                fill_color = QColor(100, 200, 100, 220)  # Light green
                border_color = QColor(80, 180, 80)
            elif i < self.max_learning:
                # Max learning potential - darker color
                fill_color = QColor(60, 120, 60, 180)  # Dark green
                border_color = QColor(50, 100, 50)
            else:
                # Empty slot
                fill_color = QColor(240, 240, 240, 100)  # Very light gray
                border_color = QColor(200, 200, 200)

            # Draw slot
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(border_color, 1))
            painter.drawRect(int(x + 1), 2, int(slot_width - 2), int(slot_height))


class SkillEditor(QWidget):
    """
    Editor for skills with visual bar representation
    
    Tracks original and current skill level. Max learning is fixed (cannot be edited).
    Skill can only be modified between original value and max learning potential.
    """

    valueChanged = pyqtSignal(int, int, int)  # (skill_id, current_level, max_learning)

    def __init__(
        self,
        skill_id: int,
        name: str,
        current_level: int,
        max_learning: int,
        parent=None
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        self.skill_id = skill_id
        self.name = name
        
        # Store original values for reset
        self.original_current_level = current_level
        self.original_max_learning = max_learning
        
        # Current working values
        self.current_level = current_level
        self.max_learning = max_learning  # Fixed - cannot be edited
        
        # Constants
        self.min_level = self.original_current_level  # Can only go down to original
        self.max_level = max_learning  # Can only go up to max learning

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        # Name label
        name_label = QLabel(self.name)
        name_label.setMinimumWidth(150)
        layout.addWidget(name_label)

        # Skill bar visualization
        self.skill_bar = SkillBarWidget(self.current_level, self.max_learning)
        layout.addWidget(self.skill_bar)

        # Min button (goes to original value)
        self.min_btn = QPushButton("⌊")
        self.min_btn.setToolTip(f"Reset to original value ({self.original_current_level})")
        self.min_btn.setMaximumWidth(30)
        self.min_btn.clicked.connect(self.set_to_min)
        layout.addWidget(self.min_btn)

        # Decrease button
        self.dec_btn = QPushButton("-")
        self.dec_btn.setMaximumWidth(30)
        self.dec_btn.setToolTip("Decrease current skill level")
        self.dec_btn.clicked.connect(self.decrement)
        layout.addWidget(self.dec_btn)

        # Value spinbox
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(self.min_level)
        self.spinbox.setMaximum(self.max_level)
        self.spinbox.setValue(self.current_level)
        self.spinbox.setMaximumWidth(50)
        self.spinbox.valueChanged.connect(self.on_value_changed)
        layout.addWidget(self.spinbox)

        # Increase button
        self.inc_btn = QPushButton("+")
        self.inc_btn.setMaximumWidth(30)
        self.inc_btn.setToolTip("Increase current skill level")
        self.inc_btn.clicked.connect(self.increment)
        layout.addWidget(self.inc_btn)

        # Max button (goes to max learning)
        self.max_btn = QPushButton("⌈")
        self.max_btn.setToolTip(f"Set to max learning ({self.max_learning})")
        self.max_btn.setMaximumWidth(30)
        self.max_btn.clicked.connect(self.set_to_max)
        layout.addWidget(self.max_btn)

        # Info label - show original in gray if different
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: gray; font-size: 10px;")
        self.info_label.setMinimumWidth(100)
        self.update_info_label()
        layout.addWidget(self.info_label)

        layout.addStretch()

        self.update_button_states()

    def update_info_label(self):
        """Update info label showing current/max and original if different"""
        info_text = f"({self.current_level}/{self.max_learning}/10)"
        if self.current_level != self.original_current_level:
            info_text += f" [was {self.original_current_level}]"
        self.info_label.setText(info_text)

    def increment(self):
        """Increment the value by 1"""
        new_value = min(self.current_level + 1, self.max_level)
        self.spinbox.setValue(new_value)

    def decrement(self):
        """Decrement the value by 1"""
        new_value = max(self.current_level - 1, self.min_level)
        self.spinbox.setValue(new_value)

    def set_to_min(self):
        """Set value to original value"""
        self.spinbox.setValue(self.original_current_level)

    def set_to_max(self):
        """Set value to max learning potential"""
        self.spinbox.setValue(self.max_learning)

    def on_value_changed(self, new_value: int):
        """Handle value change"""
        # Constrain to original <= current <= max_learning
        if new_value < self.original_current_level:
            new_value = self.original_current_level
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(new_value)
            self.spinbox.blockSignals(False)
        elif new_value > self.max_learning:
            new_value = self.max_learning
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(new_value)
            self.spinbox.blockSignals(False)
        
        self.current_level = new_value
        self.update_display()

    def update_display(self):
        """Update visual elements and emit signal"""
        self.skill_bar.set_values(self.current_level, self.max_learning)
        self.update_info_label()
        self.update_button_states()
        self.valueChanged.emit(self.skill_id, self.current_level, self.max_learning)
        self.logger.debug(f"{self.name} changed to skill={self.current_level}")

    def update_button_states(self):
        """Enable/disable buttons based on current values"""
        # Can decrease if above original
        self.dec_btn.setEnabled(self.current_level > self.original_current_level)
        self.min_btn.setEnabled(self.current_level > self.original_current_level)
        
        # Can increase if below max learning
        self.inc_btn.setEnabled(self.current_level < self.max_learning)
        self.max_btn.setEnabled(self.current_level < self.max_learning)

    def get_values(self) -> tuple[int, int]:
        """Get both current skill level and max learning"""
        return (self.current_level, self.max_learning)

    def set_to_max_learning(self):
        """Set current skill to max learning potential (for batch operations)"""
        self.spinbox.setValue(self.max_learning)


class TraitWidget(QWidget):
    """
    Widget for displaying and managing a trait

    Shows trait name and allow removal
    """

    traitRemoved = pyqtSignal(int)  # (trait_id)

    def __init__(self, trait_id: int, name: str, parent=None):
        super().__init__(parent)
        self.trait_id = trait_id
        self.name = name

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        # Trait name
        name_label = QLabel(self.name)
        name_label.setMinimumWidth(150)
        layout.addWidget(name_label)

        # Checkmark
        check_label = QLabel("✓")
        check_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        layout.addWidget(check_label)

        # Remove button
        remove_btn = QPushButton("✗")
        remove_btn.setToolTip("Remove trait")
        remove_btn.setMaximumWidth(30)
        remove_btn.setStyleSheet("color: red; font-weight: bold;")
        remove_btn.clicked.connect(lambda: self.traitRemoved.emit(self.trait_id))
        layout.addWidget(remove_btn)

        layout.addStretch()


class ConditionWidget(QWidget):
    """
    Widget for displaying and managing a condition

    Shows condition name and allow removal
    """

    conditionRemoved = pyqtSignal(int)  # (condition_id)

    def __init__(self, condition_id: int, name: str, parent=None):
        super().__init__(parent)
        self.condition_id = condition_id
        self.name = name

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        # Condition name
        name_label = QLabel(self.name)
        name_label.setMinimumWidth(150)
        layout.addWidget(name_label)

        # Status
        status_label = QLabel("Active")
        status_label.setStyleSheet("color: orange; font-style: italic;")
        layout.addWidget(status_label)

        # Remove button
        remove_btn = QPushButton("✗")
        remove_btn.setToolTip("Remove condition")
        remove_btn.setMaximumWidth(30)
        remove_btn.setStyleSheet("color: red; font-weight: bold;")
        remove_btn.clicked.connect(lambda: self.conditionRemoved.emit(self.condition_id))
        layout.addWidget(remove_btn)

        layout.addStretch()
