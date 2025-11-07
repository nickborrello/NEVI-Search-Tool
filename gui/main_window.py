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
        self.resize(1000, 700)
        self.setWindowIcon(QtGui.QIcon("assets/wpi_logo.ico"))  # Assuming icon exists
        self.terms = {}
        self.selected_file = None

        self.setup_ui()
        self.load_terms_file("data/terms.json")

        # Apply professional stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            QPushButton { background-color: #0078d4; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
            QComboBox { background-color: white; border: 1px solid #cccccc; padding: 4px; border-radius: 4px; }
            QComboBox:hover { border-color: #0078d4; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: url(down_arrow.png); }  /* Placeholder */
            QListWidget { background-color: white; border: 1px solid #cccccc; border-radius: 4px; }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background-color: #0078d4; color: white; }
            QGroupBox { font-weight: bold; border: 2px solid #cccccc; border-radius: 5px; margin-top: 1ex; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; color: #333333; }
            QLabel { color: #333333; }
        """)

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # PDF Loading Section
        pdf_group = QtWidgets.QGroupBox("PDF Document")
        pdf_layout = QtWidgets.QVBoxLayout(pdf_group)
        self.file_button = QtWidgets.QPushButton("📁 Load PDF")
        self.file_button.setToolTip("Select a PDF file to search")
        self.file_button.clicked.connect(self.load_pdf)
        pdf_layout.addWidget(self.file_button)
        layout.addWidget(pdf_group)

        # Terms Selection Section
        terms_group = QtWidgets.QGroupBox("Search Configuration")
        terms_layout = QtWidgets.QVBoxLayout(terms_group)

        cat_layout = QtWidgets.QHBoxLayout()
        cat_layout.addWidget(QtWidgets.QLabel("Category:"))
        self.category_combo = QtWidgets.QComboBox()
        cat_layout.addWidget(self.category_combo)
        terms_layout.addLayout(cat_layout)

        terms_layout.addWidget(QtWidgets.QLabel("Questions:"))
        self.term_list = QtWidgets.QListWidget()
        self.term_list.setMaximumHeight(200)
        terms_layout.addWidget(self.term_list)

        self.editTermsButton = QtWidgets.QPushButton("⚙️ Edit Terms")
        self.editTermsButton.setToolTip("Open term configuration editor")
        self.editTermsButton.clicked.connect(self.open_terms_editor)
        terms_layout.addWidget(self.editTermsButton)

        layout.addWidget(terms_group)

        # Action Section
        action_group = QtWidgets.QGroupBox("Actions")
        action_layout = QtWidgets.QVBoxLayout(action_group)
        self.search_button = QtWidgets.QPushButton("🔍 Run Search")
        self.search_button.setToolTip("Execute search on the loaded PDF")
        self.search_button.clicked.connect(self.run_search)
        action_layout.addWidget(self.search_button)
        layout.addWidget(action_group)

        # Status bar
        self.statusBar().showMessage("Ready")

    def load_pdf(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open PDF", "plans", "PDF Files (*.pdf)")
        if fname:
            self.selected_file = fname
            self.statusBar().showMessage(f"Loaded PDF: {os.path.basename(fname)}")

    def load_terms_file(self, fname):
        self.terms = load_terms(fname)
        self.category_combo.clear()
        self.category_combo.addItems(self.terms.keys())
        self.category_combo.currentTextChanged.connect(self.update_term_list)
        self.update_term_list()

    def update_term_list(self):
        category = self.category_combo.currentText()
        self.term_list.clear()
        if category in self.terms:
            self.term_list.addItems(self.terms[category].keys())

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
