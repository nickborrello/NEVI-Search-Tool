from PyQt6 import QtWidgets, QtGui, QtCore
import os
from logic.search_engine import search_pdf_for_terms, semantic_search_pdf
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
        
        # Search mode options
        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.addWidget(QtWidgets.QLabel('Search Mode:'))
        radio_layout = QtWidgets.QHBoxLayout()
        self.exact_radio = QtWidgets.QRadioButton('Exact')
        self.exact_radio.setChecked(True)
        radio_layout.addWidget(self.exact_radio)
        self.fuzzy_radio = QtWidgets.QRadioButton('Fuzzy')
        radio_layout.addWidget(self.fuzzy_radio)
        self.semantic_radio = QtWidgets.QRadioButton('Semantic')
        self.semantic_radio.setEnabled(False)  # Disabled due to torch issues
        radio_layout.addWidget(self.semantic_radio)
        mode_layout.addLayout(radio_layout)
        
        threshold_layout = QtWidgets.QHBoxLayout()
        threshold_layout.addWidget(QtWidgets.QLabel('Threshold:'))
        self.threshold_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(50, 100)
        self.threshold_slider.setValue(80)
        self.threshold_slider.setEnabled(False)
        threshold_layout.addWidget(self.threshold_slider)
        mode_layout.addLayout(threshold_layout)
        
        config_layout.addLayout(mode_layout)
        
        # NLP preprocessing
        self.preprocessing_checkbox = QtWidgets.QCheckBox('Enable NLP Preprocessing')
        config_layout.addWidget(self.preprocessing_checkbox)
        
        # Connect mode change
        self.exact_radio.toggled.connect(self.on_mode_changed)
        self.fuzzy_radio.toggled.connect(self.on_mode_changed)
        self.semantic_radio.toggled.connect(self.on_mode_changed)
        
        top_layout.addWidget(config_group)

        layout.addLayout(top_layout)

        # Search button
        self.search_button = QtWidgets.QPushButton('🔍 Run Search')
        self.search_button.clicked.connect(self.run_search)
        layout.addWidget(self.search_button)

        # Results section
        results_group = QtWidgets.QGroupBox('Search Results')
        results_layout = QtWidgets.QVBoxLayout(results_group)
        self.results_label = QtWidgets.QLabel('No search performed yet.')
        results_layout.addWidget(self.results_label)
        self.view_button = QtWidgets.QPushButton('View Results')
        self.view_button.clicked.connect(self.view_results)
        self.view_button.setEnabled(False)
        results_layout.addWidget(self.view_button)
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

    def on_mode_changed(self):
        enabled = self.fuzzy_radio.isChecked() or self.semantic_radio.isChecked()
        self.threshold_slider.setEnabled(enabled)

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
        
        use_preprocessing = self.preprocessing_checkbox.isChecked()
        
        if self.exact_radio.isChecked():
            self.results = search_pdf_for_terms(self.selected_file, term_sets, False, 80, use_preprocessing)
        elif self.fuzzy_radio.isChecked():
            threshold = self.threshold_slider.value()
            self.results = search_pdf_for_terms(self.selected_file, term_sets, True, threshold, use_preprocessing)
        else:  # semantic
            threshold = self.threshold_slider.value() / 100.0  # 0.5 to 1.0
            self.results = semantic_search_pdf(self.selected_file, term_sets, threshold)

        if not self.results:
            self.results_label.setText('No matches found.')
            self.view_button.setEnabled(False)
        else:
            num_pages = len(self.results)
            self.results_label.setText(f'Found matches on {num_pages} pages.')
            self.view_button.setEnabled(True)

        self.statusBar().showMessage(f'Search completed. Found matches on {len(self.results)} pages.')

    def view_results(self):
        if self.results:
            category = self.category_combo.currentText()
            question = self.question_list.currentItem().text()
            term_sets = self.terms[category][question]
            self.reader = ReaderWindow(self.selected_file, list(self.results.keys()), term_sets)
            self.reader.show()
