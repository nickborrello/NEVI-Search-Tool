from PyQt6 import QtWidgets, QtGui, QtCore
import os
from logic.search_engine import search_pdf_for_terms
from logic.term_loader import load_terms
from gui.reader_window import ReaderWindow
from gui.term_editor_window import TermEditorWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal PDF Keyword Search")
        self.resize(1200, 800)
        self.setWindowIcon(QtGui.QIcon("assets/wpi_logo.ico"))  # Assuming icon exists
        self.terms = {}
        self.selected_file = None

        self.setup_ui()
        self.load_terms_file("data/terms.json")

        # Apply dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            QMenuBar { background-color: #3c3c3c; color: #ffffff; border-bottom: 1px solid #555555; }
            QMenuBar::item { background-color: transparent; padding: 4px 8px; }
            QMenuBar::item:selected { background-color: #0078d4; }
            QMenu { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; }
            QMenu::item:selected { background-color: #0078d4; }
            QToolBar { background-color: #3c3c3c; border-bottom: 1px solid #555555; }
            QToolBar QToolButton { background-color: #0078d4; color: #ffffff; border: none; padding: 6px; border-radius: 4px; font-weight: bold; }
            QToolBar QToolButton:hover { background-color: #106ebe; }
            QToolBar QToolButton:pressed { background-color: #005a9e; }
            QPushButton { background-color: #0078d4; color: #ffffff; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
            QPushButton:disabled { background-color: #555555; color: #aaaaaa; }
            QComboBox { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; padding: 4px; border-radius: 4px; }
            QComboBox:hover { border-color: #0078d4; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: url(down_arrow.png); }  /* Placeholder */
            QComboBox QAbstractItemView { background-color: #3c3c3c; color: #ffffff; selection-background-color: #0078d4; }
            QListWidget { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; border-radius: 4px; }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background-color: #0078d4; color: #ffffff; }
            QListWidget::item:hover { background-color: #555555; }
            QTextEdit { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; border-radius: 4px; padding: 8px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            QStatusBar { background-color: #3c3c3c; color: #ffffff; border-top: 1px solid #555555; }
        """)

    def setup_ui(self):
        # Menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        load_action = QtGui.QAction("📁 Load PDF", self)
        load_action.triggered.connect(self.load_pdf)
        file_menu.addAction(load_action)

        # Toolbar
        toolbar = self.addToolBar("Main Toolbar")
        edit_action = QtGui.QAction("⚙️ Edit Terms", self)
        edit_action.triggered.connect(self.open_terms_editor)
        toolbar.addAction(edit_action)
        search_action = QtGui.QAction("🔍 Run Search", self)
        search_action.triggered.connect(self.run_search)
        toolbar.addAction(search_action)

        # Central widget with splitter
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # Left panel: Configuration
        config_group = QtWidgets.QGroupBox("Search Configuration")
        config_layout = QtWidgets.QVBoxLayout(config_group)

        cat_layout = QtWidgets.QHBoxLayout()
        cat_layout.addWidget(QtWidgets.QLabel("Category:"))
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.setToolTip("Select a category of search terms")
        cat_layout.addWidget(self.category_combo)
        config_layout.addLayout(cat_layout)

        config_layout.addWidget(QtWidgets.QLabel("Question:"))
        self.term_list = QtWidgets.QListWidget()
        self.term_list.setToolTip("Select a question to define the keywords to search for")
        config_layout.addWidget(self.term_list)

        main_layout.addWidget(config_group, 1)

        # Right panel: Term Preview
        preview_group = QtWidgets.QGroupBox("Selected Search Terms")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        self.terms_preview = QtWidgets.QTextEdit()
        self.terms_preview.setReadOnly(True)
        self.terms_preview.setPlaceholderText("Select a category and question to preview the search terms here.")
        self.terms_preview.setMaximumHeight(300)
        preview_layout.addWidget(self.terms_preview)
        main_layout.addWidget(preview_group, 1)

        # Status bar
        self.statusBar().showMessage("Ready")

    def load_pdf(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open PDF", "plans", "PDF Files (*.pdf)")
        if fname:
            self.selected_file = fname
            self.statusBar().showMessage(f"Loaded PDF: {os.path.basename(fname)}")
        else:
            self.statusBar().showMessage("No PDF loaded")

    def load_terms_file(self, fname):
        self.terms = load_terms(fname)
        self.category_combo.clear()
        self.category_combo.addItems(self.terms.keys())
        self.category_combo.currentTextChanged.connect(self.update_term_list)
        self.term_list.currentItemChanged.connect(self.update_terms_preview)
        self.update_term_list()

    def update_terms_preview(self):
        category = self.category_combo.currentText()
        question_item = self.term_list.currentItem()
        if category in self.terms and question_item:
            question = question_item.text()
            if question in self.terms[category]:
                term_sets = self.terms[category][question]
                preview_text = f"Category: {category}\nQuestion: {question}\n\nSearch Terms:\n"
                for i, group in enumerate(term_sets, 1):
                    preview_text += f"Group {i}: {', '.join(group)}\n"
                self.terms_preview.setPlainText(preview_text)
            else:
                self.terms_preview.setPlainText("No terms found for selected question.")
        else:
            self.terms_preview.setPlainText("Select a category and question to preview the search terms here.")

    def open_terms_editor(self):
        current_cat = self.category_combo.currentText()
        editor = TermEditorWindow("data/terms.json", start_category=current_cat)
        editor.exec()
        self.load_terms_file("data/terms.json")

    def run_search(self):
        if not self.selected_file:
            QtWidgets.QMessageBox.warning(self, "No File", "Please load a PDF file.")
            return

        category = self.category_combo.currentText()
        question_item = self.term_list.currentItem()
        if not category or not question_item:
            QtWidgets.QMessageBox.warning(self, "Incomplete Selection", "Please select a category and a question.")
            return

        question = question_item.text()
        term_sets = self.terms[category][question]
        results = search_pdf_for_terms(self.selected_file, term_sets)

        if not results:
            QtWidgets.QMessageBox.information(self, "No Results", "No matches found.")
        else:
            self.reader = ReaderWindow(self.selected_file, list(results.keys()), term_sets)
            self.reader.show()
