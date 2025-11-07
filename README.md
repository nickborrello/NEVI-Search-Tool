# NEVI Plan Keyword Search Tool

[![Sponsored by Atlas Public Policy](https://img.shields.io/badge/Sponsored_by-Atlas_Public_Policy-blue)](https://www.atlaspolicy.com/)

A Python-based tool to help analysts and researchers search through state NEVI plans for structured answers to key questions. The tool uses logic-based keyword matching to find pages that discuss specific topics in uploaded PDF documents.

Originally developed for a WPI undergraduate research initiative, **sponsored by Atlas Public Policy**.

---

## 📄 What It Does

- Load any state NEVI plan (PDF)
- Choose a category (e.g., Equity, Buildout, Maintenance)
- Choose a question
- Search for structured keyword matches
- View matching pages in a built-in reader with highlights
- Edit the term sets with an easy-to-use term editor

---

## 🧱 Project Structure

```
.
├── main.py                   # Entry point
├── data/
│   └── terms.json             # Questions and keyword groups
├── assets/
│   └── wpi_logo.ico           # App icon
├── gui/
│   ├── main_window.py         # Main application UI
│   ├── reader_window.py       # Highlighted PDF reader
│   └── term_editor_window.py  # JSON term editor
├── logic/
│   ├── search_engine.py       # Whole-word search engine
│   ├── term_loader.py         # Resource path handling
│   └── settings.py            # (reserved for future)
└── README.md
```

---

## ⚙️ Installation (Run Locally)

### Requirements

- Python 3.8+
- PyQt6
- pypdf

### Install dependencies:

```bash
pip install PyQt6 pypdf
```

---

## ▶️ Running the App

From the project root:

```bash
python main.py
```

1. Load a PDF
2. Select a category and question
3. Click "Run Search"
4. Review matching pages with highlighted keywords

---

## 🧠 JSON Term Structure

Each question has grouped terms. A page matches if **at least one word from each group** appears on it.

Example:

```json
{
  "Equity": {
    "How does the state identify disadvantaged communities?": [
      ["underserved", "disadvantaged", "DAC", "marginalized"],
      ["define", "identify", "locate"],
      ["engagement", "collaboration", "mapping tool"]
    ]
  }
}
```

---

## 🧑‍💻 Background

This project was originally developed as part of a WPI undergraduate research initiative in response to the **National Electric Vehicle Infrastructure (NEVI)** program.

The research and tool development were **sponsored by Atlas Public Policy** to assist in accelerating EV adoption and infrastructure analysis.

---

## ✍️ Authors

Developed by Nicholas Borrello  
Supported by WPI faculty and advisors  
Sponsored by Atlas Public Policy
