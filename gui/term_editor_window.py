from PyQt6 import QtWidgets, QtGui, QtCore
import json
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

class TermEditorWindow(QtWidgets.QDialog):
    def __init__(self, json_path="data/terms.json", start_category=None):
        super().__init__()
        self.setWindowTitle("Term Editor")
        self.resize(1000, 600)
        self.json_path = json_path
        self.start_category = start_category
        self.data = {}

        self.load_json()

        layout = QtWidgets.QVBoxLayout(self)

        # Top: Categories
        cat_layout = QtWidgets.QHBoxLayout()
        cat_layout.addWidget(QtWidgets.QLabel("Categories:"))
        self.cat_list = QtWidgets.QListWidget()
        self.cat_list.currentItemChanged.connect(self.on_category_changed)
        cat_layout.addWidget(self.cat_list)
        cat_btn_layout = QtWidgets.QVBoxLayout()
        add_cat_btn = QtWidgets.QPushButton("Add")
        add_cat_btn.clicked.connect(self.add_category)
        remove_cat_btn = QtWidgets.QPushButton("Remove")
        remove_cat_btn.clicked.connect(self.remove_category)
        cat_btn_layout.addWidget(add_cat_btn)
        cat_btn_layout.addWidget(remove_cat_btn)
        cat_btn_layout.addStretch()
        cat_layout.addLayout(cat_btn_layout)
        layout.addLayout(cat_layout)

        # Middle: Questions
        q_layout = QtWidgets.QHBoxLayout()
        q_layout.addWidget(QtWidgets.QLabel("Questions:"))
        self.q_list = QtWidgets.QListWidget()
        self.q_list.currentItemChanged.connect(self.on_question_changed)
        q_layout.addWidget(self.q_list)
        q_btn_layout = QtWidgets.QVBoxLayout()
        add_q_btn = QtWidgets.QPushButton("Add")
        add_q_btn.clicked.connect(self.add_question)
        remove_q_btn = QtWidgets.QPushButton("Remove")
        remove_q_btn.clicked.connect(self.remove_question)
        q_btn_layout.addWidget(add_q_btn)
        q_btn_layout.addWidget(remove_q_btn)
        q_btn_layout.addStretch()
        q_layout.addLayout(q_btn_layout)
        layout.addLayout(q_layout)

        # Bottom: Terms
        terms_layout = QtWidgets.QHBoxLayout()
        terms_layout.addWidget(QtWidgets.QLabel("Term Groups (one per line, comma-separated):"))
        self.terms_edit = QtWidgets.QPlainTextEdit()
        self.terms_edit.setPlaceholderText("e.g.\nterm1, term2\nterm3")
        terms_layout.addWidget(self.terms_edit)
        terms_btn_layout = QtWidgets.QVBoxLayout()
        save_terms_btn = QtWidgets.QPushButton("Save Terms")
        save_terms_btn.clicked.connect(self.save_terms)
        terms_btn_layout.addWidget(save_terms_btn)
        terms_btn_layout.addStretch()
        terms_layout.addLayout(terms_btn_layout)
        layout.addLayout(terms_layout)

        # Bottom buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save All")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.save_btn.clicked.connect(self.save_json)
        self.cancel_btn.clicked.connect(self.reject)

        self.load_ui()

    def load_json(self):
        path = resource_path(self.json_path)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save_json(self):
        save_path = os.path.join(os.getcwd(), "data", "terms.json")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(self.data, f, indent=2)
        QtWidgets.QMessageBox.information(self, "Saved", "Terms saved successfully.")
        self.accept()

    def load_ui(self):
        self.cat_list.clear()
        for cat in sorted(self.data.keys()):
            self.cat_list.addItem(cat)
        if self.start_category and self.start_category in self.data:
            index = self.cat_list.findItems(self.start_category, QtCore.Qt.MatchFlag.MatchExactly)
            if index:
                self.cat_list.setCurrentItem(index[0])

    def on_category_changed(self, current, previous):
        self.q_list.clear()
        self.terms_edit.clear()
        if current:
            cat = current.text()
            if cat in self.data:
                for q in sorted(self.data[cat].keys()):
                    self.q_list.addItem(q)

    def on_question_changed(self, current, previous):
        self.terms_edit.clear()
        if current:
            cat = self.cat_list.currentItem().text()
            q = current.text()
            if cat in self.data and q in self.data[cat]:
                groups = self.data[cat][q]
                lines = ["\n".join(sorted(group)) for group in groups]
                self.terms_edit.setPlainText("\n\n".join(lines))

    def add_category(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Category", "Category name:")
        if ok and name.strip():
            name = name.strip()
            if name not in self.data:
                self.data[name] = {}
                self.load_ui()

    def remove_category(self):
        current = self.cat_list.currentItem()
        if current:
            cat = current.text()
            confirm = QtWidgets.QMessageBox.question(self, "Remove Category", f"Remove '{cat}' and all its questions?")
            if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
                del self.data[cat]
                self.load_ui()

    def add_question(self):
        current_cat = self.cat_list.currentItem()
        if not current_cat:
            QtWidgets.QMessageBox.warning(self, "No Category", "Select a category first.")
            return
        cat = current_cat.text()
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Question", "Question text:")
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
            confirm = QtWidgets.QMessageBox.question(self, "Remove Question", f"Remove '{q}' and all its terms?")
            if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
                del self.data[cat][q]
                self.on_category_changed(current_cat, None)

    def save_terms(self):
        current_cat = self.cat_list.currentItem()
        current_q = self.q_list.currentItem()
        if not current_cat or not current_q:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Select a category and question.")
            return
        cat = current_cat.text()
        q = current_q.text()
        text = self.terms_edit.toPlainText()
        groups = []
        for block in text.split("\n\n"):
            group = [term.strip() for term in block.split("\n") if term.strip()]
            if group:
                groups.append(group)
        self.data[cat][q] = groups
        QtWidgets.QMessageBox.information(self, "Saved", "Terms updated.")

    def get_current_category(self):
        current = self.cat_list.currentItem()
        return current.text() if current else None
