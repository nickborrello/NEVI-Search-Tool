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
        self.terms = {}
        self.selected_file = None

        self.setup_ui()
        self.load_terms_file("data/terms.json")

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.file_button = QtWidgets.QPushButton("Load PDF")
        self.file_button.clicked.connect(self.load_pdf)
        layout.addWidget(self.file_button)

        self.category_combo = QtWidgets.QComboBox()
        layout.addWidget(self.category_combo)

        self.term_list = QtWidgets.QListWidget()
        layout.addWidget(self.term_list)

        self.editTermsButton = QtWidgets.QPushButton("Edit Terms")
        self.editTermsButton.clicked.connect(self.open_terms_editor)
        layout.addWidget(self.editTermsButton)

        self.search_button = QtWidgets.QPushButton("Run Search")
        self.search_button.clicked.connect(self.run_search)
        layout.addWidget(self.search_button)

    def load_pdf(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
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
        editor.exec_()
        new_cat = editor.get_current_category()
        self.load_terms_file("data/terms.json")
        if new_cat in self.terms:
            index = self.category_combo.findText(new_cat)
            self.category_combo.setCurrentIndex(index)

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
