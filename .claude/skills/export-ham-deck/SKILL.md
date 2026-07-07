---
name: export-ham-deck
description: Build an Anki deck (.apkg) from an NCVEC amateur-radio exam question pool (Technician, General, or Amateur Extra), with figures embedded and auto-attached. Use when the user wants to create, export, build, or regenerate a ham radio question-pool deck for import into Anki.
---

# Export a ham radio question-pool deck

## Goal

Turn an NCVEC question pool into a finished, quality-checked Anki `.apkg` in a
few minutes — figures embedded and automatically attached to the right cards,
using the user's existing "Amateur Radio Pool Question" card type — so the user
only has to import it and glance over it.

A new pool is released per license class (Technician / General / Amateur Extra)
every four years. This skill rebuilds the deck for whichever pool the user names.

Read `CLAUDE.md` for architecture and the Python-on-this-machine details. Use the
explicit interpreter path (Python is not on `PATH`):
`%LOCALAPPDATA%\Programs\Python\Python312\python.exe`.

## Step 1 — What the human must provide

Ask the user to gather these from the pool page on <https://ncvec.org> (the site
blocks automated fetching, so the human downloads). For each pool the page links:

1. **The pool release Word document (`.docx`)** — always prefer this over trying
   to get plain text. Use the **latest** release/errata revision.
2. **The figure/diagram images** — the pool page publishes them as separate image
   downloads (and they also appear in the pool PDF). Get every diagram the pool
   uses.
3. **The official question count**, stated in the NCVEC release notes or ARRL
   announcement (e.g. the 2026–2030 Technician pool has **409** questions). Record
   it — it is a required QC input.

Have the user drop the `.docx` and images into a working directory
`question/<year>-<class>/` (e.g. `question/2026-technician/`). This path is
gitignored.

Also confirm the target **card type**. The writer reads the note type at build
time from a sample package (`etc/amateur_radio_question.apkg` by default), so
imported cards merge into the "Amateur Radio Pool Question" type and update in
place. To use a different card type, have the user export a deck that uses it as
`.apkg` and pass it with `--template-apkg <file>`; the writer will reuse that
model's id, fields, templates, and CSS automatically.

## Step 2 — Pre-processing (Claude does this)

1. **Install deps** if needed: `pip install -r requirements.txt`.

2. **Identify the figure labels** the pool uses. Extract the pool text and grep
   for figure references (`Figure T-1`, `Figure E5-2`, …) so you know which
   labels exist and which image is which.

3. **Crop the figures.** NCVEC exports have large blank borders. Auto-trim and
   name each output after its figure label:
   ```
   python scripts/crop_figures.py <image files...> \
       --out-dir question/<year>-<class>/figures --names T-1,T-2,T-3
   ```
   Filenames must normalize to the reference (e.g. `T-1.png` ↔ "Figure T-1").
   On the first pool of a run, open the cropped PNGs once to confirm nothing was
   clipped (component numbers and the "Figure X" caption intact); after that the
   crop is deterministic and needs no further inspection.

4. **Build the deck**, reading the `.docx` directly:
   ```
   python main.py "question/<year>-<class>/<pool>.docx" \
       "question/<year>-<class>/<Class>_<years>.apkg" \
       -r ncev-docx -w anki-apkg \
       -f "question/<year>-<class>/figures" \
       -d "Ham Radio - <Class> (<years>)"
   ```
   `main.py` prints a per-subelement question count — sanity-check it looks
   right. Note any "rejected"/"error" blocks it reports (should be zero); if not,
   the pool's layout differs from the usual `~~` format and the reader needs a
   look.

## Step 3 — Quality control (Claude does this, every time)

Run the automated cross-check, passing the published count from Step 1:
```
python scripts/qc_deck.py "question/<year>-<class>/<pool>.docx" \
    "question/<year>-<class>/<Class>_<years>.apkg" --expected-count <N>
```
It independently re-parses the source (not via the pipeline) and verifies:

- **Count vs. the published number** — source and deck both equal `<N>`. This
  catches a stale or truncated download.
- **Internal count consistency** — `~~` sentinels, question-head lines, and note
  count all agree.
- **ID coverage** — every source question id is in the deck, and no extras.
- **Field content** — answer letter, answer text, question, and choices match the
  source for all questions (allowing for HTML escaping and appended figures).
- **No corrupted characters** (U+FFFD); no empty/invalid answers.
- **Figure associations** — prints which cards carry which figure image; confirm
  the count of figure cards matches the number of questions that reference a
  figure.

A trailing-whitespace warning is expected and harmless (copied from the source).
The script exits non-zero on any hard failure. Report the QC summary to the user.

## Step 4 — Deliver

Send the `.apkg` to the user with `SendUserFile` and a one-line summary (question
count, figures embedded, card type). Remind them it imports into their existing
"Amateur Radio Pool Question" card type and updates in place on re-import (notes
are keyed on question number).

## Things people forget

- **Use the latest errata revision** of the pool, not the original release.
- **Figure labels and counts differ per pool** (Technician uses `T-1..T-3`;
  General/Extra use `E5-2`-style labels and there are more of them). Don't assume.
- **The published count is the source of truth** for completeness — always pass
  `--expected-count`.
- **Special characters** (curly quotes, degree signs) should survive intact; the
  QC script's U+FFFD check guards this.
- Pool working data and generated decks are **gitignored** (`question/*/`); don't
  commit them.
