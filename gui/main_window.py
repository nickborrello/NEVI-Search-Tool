from PyQt6 import QtWidgets, QtGui, QtCore
import os
from logic.search_engine import search_pdf_for_terms
from logic.term_loader import load_terms
from gui.reader_window import ReaderWindow
from gui.term_editor_window import TermEditorWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('EV Infrastructure Plan Search Tool')
        self.resize(1000, 700)
        self.setWindowIcon(QtGui.QIcon('assets/wpi_logo.ico'))
        self.terms = {}
        self.selected_file = None
        self.results = {}

        self.setup_ui()
        self.load_terms_file('data/terms.json')

        self.setStyleSheet('''
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
            QComboBox QAbstractItemView { background-color: #3c3c3c; color: #ffffff; selection-background-color: #0078d4; }
            QListWidget { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; border-radius: 4px; }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background-color: #0078d4; color: #ffffff; }
            QListWidget::item:hover { background-color: #555555; }
            QTextEdit { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; border-radius: 4px; padding: 8px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            QGroupBox { font-weight: bold; border: 2px solid #555555; border-radius: 5px; margin-top: 1ex; padding-top: 10px; color: #ffffff; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; color: #ffffff; }
            QLabel { color: #ffffff; }
            QStatusBar { background-color: #3c3c3c; color: #ffffff; border-top: 1px solid #555555; }
        ''')

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        load_action = QtGui.QAction('Load PDF', self)
        load_action.triggered.connect(self.load_pdf)
        file_menu.addAction(load_action)

        # Toolbar
        toolbar = self.addToolBar('Main Toolbar')
        edit_action = QtGui.QAction('Edit Terms', self)
        edit_action.triggered.connect(self.open_terms_editor)
        toolbar.addAction(edit_action)

        # Top section: PDF and Configuration
        top_layout = QtWidgets.QHBoxLayout()

        pdf_group = QtWidgets.QGroupBox('Document')
        pdf_layout = QtWidgets.QVBoxLayout(pdf_group)
        self.file_label = QtWidgets.QLabel('No PDF loaded')
        pdf_layout.addWidget(self.file_label)
        top_layout.addWidget(pdf_group)

        config_group = QtWidgets.QGroupBox('Search Configuration')
        config_layout = QtWidgets.QVBoxLayout(config_group)
        cat_layout = QtWidgets.QHBoxLayout()
        cat_layout.addWidget(QtWidgets.QLabel('Category:'))
        self.category_combo = QtWidgets.QComboBox()
        cat_layout.addWidget(self.category_combo)
        config_layout.addLayout(cat_layout)
        config_layout.addWidget(QtWidgets.QLabel('Question:'))
        self.question_list = QtWidgets.QListWidget()
        config_layout.addWidget(self.question_list)
        
        # Fuzzy matching options
        fuzzy_layout = QtWidgets.QHBoxLayout()
        self.fuzzy_checkbox = QtWidgets.QCheckBox('Enable Fuzzy Matching')
        fuzzy_layout.addWidget(self.fuzzy_checkbox)
        fuzzy_layout.addWidget(QtWidgets.QLabel('Threshold:'))
        self.fuzzy_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.fuzzy_slider.setRange(50, 100)
        self.fuzzy_slider.setValue(80)
        fuzzy_layout.addWidget(self.fuzzy_slider)
        config_layout.addLayout(fuzzy_layout)
        
        top_layout.addWidget(config_group)

        layout.addLayout(top_layout)

        # Search button
        self.search_button = QtWidgets.QPushButton('🔍 Run Search')
        self.search_button.clicked.connect(self.run_search)
        layout.addWidget(self.search_button)

        # Results section
        results_group = QtWidgets.QGroupBox('Search Results')
        results_layout = QtWidgets.QVBoxLayout(results_group)
        self.results_list = QtWidgets.QListWidget()
        self.results_list.itemDoubleClicked.connect(self.open_page)
        results_layout.addWidget(self.results_list)
        layout.addWidget(results_group)

        self.statusBar().showMessage('Ready')

    def load_pdf(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open PDF', 'plans', 'PDF Files (*.pdf)')
        if fname:
            self.selected_file = fname
            self.file_label.setText(f'Loaded: {os.path.basename(fname)}')
            self.statusBar().showMessage(f'Loaded PDF: {os.path.basename(fname)}')

    def load_terms_file(self, fname):
        self.terms = load_terms(fname)
        self.category_combo.clear()
        self.category_combo.addItems(self.terms.keys())
        self.category_combo.currentTextChanged.connect(self.update_questions)

    def update_questions(self):
        category = self.category_combo.currentText()
        self.question_list.clear()
        if category in self.terms:
            self.question_list.addItems(self.terms[category].keys())

    def open_terms_editor(self):
        current_cat = self.category_combo.currentText()
        editor = TermEditorWindow('data/terms.json', start_category=current_cat)
        editor.exec()
        self.load_terms_file('data/terms.json')

    def run_search(self):
        if not self.selected_file:
            QtWidgets.QMessageBox.warning(self, 'No File', 'Please load a PDF file.')
            return

        category = self.category_combo.currentText()
        question_item = self.question_list.currentItem()
        if not category or not question_item:
            QtWidgets.QMessageBox.warning(self, 'Incomplete Selection', 'Please select a category and a question.')
            return

        question = question_item.text()
        term_sets = self.terms[category][question]
        self.results = search_pdf_for_terms(self.selected_file, term_sets, self.fuzzy_checkbox.isChecked(), self.fuzzy_slider.value())

        self.results_list.clear()
        if not self.results:
            self.results_list.addItem('No matches found.')
        else:
            for page in sorted(self.results.keys()):
                self.results_list.addItem(f'Page {page + 1}: {len(self.results[page])} matches')

        self.statusBar().showMessage(f'Search completed. Found matches on {len(self.results)} pages.')

    def open_page(self, item):
        if not self.results:
            return
        text = item.text()
        if 'Page' in text:
            page_part = text.split(':')[0]
            page_num = int(page_part.split()[1]) - 1
            if page_num in self.results:
                category = self.category_combo.currentText()
                question = self.question_list.currentItem().text()
                term_sets = self.terms[category][question]
                self.reader = ReaderWindow(self.selected_file, list(self.results.keys()), term_sets)
                self.reader.current_index = list(self.results.keys()).index(page_num)
                self.reader.show()
