# PyQt5 to PyQt6 Migration Plan for NEVI Search Tool

## Overview
This plan outlines a phased migration from PyQt5 to PyQt6 for the NEVI Search Tool. The migration leverages Qt6's improvements in performance, high-DPI support, and modern Python integration while addressing breaking API changes. Estimated total effort: 1-2 weeks for a developer familiar with PyQt, including testing.

Key goals:
- Update all imports and APIs to PyQt6.
- Resolve deprecated features (e.g., QRegExp → QRegularExpression).
- Ensure backward compatibility where possible.
- Test thoroughly on Windows (primary platform).

## Phase 1: Preparation and Research
- [x] Review Qt6/PyQt6 documentation for breaking changes (focus on QRegExp, enums, signals).
- [ ] Backup current codebase (commit to Git).
- [ ] Install PyQt6 in a virtual environment: `pip install PyQt6`.
- [ ] Run current app with PyQt5 to confirm baseline functionality.
- [ ] Identify all PyQt5-specific code (grep for "PyQt5", "QRegExp", etc.).

## Phase 2: Core Migration
- [ ] Update main.py: Change imports from PyQt5 to PyQt6.
- [ ] Update gui/main_window.py: Migrate QMainWindow, QComboBox, QListWidget, QPushButton, QFileDialog, QMessageBox.
- [ ] Update gui/reader_window.py: Replace QRegExp with QRegularExpression in highlight_text() method.
- [ ] Update gui/term_editor_window.py: Migrate QDialog, QComboBox, QListWidget, QPlainTextEdit, QMessageBox.
- [ ] Update logic/term_loader.py: No changes needed (pure Python).
- [ ] Update logic/search_engine.py: No changes needed (uses pypdf, not PyQt).
- [ ] Update data/terms.json: No changes needed.
- [ ] Update README.md: Change installation instructions to PyQt6, update Python version to 3.8+.

## Phase 3: Testing and Validation
- [ ] Run app and test basic UI (load PDF, select category/question, run search).
- [ ] Test PDF reading and keyword highlighting (ensure matches are found and highlighted).
- [ ] Test term editor (add/remove categories/questions, save changes).
- [ ] Check for runtime errors (e.g., deprecated API warnings).
- [ ] Test on different PDF files (various sizes, text complexity).
- [ ] Validate on Windows (primary OS); note any platform-specific issues.

## Phase 4: Optimization and Polish
- [ ] Leverage new PyQt6 features if beneficial (e.g., type hints for better IDE support).
- [ ] Update requirements.txt or README to specify PyQt6.
- [ ] Profile performance (startup time, search speed) and compare to PyQt5 baseline.
- [ ] Add comments in code for PyQt6-specific changes.
- [ ] Final Git commit with migration summary.

## Risks and Mitigations
- **Breaking Changes**: QRegExp migration may introduce bugs in highlighting—test regex patterns thoroughly.
- **Dependency Conflicts**: Ensure pypdf and other libs work with Python 3.8+.
- **Qt6 Quirks**: High-DPI or rendering differences—test on multiple displays.
- **Rollback Plan**: Keep PyQt5 branch for quick revert if issues arise.

## Success Criteria
- App runs without errors on PyQt6.
- All features (search, highlight, edit terms) work identically to PyQt5 version.
- No performance regressions; ideally slight improvements.
- Code is maintainable and uses modern PyQt6 idioms.

## Timeline
- Phase 1: 1 day
- Phase 2: 3-5 days
- Phase 3: 2-3 days
- Phase 4: 1-2 days

Total: 7-11 days, depending on testing depth.