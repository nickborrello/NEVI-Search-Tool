import fitz  # PyMuPDF
import re
from thefuzz import fuzz

try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
except (ImportError, OSError):
    nlp = None

def preprocess_text(text):
    if nlp is None:
        return text.lower()
    doc = nlp(text.lower())
    return ' '.join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])

def group_matches(text, group, use_fuzzy=False, threshold=80):
    for term in group:
        if term.strip() == "":
            continue
        if use_fuzzy:
            term_lower = term.lower()
            if any(fuzz.ratio(term_lower, word.lower()) >= threshold for word in text.split()):
                return True
        else:
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True
    return False

def search_pdf_for_terms(pdf_path, term_sets, use_fuzzy=False, fuzzy_threshold=80, use_preprocessing=False):
    results = {}
    doc = fitz.open(pdf_path)

    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text() or ""
        if use_preprocessing:
            text = preprocess_text(text)
        lower_text = text.lower()
        if all(group_matches(lower_text, group, use_fuzzy, fuzzy_threshold) for group in term_sets):
            results[i] = text

    doc.close()
    return results

def semantic_search_pdf(pdf_path, term_sets, threshold=0.5):
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer('all-MiniLM-L6-v2')
        results = {}
        doc = fitz.open(pdf_path)
        term_embeddings = [model.encode(' '.join(group), convert_to_tensor=True) for group in term_sets]
        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text() or ""
            page_embedding = model.encode(text, convert_to_tensor=True)
            if all(util.cos_sim(page_embedding, term_emb).max() >= threshold for term_emb in term_embeddings):
                results[i] = text
        doc.close()
        return results
    except ImportError as e:
        print(f"Semantic search not available: {e}")
        return {}
