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

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabel("Terms Structure")
        self.tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.tree)

        button_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.save_btn.clicked.connect(self.save_json)
        self.cancel_btn.clicked.connect(self.reject)

        self.load_tree()

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

    def load_tree(self):
        self.tree.clear()
        for cat in sorted(self.data.keys()):
            cat_item = QtWidgets.QTreeWidgetItem([cat])
            cat_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, ("category", cat))
            self.tree.addTopLevelItem(cat_item)
            for q in sorted(self.data[cat].keys()):
                q_item = QtWidgets.QTreeWidgetItem([q])
                q_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, ("question", cat, q))
                cat_item.addChild(q_item)
                for i, group in enumerate(self.data[cat][q]):
                    group_item = QtWidgets.QTreeWidgetItem([f"Group {i+1}"])
                    group_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, ("group", cat, q, i))
                    q_item.addChild(group_item)
                    for term in group:
                        term_item = QtWidgets.QTreeWidgetItem([term])
                        term_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, ("term", cat, q, i, term))
                        group_item.addChild(term_item)
        self.tree.expandAll()

    def show_context_menu(self, position):
        item = self.tree.itemAt(position)
        if not item:
            menu = QtWidgets.QMenu()
            add_cat_action = menu.addAction("Add Category")
            add_cat_action.triggered.connect(lambda: self.add_item("category"))
            menu.exec(self.tree.mapToGlobal(position))
            return

        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        menu = QtWidgets.QMenu()
        if data[0] == "category":
            add_q_action = menu.addAction("Add Question")
            add_q_action.triggered.connect(lambda: self.add_item("question", data[1]))
            remove_action = menu.addAction("Remove Category")
            remove_action.triggered.connect(lambda: self.remove_item(data))
        elif data[0] == "question":
            add_g_action = menu.addAction("Add Group")
            add_g_action.triggered.connect(lambda: self.add_item("group", data[1], data[2]))
            remove_action = menu.addAction("Remove Question")
            remove_action.triggered.connect(lambda: self.remove_item(data))
        elif data[0] == "group":
            add_t_action = menu.addAction("Add Term")
            add_t_action.triggered.connect(lambda: self.add_item("term", data[1], data[2], data[3]))
            remove_action = menu.addAction("Remove Group")
            remove_action.triggered.connect(lambda: self.remove_item(data))
        elif data[0] == "term":
            remove_action = menu.addAction("Remove Term")
            remove_action.triggered.connect(lambda: self.remove_item(data))
        menu.exec(self.tree.mapToGlobal(position))

    def add_item(self, type_, *args):
        if type_ == "category":
            name, ok = QtWidgets.QInputDialog.getText(self, "New Category", "Category name:")
            if ok and name.strip():
                name = name.strip()
                if name not in self.data:
                    self.data[name] = {}
                    self.load_tree()
        elif type_ == "question":
            cat = args[0]
            name, ok = QtWidgets.QInputDialog.getText(self, "New Question", "Question text:")
            if ok and name.strip():
                name = name.strip()
                if name not in self.data[cat]:
                    self.data[cat][name] = []
                    self.load_tree()
        elif type_ == "group":
            cat, q = args
            self.data[cat][q].append([])
            self.load_tree()
        elif type_ == "term":
            cat, q, g_idx = args
            term, ok = QtWidgets.QInputDialog.getText(self, "New Term", "Term:")
            if ok and term.strip():
                self.data[cat][q][g_idx].append(term.strip())
                self.load_tree()

    def remove_item(self, data):
        type_ = data[0]
        if type_ == "category":
            cat = data[1]
            if cat in self.data:
                del self.data[cat]
                self.load_tree()
        elif type_ == "question":
            cat, q = data[1], data[2]
            if q in self.data[cat]:
                del self.data[cat][q]
                self.load_tree()
        elif type_ == "group":
            cat, q, g_idx = data[1], data[2], data[3]
            if g_idx < len(self.data[cat][q]):
                del self.data[cat][q][g_idx]
                self.load_tree()
        elif type_ == "term":
            cat, q, g_idx, term = data[1], data[2], data[3], data[4]
            if term in self.data[cat][q][g_idx]:
                self.data[cat][q][g_idx].remove(term)
                self.load_tree()

    def get_current_category(self):
        # Return the first category or None
        if self.data:
            return next(iter(self.data))
        return None
