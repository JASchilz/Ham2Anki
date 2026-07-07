# CLAUDE.md

Guidance for Claude Code (and humans) working in this repository.

## What this project does

Ham2Anki converts an NCVEC amateur-radio exam **question pool** into an **Anki
deck**. A new pool is released for each license class (Technician, General,
Amateur Extra) every four years, and this tool rebuilds the corresponding deck.

The headline workflow produces a finished `.apkg` with the pool's figures
embedded and automatically attached to the cards that reference them — no manual
image work in Anki. See `.claude/skills/export-ham-deck/SKILL.md` for the
step-by-step procedure; that skill is the primary entry point when the user asks
to build a new deck.

## Architecture

The pipeline is a strategy pattern: a **reader** parses a source pool into
`Question` objects, and a **writer** serializes them. `main.py` wires them
together and prints a per-subelement question count.

- `question/question.py` — `Question(head, question, choices, answer_key)`.
- `reader/ncev_txt.py` (`ncev-txt`) — parses NCVEC's plain-text release. Blocks
  are separated by blank lines and end with a `~~` sentinel; the shared parsing
  lives in `extract_from_text`.
- `reader/ncev_docx.py` (`ncev-docx`) — reads the questions straight from the
  NCVEC Word (`.docx`) release. The `.docx` uses the same `~~`-delimited layout,
  so it recovers the paragraph text and delegates to `NCEVTxt.extract_from_text`.
  **Prefer this**: NCVEC reliably publishes a `.docx`, and downloading clean
  plain text is often not possible.
- `writer/anki_tsv.py` (`anki-tsv`) — legacy tab-separated output for manual
  import into a card type.
- `writer/anki_apkg.py` (`anki-apkg`) — builds a finished `.apkg` via `genanki`.
  It reproduces the user's existing **"Amateur Radio Pool Question"** note type
  (model id `1433221774348`, fields `head/question/choices/answer_letter/
  answer_text`), so imported cards join that card type and update in place. That
  note type has no image field, so referenced figures are folded into the
  `question` field, between the question text and the choices. Notes are keyed on
  the question number (e.g. `T1A01`) so re-imports update rather than duplicate.

### Readers/writers contract

Every reader exposes `extract_questions(path)` returning
`(questions, possible_but_rejected, error_questions)`. Every writer exposes
`write_questions(questions, path, figures_dir=None)`. Register new strategies in
`main.py` and the package `__init__`.

## Helper scripts

- `scripts/crop_figures.py` — auto-trims the blank borders off NCVEC figure
  exports (non-white bounding box + margin) and can rename them to the figure
  labels the writer matches. Outputs PNG (crisper than JPEG for line art).
- `scripts/qc_deck.py` — independently re-parses the source pool and compares it
  to a built `.apkg`: counts, id coverage, per-field content, figure
  associations, and character-corruption checks. Exits non-zero on any hard
  failure. Run this on every deck before shipping.

## Figure matching

The writer scans each question and its choices for references like
`Figure T-1` (case-insensitive) and injects the matching image. Matching is by a
normalized key: labels and image filename stems are lowercased with non-
alphanumerics removed, and a leading `figure` is stripped — so a `Figure T-1`
reference matches `T-1.png`, `t-1.jpg`, or `figure_t1.png`. Name cropped figure
files after their label (`T-1.png`, `E5-2.png`, …).

## Environment notes (this machine)

- **Python is not on `PATH`.** Invoke it explicitly:
  `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` (Python 3.12). `python`,
  `py`, and `pandoc` are all absent from `PATH`.
- Install dependencies with `pip install -r requirements.txt` (`genanki` for the
  writer; `Pillow` for the crop script).
- Shell is PowerShell; to pass multi-line Python to `python -c`, use a
  single-quoted here-string (`@' ... '@`).

## Testing

`python -m unittest discover -s tests`. Tests cover the txt and docx readers and
the apkg writer's figure logic. Add a test when you add a reader or writer.

## Conventions

- Match the existing terse, dependency-light style. Standard library first;
  `genanki`/`Pillow` are the only third-party deps.
- Do not commit pool working data or generated decks — `question/*/` is
  gitignored. Committed pools/decks are only the small examples already in `etc/`.
