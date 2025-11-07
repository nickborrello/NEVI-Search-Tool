from PyQt6 import QtWidgets, QtGui, QtCore
from pypdf import PdfReader

class ReaderWindow(QtWidgets.QWidget):
    def __init__(self, pdf_path, matched_pages, term_sets, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Viewer - Highlighted Matches")
        self.resize(1000, 700)
        self.setWindowIcon(QtGui.QIcon("assets/wpi_logo.ico"))  # Assuming icon exists

        self.pdf_path = pdf_path
        self.matched_pages = matched_pages
        self.term_sets = term_sets
        self.current_index = 0

        self.reader = PdfReader(self.pdf_path)

        self.setup_ui()

        # Apply professional stylesheet
        self.setStyleSheet("""
            QWidget { background-color: #f5f5f5; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            QTextEdit { background-color: white; border: 1px solid #cccccc; border-radius: 4px; padding: 8px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; }
            QPushButton { background-color: #0078d4; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
            QLabel { color: #333333; font-weight: bold; }
            QGroupBox { font-weight: bold; border: 2px solid #cccccc; border-radius: 5px; margin-top: 1ex; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; color: #333333; }
        """)

        self.update_page()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Text Viewer Section
        viewer_group = QtWidgets.QGroupBox("Document Content")
        viewer_layout = QtWidgets.QVBoxLayout(viewer_group)
        self.text_viewer = QtWidgets.QTextEdit(self)
        self.text_viewer.setReadOnly(True)
        self.text_viewer.setFont(QtGui.QFont("Segoe UI", 11))
        viewer_layout.addWidget(self.text_viewer)
        layout.addWidget(viewer_group)

        # Navigation Section
        nav_group = QtWidgets.QGroupBox("Navigation")
        nav_layout = QtWidgets.QHBoxLayout(nav_group)
        self.prev_button = QtWidgets.QPushButton("⬅️ Previous Page")
        self.prev_button.setToolTip("Go to previous matched page")
        nav_layout.addWidget(self.prev_button)

        self.page_label = QtWidgets.QLabel("Page: N/A")
        self.page_label.setAlignment(QtCore.Qt.AlignCenter)
        nav_layout.addWidget(self.page_label, stretch=1)

        self.next_button = QtWidgets.QPushButton("Next Page ➡️")
        self.next_button.setToolTip("Go to next matched page")
        nav_layout.addWidget(self.next_button)
        layout.addWidget(nav_group)

        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

    def update_page(self):
        if not self.matched_pages:
            self.text_viewer.setPlainText("No matches found.")
            self.page_label.setText("Page: N/A")
            return

        page_num = self.matched_pages[self.current_index]
        page = self.reader.pages[page_num]
        text = page.extract_text() or ""

        self.highlight_text(text, self.term_sets)
        self.page_label.setText(f"Page: {page_num + 1}")

        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.matched_pages) - 1)

    def highlight_text(self, text, term_sets):
        self.text_viewer.setPlainText(text)
        cursor = self.text_viewer.textCursor()
        fmt = QtGui.QTextCharFormat()
        fmt.setBackground(QtGui.QColor("yellow"))

        for group in term_sets:
            for term in group:
                if not term.strip():
                    continue
                # PyQt6 migration: Replaced QRegExp with QRegularExpression (QRegExp deprecated in Qt6)
                regex = QtCore.QRegularExpression(r"\b" + QtCore.QRegularExpression.escape(term) + r"\b", QtCore.QRegularExpression.CaseInsensitiveOption)
                it = regex.globalMatch(text)
                while it.hasNext():
                    match = it.next()
                    start = match.capturedStart()
                    end = match.capturedEnd()
                    cursor.setPosition(start)
                    cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
                    cursor.mergeCharFormat(fmt)

    def next_page(self):
        if self.current_index < len(self.matched_pages) - 1:
            self.current_index += 1
            self.update_page()

    def prev_page(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_page()
