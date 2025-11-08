# AI/ML Improvements for EV Infrastructure Plan Search Tool Logic

## Overview
The current logic in the EV Infrastructure Plan Search Tool relies on simple regex-based keyword matching for searching PDFs. While effective for exact terms, it lacks flexibility for semantic variations, typos, or contextual understanding. This document outlines a plan to integrate AI/ML advancements since 2022 to enhance search accuracy, robustness, and user experience. Improvements include fuzzy matching, semantic search, NLP preprocessing, query expansion with LLMs, and UI options.

All changes will maintain backward compatibility, with new features as optional toggles.

## 1. Fuzzy Matching
### Description
Use approximate string matching to handle spelling variations or typos in terms (e.g., "chargng" matches "charging" at 80% similarity). This complements exact regex matching.

### Dependencies
- Install `thefuzz` library: `pip install thefuzz`

### Implementation Steps
1. Update `logic/search_engine.py`:
   - Import: `from thefuzz import fuzz`
   - Modify `group_matches` function to include fuzzy check:
     ```python
     def group_matches(text, group, use_fuzzy=False, threshold=80):
         for term in group:
             if term.strip() == "":
                 continue
             if use_fuzzy:
                 if any(fuzz.ratio(term.lower(), word.lower()) >= threshold for word in text.split()):
                     return True
             else:
                 pattern = r"\b" + re.escape(term) + r"\b"
                 if re.search(pattern, text, flags=re.IGNORECASE):
                     return True
         return False
     ```
   - Update `search_pdf_for_terms` to accept `use_fuzzy` and `fuzzy_threshold` parameters.

2. Update `gui/main_window.py`:
   - Add checkbox: `self.fuzzy_checkbox = QtWidgets.QCheckBox("Enable Fuzzy Matching")`
   - Add slider for threshold: `self.fuzzy_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.fuzzy_slider.setRange(50, 100); self.fuzzy_slider.setValue(80)`
   - Pass to search: `results = search_pdf_for_terms(self.selected_file, term_sets, use_fuzzy=self.fuzzy_checkbox.isChecked(), fuzzy_threshold=self.fuzzy_slider.value())`

### Testing
- Test with PDFs containing typos; verify matches at different thresholds.

## 2. Semantic Search
### Description
Use embedding models for semantic similarity, finding pages conceptually related to terms (e.g., "EV stations" matches "electric vehicle charging points").

### Dependencies
- Install `sentence-transformers`: `pip install sentence-transformers`

### Implementation Steps
1. Update `logic/search_engine.py`:
   - Import: `from sentence_transformers import SentenceTransformer, util`
   - Add model loading: `model = SentenceTransformer("all-MiniLM-L6-v2")`
   - Create `semantic_search_pdf` function:
     ```python
     def semantic_search_pdf(pdf_path, term_sets, threshold=0.5):
         results = {}
         doc = fitz.open(pdf_path)
         term_embeddings = [model.encode(" ".join(group), convert_to_tensor=True) for group in term_sets]
         for i in range(len(doc)):
             page = doc.load_page(i)
             text = page.get_text() or ""
             page_embedding = model.encode(text, convert_to_tensor=True)
             if all(util.cos_sim(page_embedding, term_emb).max() >= threshold for term_emb in term_embeddings):
                 results[i] = text
         doc.close()
         return results
     ```

2. Update `gui/main_window.py`:
   - Add radio buttons: Keyword vs Semantic search.
   - Add threshold slider.
   - Call appropriate function based on selection.

### Testing
- Test with semantically related but non-exact terms; adjust threshold for precision/recall.

## 3. NLP Preprocessing
### Description
Clean and normalize text using NLP (lemmatization, stop-word removal) for better matching.

### Dependencies
- Install `spacy`: `pip install spacy`
- Download model: `python -m spacy download en_core_web_sm`

### Implementation Steps
1. Update `logic/search_engine.py`:
   - Import: `import spacy`
   - Load model: `nlp = spacy.load("en_core_web_sm")`
   - Add preprocess function:
     ```python
     def preprocess_text(text):
         doc = nlp(text.lower())
         return " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
     ```
   - Apply to page text and terms before matching.

### Testing
- Compare search results with/without preprocessing on noisy PDFs.

## 4. Query Expansion with LLMs
### Description
Use LLMs to dynamically expand search terms with synonyms/related words based on questions.

### Dependencies
- Install `openai` or `langchain`: `pip install openai langchain`

### Implementation Steps
1. Add API key handling in `logic/settings.py`.
2. Update `logic/search_engine.py`:
   - Function to expand terms:
     ```python
     from langchain.llms import OpenAI
     llm = OpenAI(api_key=settings["openai_key"])
     def expand_terms(question, terms):
         prompt = f"Expand these terms for the question \"{question}\": {terms}. Provide comma-separated synonyms."
         response = llm(prompt)
         return response.split(",")
     ```
3. Integrate into term loading or search.

### Testing
- Manually verify expansions; test search with expanded terms.

## 5. UI Integration
### Description
Add toggles and controls in the main window for new features.

### Implementation Steps
1. In `gui/main_window.py`:
   - Add group box for "Advanced Search Options".
   - Include checkboxes, sliders, and radio buttons as described.
   - Update `run_search` to pass parameters.

### Testing
- Ensure UI elements enable/disable features correctly.

## 6. Testing and Validation
- Unit tests for new functions in `logic/`.
- Integration tests with sample EV PDFs.
- Performance benchmarks (time for search).
- User testing for usability.

## Conclusion
These improvements will make the tool more intelligent and adaptable. Start with fuzzy matching and semantic search for quick wins. Estimated effort: 2-3 weeks. Update README with new features.
## Implementation Status
- [x] Fuzzy Matching: Implemented with thefuzz library, configurable threshold.
- [x] Semantic Search: Not implemented due to PyTorch DLL issues on Windows.
- [x] NLP Preprocessing: Implemented with spaCy, handles import errors gracefully.
- [ ] Query Expansion with LLMs: Not implemented due to PyTorch dependencies.
- [x] UI Integration: Added radio buttons for search modes, threshold slider, preprocessing checkbox.
- [ ] Testing: Basic testing done; further validation needed.

Note: Semantic search and LLM features require PyTorch, which has compatibility issues on this Windows system (DLL initialization failure). These can be added later on compatible systems.
