"""
Simple word-style editor: Hinglish → Hindi in Kruti Dev font encoding (legacy font bytes).
"""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtGui import (
    QAction,
    QFont,
    QFontDatabase,
    QTextCharFormat,
    QTextCursor,
)
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFontComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QToolBar,
    QWidget,
)

from hinglish_kruti import hinglish_document_to_krutidev, hinglish_selection_to_krutidev


def resolve_kruti_family() -> str:
    """Prefer a bundled TTF, then installed Windows Kruti Dev faces."""

    base = Path(__file__).resolve().parent
    for rel in ("fonts/KrutiDev010.ttf", "fonts/Kruti_Dev_010.ttf", "KrutiDev010.ttf"):
        p = base / rel
        if p.is_file():
            fid = QFontDatabase.addApplicationFont(str(p))
            if fid >= 0:
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams:
                    return fams[0]

    db = QFontDatabase()
    for name in ("Kruti Dev", "KrutiDev010", "KrutiDev", "KD", "Krutidev"):
        if name in db.families():
            return name
    return ""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hinglish → Kruti Dev Editor")
        self.resize(1000, 700)

        self.kruti_family = resolve_kruti_family()

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(True)
        self.setCentralWidget(self.editor)
        if self.kruti_family:
            self.editor.setFont(QFont(self.kruti_family, 14))
        else:
            self.editor.setFont(QFont("Arial", 12))

        self._build_toolbar()
        self._build_status_hint()

    def _build_status_hint(self) -> None:
        hint = QWidget()
        lay = QHBoxLayout(hint)
        if self.kruti_family:
            msg = f'Kruti font: "{self.kruti_family}" (place fonts/KrutiDev010.ttf next to the app if missing).'
        else:
            msg = (
                "Kruti Dev not found. Converted text will look garbled until you install "
                'Kruti Dev or add fonts/KrutiDev010.ttf beside this program.'
            )
        lay.addWidget(QLabel(msg))
        self.statusBar().addPermanentWidget(hint, 1)

    def _build_toolbar(self) -> None:
        tb = QToolBar()
        tb.setMovable(False)
        self.addToolBar(tb)

        tb.addAction(self._action("Bold", self._toggle_bold, shortcut="Ctrl+B"))
        tb.addAction(self._action("Italic", self._toggle_italic, shortcut="Ctrl+I"))
        tb.addAction(self._action("Underline", self._toggle_underline, shortcut="Ctrl+U"))

        tb.addSeparator()

        self.size_combo = QComboBox()
        for s in range(8, 37):
            self.size_combo.addItem(str(s), s)
        self.size_combo.setCurrentText("14")
        self.size_combo.currentIndexChanged.connect(self._apply_size)
        tb.addWidget(QLabel(" Size "))
        tb.addWidget(self.size_combo)

        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self._apply_font_family)
        tb.addWidget(QLabel(" Font "))
        tb.addWidget(self.font_combo)

        tb.addSeparator()

        tb.addAction(
            self._action(
                "Convert selection (Hinglish→Kruti)",
                self._convert_selection,
                shortcut="Ctrl+Shift+H",
            )
        )
        tb.addAction(self._action("Convert Latin words in document", self._convert_document))

        tb.addSeparator()
        tb.addAction(self._action("Open…", self._open_file))
        tb.addAction(self._action("Save…", self._save_file))

    def _action(self, text: str, slot, shortcut: str | None = None) -> QAction:
        a = QAction(text, self)
        a.triggered.connect(slot)
        if shortcut:
            a.setShortcut(shortcut)
        return a

    def _merge_format(self, fmt: QTextCharFormat) -> None:
        c = self.editor.textCursor()
        if not c.hasSelection():
            c.select(QTextCursor.SelectionType.WordUnderCursor)
        c.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_bold(self) -> None:
        fmt = QTextCharFormat()
        weight = QFont.Weight.Bold if self.editor.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal
        fmt.setFontWeight(weight)
        self._merge_format(fmt)

    def _toggle_italic(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self._merge_format(fmt)

    def _toggle_underline(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self._merge_format(fmt)

    def _apply_size(self) -> None:
        ok = False
        size = int(self.size_combo.currentData()) if self.size_combo.currentData() else 14
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(size))
        self._merge_format(fmt)

    def _apply_font_family(self, font: QFont) -> None:
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self._merge_format(fmt)

    def _kruti_char_format(self) -> QTextCharFormat:
        fmt = QTextCharFormat()
        if self.kruti_family:
            fmt.setFontFamily(self.kruti_family)
        pt = float(self.size_combo.currentData()) if self.size_combo.currentData() else 14.0
        fmt.setFontPointSize(pt)
        return fmt

    def _convert_selection(self) -> None:
        c = self.editor.textCursor()
        if not c.hasSelection():
            QMessageBox.information(
                self,
                "Nothing selected",
                "Select Hinglish text first, then choose Convert selection.",
            )
            return
        raw = c.selectedText().replace("\u2029", "\n")
        try:
            out = hinglish_selection_to_krutidev(raw)
        except Exception as e:
            QMessageBox.warning(self, "Convert failed", str(e))
            return
        fmt = self._kruti_char_format()
        c.beginEditBlock()
        c.insertText(out, fmt)
        c.endEditBlock()

    def _convert_document(self) -> None:
        plain = self.editor.toPlainText()
        try:
            out = hinglish_document_to_krutidev(plain)
        except Exception as e:
            QMessageBox.warning(self, "Convert failed", str(e))
            return
        fmt = self._kruti_char_format()
        self.editor.selectAll()
        c = self.editor.textCursor()
        c.beginEditBlock()
        c.insertText(out, fmt)
        c.endEditBlock()
        c.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(c)

    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open text", "", "Text files (*.txt);;All (*.*)")
        if not path:
            return
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        self.editor.setPlainText(text)

    def _save_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save text", "", "Text files (*.txt);;All (*.*)")
        if not path:
            return
        Path(path).write_text(self.editor.toPlainText(), encoding="utf-8")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("HinglishKrutiEditor")
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
