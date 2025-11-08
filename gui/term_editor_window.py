from PyQt6 import QtWidgets, QtGui, QtCore
import json
import os

class TermEditorWindow(QtWidgets.QDialog):
    def __init__(self, json_path='data/terms.json', start_category=None):
        super().__init__()
        self.setWindowTitle('Advanced Term Configuration')
        self.resize(1200, 700)
        self.setWindowIcon(QtGui.QIcon('assets/wpi_logo.ico'))
        self.json_path = json_path
        self.start_category = start_category
        self.data = {}

        self.load_json()

        self.setup_ui()

        self.setStyleSheet('''
            QDialog { background-color: #2b2b2b; color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            QGroupBox { font-weight: bold; border: 2px solid #555555; border-radius: 5px; margin-top: 1ex; color: #ffffff; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; color: #ffffff; }
            QListWidget { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; border-radius: 4px; }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background-color: #0078d4; color: #ffffff; }
            QListWidget::item:hover { background-color: #555555; }
            QTableWidget { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; border-radius: 4px; gridline-color: #555555; }
            QTableWidget::item { padding: 4px; }
            QPushButton { background-color: #0078d4; color: #ffffff; border: none; padding: 6px 12px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
            QPushButton:disabled { background-color: #555555; color: #aaaaaa; }
            QLabel { color: #ffffff; }
            QInputDialog { background-color: #2b2b2b; color: #ffffff; }
            QMessageBox { background-color: #2b2b2b; color: #ffffff; }
        ''')

        self.load_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Categories
        cat_group = QtWidgets.QGroupBox('Categories')
        cat_layout = QtWidgets.QVBoxLayout(cat_group)
        self.cat_list = QtWidgets.QListWidget()
        self.cat_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.cat_list.currentItemChanged.connect(self.on_category_changed)
        cat_layout.addWidget(self.cat_list)
        cat_btn_layout = QtWidgets.QHBoxLayout()
        add_cat_btn = QtWidgets.QPushButton('➕ Add Category')
        add_cat_btn.clicked.connect(self.add_category)
        remove_cat_btn = QtWidgets.QPushButton('➖ Remove Category')
        remove_cat_btn.clicked.connect(self.remove_category)
        cat_btn_layout.addWidget(add_cat_btn)
        cat_btn_layout.addWidget(remove_cat_btn)
        cat_layout.addLayout(cat_btn_layout)
        layout.addWidget(cat_group)

        # Questions
        q_group = QtWidgets.QGroupBox('Questions')
        q_layout = QtWidgets.QVBoxLayout(q_group)
        self.q_list = QtWidgets.QListWidget()
        self.q_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.q_list.currentItemChanged.connect(self.on_question_changed)
        q_layout.addWidget(self.q_list)
        q_btn_layout = QtWidgets.QHBoxLayout()
        add_q_btn = QtWidgets.QPushButton('➕ Add Question')
        add_q_btn.clicked.connect(self.add_question)
        remove_q_btn = QtWidgets.QPushButton('➖ Remove Question')
        remove_q_btn.clicked.connect(self.remove_question)
        q_btn_layout.addWidget(add_q_btn)
        q_btn_layout.addWidget(remove_q_btn)
        q_layout.addLayout(q_btn_layout)
        layout.addWidget(q_group)

        # Terms
        terms_group = QtWidgets.QGroupBox('Term Groups')
        terms_layout = QtWidgets.QVBoxLayout(terms_group)
        self.terms_table = QtWidgets.QTableWidget()
        self.terms_table.setColumnCount(2)
        self.terms_table.setHorizontalHeaderLabels(['Group', 'Terms (comma-separated)'])
        self.terms_table.horizontalHeader().setStretchLastSection(True)
        self.terms_table.setAlternatingRowColors(True)
        terms_layout.addWidget(self.terms_table)
        terms_btn_layout = QtWidgets.QHBoxLayout()
        add_group_btn = QtWidgets.QPushButton('➕ Add Group')
        add_group_btn.clicked.connect(self.add_group)
        remove_group_btn = QtWidgets.QPushButton('➖ Remove Group')
        remove_group_btn.clicked.connect(self.remove_group)
        save_terms_btn = QtWidgets.QPushButton('💾 Save Changes')
        save_terms_btn.clicked.connect(self.save_terms)
        terms_btn_layout.addWidget(add_group_btn)
        terms_btn_layout.addWidget(remove_group_btn)
        terms_btn_layout.addStretch()
        terms_btn_layout.addWidget(save_terms_btn)
        terms_layout.addLayout(terms_btn_layout)
        layout.addWidget(terms_group)

        # Bottom buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton('💾 Save All & Close')
        self.cancel_btn = QtWidgets.QPushButton('❌ Cancel')
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.save_btn.clicked.connect(self.save_json)
        self.cancel_btn.clicked.connect(self.reject)

    def load_json(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save_json(self):
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        with open(self.json_path, 'w') as f:
            json.dump(self.data, f, indent=2)
        QtWidgets.QMessageBox.information(self, 'Success', 'All term configurations saved successfully.')
        self.accept()

    def load_ui(self):
        self.cat_list.clear()
        for cat in sorted(self.data.keys()):
            item = QtWidgets.QListWidgetItem(cat)
            self.cat_list.addItem(item)
        if self.start_category and self.start_category in self.data:
            items = self.cat_list.findItems(self.start_category, QtCore.Qt.MatchFlag.MatchExactly)
            if items:
                self.cat_list.setCurrentItem(items[0])

    def on_category_changed(self, current, previous):
        self.q_list.clear()
        self.terms_table.setRowCount(0)
        if current:
            cat = current.text()
            if cat in self.data:
                for q in sorted(self.data[cat].keys()):
                    item = QtWidgets.QListWidgetItem(q)
                    self.q_list.addItem(item)

    def on_question_changed(self, current, previous):
        self.terms_table.setRowCount(0)
        if current:
            cat = self.cat_list.currentItem().text()
            q = current.text()
            if cat in self.data and q in self.data[cat]:
                groups = self.data[cat][q]
                self.terms_table.setRowCount(len(groups))
                for i, group in enumerate(groups):
                    self.terms_table.setItem(i, 0, QtWidgets.QTableWidgetItem(f'Group {i+1}'))
                    self.terms_table.setItem(i, 1, QtWidgets.QTableWidgetItem(', '.join(sorted(group))))

    def add_category(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'Add Category', 'Enter category name:')
        if ok and name.strip():
            name = name.strip()
            if name not in self.data:
                self.data[name] = {}
                self.load_ui()

    def remove_category(self):
        current = self.cat_list.currentItem()
        if current:
            cat = current.text()
            reply = QtWidgets.QMessageBox.question(self, 'Confirm Removal', f'Remove category \'{cat}\' and all its contents?',
                                                   QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                del self.data[cat]
                self.load_ui()

    def add_question(self):
        current_cat = self.cat_list.currentItem()
        if not current_cat:
            QtWidgets.QMessageBox.warning(self, 'Selection Required', 'Please select a category first.')
            return
        cat = current_cat.text()
        name, ok = QtWidgets.QInputDialog.getText(self, 'Add Question', 'Enter question text:')
        if ok and name.strip():
            name = name.strip()
            if name not in self.data[cat]:
                self.data[cat][name] = []
                self.on_category_changed(current_cat, None)

    def remove_question(self):
        current_cat = self.cat_list.currentItem()
        current_q = self.q_list.currentItem()
        if current_cat and current_q:
            cat = current_cat.text()
            q = current_q.text()
            reply = QtWidgets.QMessageBox.question(self, 'Confirm Removal', f'Remove question \'{q}\' and all its terms?',
                                                   QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                del self.data[cat][q]
                self.on_category_changed(current_cat, None)

    def add_group(self):
        current_cat = self.cat_list.currentItem()
        current_q = self.q_list.currentItem()
        if not current_cat or not current_q:
            QtWidgets.QMessageBox.warning(self, 'Selection Required', 'Please select a category and question first.')
            return
        cat = current_cat.text()
        q = current_q.text()
        self.data[cat][q].append([])
        self.on_question_changed(current_q, None)

    def remove_group(self):
        current_cat = self.cat_list.currentItem()
        current_q = self.q_list.currentItem()
        if not current_cat or not current_q:
            QtWidgets.QMessageBox.warning(self, 'Selection Required', 'Please select a category and question first.')
            return
        cat = current_cat.text()
        q = current_q.text()
        row = self.terms_table.currentRow()
        if row >= 0 and row < len(self.data[cat][q]):
            reply = QtWidgets.QMessageBox.question(self, 'Confirm Removal', f'Remove group {row+1}?',
                                                   QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                del self.data[cat][q][row]
                self.on_question_changed(current_q, None)

    def save_terms(self):
        current_cat = self.cat_list.currentItem()
        current_q = self.q_list.currentItem()
        if not current_cat or not current_q:
            QtWidgets.QMessageBox.warning(self, 'Selection Required', 'Please select a category and question first.')
            return
        cat = current_cat.text()
        q = current_q.text()
        groups = []
        for row in range(self.terms_table.rowCount()):
            terms_text = self.terms_table.item(row, 1).text() if self.terms_table.item(row, 1) else ''
            terms = [term.strip() for term in terms_text.split(',') if term.strip()]
            groups.append(terms)
        self.data[cat][q] = groups
        QtWidgets.QMessageBox.information(self, 'Success', 'Term groups updated.')

    def get_current_category(self):
        current = self.cat_list.currentItem()
        return current.text() if current else None
