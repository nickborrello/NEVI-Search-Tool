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
        self.resize(800, 600)
        self.json_path = json_path
        self.start_category = start_category
        self.data = {}

        self.load_json()

        layout = QtWidgets.QVBoxLayout(self)

        cat_layout = QtWidgets.QHBoxLayout()
        self.cat_combo = QtWidgets.QComboBox()
        self.cat_combo.currentTextChanged.connect(self.load_questions)
        self.add_cat_btn = QtWidgets.QPushButton("Add Category")
        self.remove_cat_btn = QtWidgets.QPushButton("Remove Category")
        cat_layout.addWidget(self.cat_combo)
        cat_layout.addWidget(self.add_cat_btn)
        cat_layout.addWidget(self.remove_cat_btn)

        ques_layout = QtWidgets.QVBoxLayout()
        self.question_list = QtWidgets.QListWidget()
        self.add_question_btn = QtWidgets.QPushButton("Add Question")
        self.remove_question_btn = QtWidgets.QPushButton("Remove Question")
        ques_layout.addWidget(self.question_list)
        ques_layout.addWidget(self.add_question_btn)
        ques_layout.addWidget(self.remove_question_btn)

        terms_layout = QtWidgets.QVBoxLayout()
        self.terms_editor = QtWidgets.QPlainTextEdit()
        self.terms_editor.setPlaceholderText("One term group per line, comma-separated.")
        terms_layout.addWidget(QtWidgets.QLabel("Term Groups (CSV per line):"))
        terms_layout.addWidget(self.terms_editor)

        self.save_btn = QtWidgets.QPushButton("Save Changes")

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(ques_layout, 2)
        main_layout.addLayout(terms_layout, 3)
        layout.addLayout(cat_layout)
        layout.addLayout(main_layout)
        layout.addWidget(self.save_btn)

        self.add_cat_btn.clicked.connect(self.add_category)
        self.remove_cat_btn.clicked.connect(self.remove_category)
        self.add_question_btn.clicked.connect(self.add_question)
        self.remove_question_btn.clicked.connect(self.remove_question)
        self.question_list.itemClicked.connect(self.load_terms)
        self.save_btn.clicked.connect(self.save_terms)

        self.load_categories()

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

    def load_categories(self):
        self.cat_combo.blockSignals(True)
        self.cat_combo.clear()
        self.cat_combo.addItems(sorted(self.data.keys()))
        self.cat_combo.blockSignals(False)

        if self.cat_combo.count() > 0:
            if self.start_category and self.start_category in self.data:
                index = self.cat_combo.findText(self.start_category)
                self.cat_combo.setCurrentIndex(index)
            else:
                self.cat_combo.setCurrentIndex(0)
            self.load_questions()

    def load_questions(self):
        self.question_list.clear()
        self.terms_editor.clear()
        cat = self.cat_combo.currentText()
        if cat in self.data:
            self.question_list.addItems(sorted(self.data[cat].keys()))

    def load_terms(self):
        cat = self.cat_combo.currentText()
        item = self.question_list.currentItem()
        if not cat or not item:
            return
        question = item.text()
        groups = self.data[cat][question]
        lines = [", ".join(sorted(group)) for group in groups]
        self.terms_editor.setPlainText("\n".join(lines))

    def save_terms(self):
        cat = self.cat_combo.currentText()
        item = self.question_list.currentItem()
        if not cat or not item:
            return
        question = item.text()
        lines = self.terms_editor.toPlainText().strip().splitlines()
        groups = [[term.strip() for term in sorted(line.split(",")) if term.strip()] for line in lines if line.strip()]
        self.data[cat][question] = groups
        self.save_json()
        QtWidgets.QMessageBox.information(self, "Saved", "Terms saved successfully.")

    def add_category(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "New Category", "Category name:")
        if ok and name.strip():
            name = name.strip()
            if name not in self.data:
                self.data[name] = {}
                self.load_categories()
                self.cat_combo.setCurrentText(name)

    def remove_category(self):
        cat = self.cat_combo.currentText()
        if cat and cat in self.data:
            confirm = QtWidgets.QMessageBox.question(
                self, "Delete Category",
                f"Are you sure you want to delete the entire category '{cat}' and all its questions?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirm == QtWidgets.QMessageBox.Yes:
                del self.data[cat]
                self.load_categories()
                self.save_json()

    def add_question(self):
        cat = self.cat_combo.currentText()
        if not cat:
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "New Question", "Question text:")
        if ok and name.strip():
            name = name.strip()
            if name not in self.data[cat]:
                self.data[cat][name] = []
                self.load_questions()
                self.question_list.setCurrentRow(self.question_list.count() - 1)
    
    def get_current_category(self):
        return self.cat_combo.currentText()

    def remove_question(self):
        cat = self.cat_combo.currentText()
        item = self.question_list.currentItem()
        if cat and item:
            question = item.text()
            confirm = QtWidgets.QMessageBox.question(
                self, "Delete Question",
                f"Are you sure you want to delete the question '{question}' and all its terms?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirm == QtWidgets.QMessageBox.Yes:
                del self.data[cat][question]
                self.load_questions()
                self.terms_editor.clear()
                self.save_json()
