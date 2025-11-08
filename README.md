# EV Infrastructure Plan Search Tool

[![Sponsored by Atlas Public Policy](https://img.shields.io/badge/Sponsored_by-Atlas_Public_Policy-blue)](https://www.atlaspolicy.com/)

A Python-based tool to help analysts and researchers search through state NEVI plans for structured answers to key questions. The tool uses advanced search modes including exact keyword matching, fuzzy string matching for typos and variations, and semantic similarity (AI-powered) to find pages that discuss specific topics in uploaded PDF documents.

Originally developed for a WPI undergraduate research initiative, **sponsored by Atlas Public Policy**.

---

## 📄 What It Does

- Load any state NEVI plan (PDF)
- Choose a category (e.g., Equity, Buildout, Maintenance)
- Choose a question
- Select search mode: Exact (keyword matching), Fuzzy (approximate matching), or Semantic (AI similarity)
- Adjust similarity threshold for fuzzy/semantic searches
- Enable NLP preprocessing for better text matching
- Search for structured keyword matches
- View matching pages in a built-in reader with highlights
- Edit the term sets with an easy-to-use term editor
- User selections are saved and restored on next run

---

## 🧱 Project Structure

```
.
├── main.py                   # Entry point
├── config.json               # User settings (auto-generated)
├── data/
│   └── terms.json             # Questions and keyword groups
├── assets/
│   └── wpi_logo.ico           # App icon
├── gui/
│   ├── main_window.py         # Main application UI
│   ├── reader_window.py       # Highlighted PDF reader
│   └── term_editor_window.py  # JSON term editor
├── logic/
│   ├── search_engine.py       # Search engine with exact/fuzzy modes
│   ├── term_loader.py         # Resource path handling
│   └── settings.py            # (reserved for future)
└── README.md
```

---

## ⚙️ Installation (Run Locally)

### Requirements

- Python 3.8+
- PyQt6
- PyMuPDF (for PDF processing)
- thefuzz (for fuzzy matching)
- spaCy (for NLP preprocessing)

### Install dependencies:

```bash
pip install PyQt6 PyMuPDF thefuzz spacy
python -m spacy download en_core_web_sm
```

---

## ▶️ Running the App

From the project root:

```bash
python main.py
```

1. Load a PDF
2. Select a category and question
3. Choose search mode (Exact, Fuzzy, or Semantic)
4. Adjust threshold if using Fuzzy/Semantic (higher for stricter matching)
5. Enable NLP preprocessing if desired
6. Click "Run Search"
7. Review matching pages with highlighted keywords

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

## 🔍 Search Modes

- **Exact**: Precise keyword matching with word boundaries. Searches for terms exactly as entered.
- **Fuzzy**: Approximate string matching using similarity scoring. Useful for handling typos, variations, or synonyms.
- **Semantic**: AI-powered similarity using embeddings (currently disabled due to system limitations). Finds conceptually related terms.

For Fuzzy and Semantic modes, adjust the threshold slider (50-100%) to control match strictness.

Enable NLP preprocessing for lemmatization and stop-word removal to improve matching accuracy.

---

## 🧑‍💻 Background

This project was originally developed as part of a WPI undergraduate research initiative in response to the **National Electric Vehicle Infrastructure (NEVI)** program.

The research and tool development were **sponsored by Atlas Public Policy** to assist in accelerating EV adoption and infrastructure analysis.

Recent enhancements include migration to PyQt6, upgraded PDF processing with PyMuPDF, addition of fuzzy and semantic search modes, NLP preprocessing, and persistent user settings.

---

## ✍️ Authors

Developed by Nicholas Borrello  
Supported by WPI faculty and advisors  
Sponsored by Atlas Public Policy
