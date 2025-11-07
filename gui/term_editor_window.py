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
        self.setWindowTitle("JSON Term Editor")
        self.resize(800, 600)
        self.json_path = json_path
        self.start_category = start_category

        layout = QtWidgets.QVBoxLayout(self)

        self.text_editor = QtWidgets.QPlainTextEdit()
        self.text_editor.setFont(QtGui.QFont("Courier New", 10))
        layout.addWidget(self.text_editor)

        button_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.save_btn.clicked.connect(self.save_json)
        self.cancel_btn.clicked.connect(self.reject)

        self.load_json()

    def load_json(self):
        path = resource_path(self.json_path)
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
            self.text_editor.setPlainText(content)
        else:
            self.text_editor.setPlainText("{}")

    def save_json(self):
        try:
            content = self.text_editor.toPlainText()
            data = json.loads(content)
            # Basic validation: ensure it's a dict of dicts
            if not isinstance(data, dict):
                raise ValueError("Root must be an object")
            for cat, questions in data.items():
                if not isinstance(questions, dict):
                    raise ValueError(f"Category '{cat}' must be an object")
                for q, groups in questions.items():
                    if not isinstance(groups, list):
                        raise ValueError(f"Question '{q}' in '{cat}' must be a list")
                    for group in groups:
                        if not isinstance(group, list) or not all(isinstance(term, str) for term in group):
                            raise ValueError(f"Each group in '{q}' must be a list of strings")
            # Save
            save_path = os.path.join(os.getcwd(), "data", "terms.json")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w") as f:
                json.dump(data, f, indent=2)
            QtWidgets.QMessageBox.information(self, "Saved", "Terms saved successfully.")
            self.accept()
        except json.JSONDecodeError as e:
            QtWidgets.QMessageBox.warning(self, "Invalid JSON", f"JSON error: {e}")
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Invalid Structure", f"Structure error: {e}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Save failed: {e}")

    def get_current_category(self):
        # Since it's JSON editor, return None or something; main_window can handle
        return None
