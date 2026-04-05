"""
Intelligent word suggestion system for Hinglish → Kruti Dev conversion.
Provides autocomplete suggestions when user types space.
"""

from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QFrame, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from hinglish_kruti import hinglish_document_to_krutidev


# Common Hinglish words and phrases for quick lookup
COMMON_HINGLISH_WORDS = {
    # Pronouns
    "mera": "मेरा",
    "meri": "मेरी",
    "tera": "तेरा",
    "teri": "तेरी",
    "aapka": "आपका",
    "unka": "उनका",
    "uska": "उसका",
    "iska": "इसका",
    
    # Common verbs
    "hai": "है",
    "hain": "हैं",
    "hoon": "हूँ",
    "ho": "हो",
    "ho": "हो",
    "hun": "हूँ",
    "tha": "था",
    "the": "थे",
    "thi": "थी",
    "karunga": "करूंगा",
    "karengi": "करेंगी",
    "karo": "करो",
    "kar": "कर",
    "karna": "करना",
    "karni": "करनी",
    "dekha": "देखा",
    "dekhi": "देखी",
    "dekhu": "देखू",
    "aa": "आ",
    "aa": "आ",
    "aaya": "आया",
    
    # Common nouns
    "naam": "नाम",
    "din": "दिन",
    "raat": "रात",
    "ghar": "घर",
    "shahar": "शहर",
    "mata": "माता",
    "pita": "पिता",
    "beta": "बेटा",
    "beti": "बेटी",
    "sahiba": "साहिबा",
    "sahab": "साहब",
    
    # Common adjectives
    "acha": "अच्छा",
    "achi": "अच्छी",
    "bada": "बड़ा",
    "badi": "बड़ी",
    "chota": "छोटा",
    "choti": "छोटी",
    "pyara": "प्यारा",
    "pyari": "प्यारी",
    "sundar": "सुंदर",
    "khubsurat": "खूबसूरत",
    
    # Common phrases
    "namaste": "नमस्ते",
    "shukriya": "शुक्रिया",
    "dhanyvad": "धन्यवाद",
    "maafi": "माफी",
    "haan": "हाँ",
    "nahi": "नहीं",
    "bilkul": "बिलकुल",
    "theek": "ठीक",
    "chalo": "चलो",
}


class SuggestionPopup(QFrame):
    """Popup widget showing word suggestions."""
    
    suggestion_selected = pyqtSignal(str)  # Emitted when user selects a suggestion
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet(
            "QFrame { background: #ffffff; border: 1px solid #a0a0a0; border-radius: 3px; }"
        )
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "QListWidget { border: none; }"
            "QListWidget::item { padding: 6px 8px; }"
            "QListWidget::item:hover { background: #e5f3ff; }"
            "QListWidget::item:selected { background: #0078d4; color: #ffffff; }"
        )
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
        self.setLayout(layout)
        self.hide()
        self._current_suggestions = []
    
    def show_suggestions(self, hinglish_word: str, suggestions: list[tuple[str, str]]) -> None:
        """Show suggestions for a Hinglish word.
        
        Args:
            hinglish_word: The original Hinglish word typed
            suggestions: List of (hinglish, krutidev) tuples
        """
        self.list_widget.clear()
        self._current_suggestions = suggestions
        
        if not suggestions:
            self.hide()
            return
        
        for hind, kruti in suggestions:
            item = QListWidgetItem(f"{hind}  →  {kruti}")
            item.setData(Qt.ItemDataRole.UserRole, kruti)
            self.list_widget.addItem(item)
        
        # Auto-select first item
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
        
        self.show()
    
    def get_selected_suggestion(self) -> str:
        """Get the currently selected Kruti Dev word."""
        current_item = self.list_widget.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return ""
    
    def highlight_next(self) -> None:
        """Move highlight to next suggestion."""
        current = self.list_widget.currentRow()
        if current < self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(current + 1)
    
    def highlight_prev(self) -> None:
        """Move highlight to previous suggestion."""
        current = self.list_widget.currentRow()
        if current > 0:
            self.list_widget.setCurrentRow(current - 1)
    
    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        kruti_word = item.data(Qt.ItemDataRole.UserRole)
        self.suggestion_selected.emit(kruti_word)


class WordSuggester:
    """Intelligent word suggestion engine."""
    
    def __init__(self):
        self.word_map = COMMON_HINGLISH_WORDS.copy()
    
    def get_suggestions(self, hinglish_word: str) -> list[tuple[str, str]]:
        """Get Kruti Dev suggestions for a Hinglish word.
        
        Returns:
            List of (hinglish, krutidev) tuples
        """
        hinglish_word = hinglish_word.lower().strip()
        
        if not hinglish_word:
            return []
        
        suggestions = []
        
        # Exact match takes precedence
        if hinglish_word in self.word_map:
            kruti = self.word_map[hinglish_word]
            suggestions.append((hinglish_word, kruti))
            return suggestions
        
        # Prefix matching for fuzzy suggestions
        for word, kruti in self.word_map.items():
            if word.startswith(hinglish_word):
                suggestions.append((word, kruti))
        
        # Limit to top 5 suggestions
        return suggestions[:5]
    
    def convert_word(self, hinglish_word: str) -> str:
        """Convert a single Hinglish word to Kruti Dev.
        
        Uses direct lookup first, then tries conversion if not in dictionary.
        """
        hinglish_word_lower = hinglish_word.lower()
        
        # Direct lookup
        if hinglish_word_lower in self.word_map:
            return self.word_map[hinglish_word_lower]
        
        # Fallback to conversion function
        try:
            from hinglish_kruti import hinglish_document_to_krutidev
            return hinglish_document_to_krutidev(hinglish_word)
        except:
            return hinglish_word
    
    def add_word(self, hinglish: str, krutidev: str) -> None:
        """Add or update a word in the suggestion dictionary."""
        self.word_map[hinglish.lower()] = krutidev
