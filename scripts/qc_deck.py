"""Quality-check a generated .apkg against its source question pool.

This re-parses the source pool independently of the Ham2Anki reader/writer
pipeline (a raw walk of the document) and compares it to the notes actually
stored in the .apkg, so it catches problems anywhere from reading to writing.

Checks performed:
  * Question count: source "~~" sentinels and question-head lines vs. apkg notes.
  * Every source question id is present in the apkg, and vice versa.
  * For every question: answer letter, answer text, question text, and choices
    match the source (allowing for HTML escaping and appended figure images).
  * No corrupted (U+FFFD) characters; no empty/invalid answers.
  * Reports which cards carry a figure image (for a manual glance).
  * Trailing whitespace is reported as a warning only (it is copied faithfully
    from the source and is harmless in Anki).

Exit status is non-zero if any hard check fails.

Usage:
    python scripts/qc_deck.py SOURCE.docx DECK.apkg
"""
import argparse
import html
import os
import re
import sqlite3
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET


W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
HEAD_RE = re.compile(r'^([A-Z][0-9][A-Z][0-9]{2})\s+\(([A-D])\)')
CHOICE_RE = re.compile(r'^([A-D])\.\s*(.*)$')
FIGURE_TAIL_RE = re.compile(r'(<br><img[^>]*>)+$')
FIELD_SEP = chr(0x1f)


def source_lines(path):
    """Return the source pool as a list of text lines (one per docx paragraph)."""
    if path.lower().endswith('.docx'):
        root = ET.fromstring(zipfile.ZipFile(path).read('word/document.xml'))
        return [
            ''.join(node.text for node in paragraph.iter(W + 't') if node.text)
            for paragraph in root.iter(W + 'p')
        ]
    with open(path, 'r', encoding='utf-8') as handle:
        return handle.read().split('\n')


def parse_source(lines):
    """Independently parse the pool into {qid: (answer_letter, question, choices)}."""
    questions = {}
    i = 0
    while i < len(lines):
        match = HEAD_RE.match(lines[i].strip())
        if not match:
            i += 1
            continue
        qid, answer = match.group(1), match.group(2)
        question = lines[i + 1].strip()
        choices = {}
        j = i + 2
        while j < len(lines) and lines[j].strip() != '~~':
            choice = CHOICE_RE.match(lines[j].strip())
            if choice:
                choices[choice.group(1)] = choice.group(2)
            j += 1
        questions[qid] = (answer, question, choices)
        i = j + 1
    return questions


def load_apkg_notes(path):
    """Return {qid: (head, question, choices, answer_letter, answer_text)}."""
    archive = zipfile.ZipFile(path)
    tmp = os.path.join(tempfile.mkdtemp(), 'collection.anki2')
    with open(tmp, 'wb') as handle:
        handle.write(archive.read('collection.anki2'))
    con = sqlite3.connect(tmp)
    try:
        notes = {}
        for (flds,) in con.execute('select flds from notes'):
            parts = flds.split(FIELD_SEP)
            notes[parts[0].split()[0]] = tuple(parts)
        return notes
    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', help='Source pool (.docx or .txt).')
    parser.add_argument('apkg', help='Generated .apkg deck to check.')
    parser.add_argument(
        '--expected-count', type=int, default=None,
        help='The official question count published on the NCVEC pool page. '
             'If given, the source and deck must both contain exactly this many '
             'questions (guards against a stale or truncated download).')
    args = parser.parse_args()

    lines = source_lines(args.source)
    source = parse_source(lines)
    tildes = sum(1 for line in lines if line.strip() == '~~')
    heads = sum(1 for line in lines if HEAD_RE.match(line.strip()))
    notes = load_apkg_notes(args.apkg)

    failures = []
    warnings = []

    # --- Counts ---
    print('Source: {} "~~" sentinels, {} question-head lines, {} unique ids'.format(
        tildes, heads, len(source)))
    print('APKG:   {} notes, {} unique ids'.format(len(notes), len(notes)))
    if not (tildes == heads == len(source)):
        failures.append('Source is internally inconsistent (sentinels/heads/ids differ).')
    if len(notes) != len(source):
        failures.append('Note count {} != source question count {}.'.format(
            len(notes), len(source)))
    if args.expected_count is not None:
        print('Expected (published) count: {}'.format(args.expected_count))
        if len(source) != args.expected_count:
            failures.append('Source has {} questions, but the published count is {}.'.format(
                len(source), args.expected_count))
        if len(notes) != args.expected_count:
            failures.append('Deck has {} questions, but the published count is {}.'.format(
                len(notes), args.expected_count))

    # --- Id set comparison ---
    missing = sorted(set(source) - set(notes))
    extra = sorted(set(notes) - set(source))
    if missing:
        failures.append('In source but not apkg: {}'.format(missing))
    if extra:
        failures.append('In apkg but not source: {}'.format(extra))

    # --- Field-level comparison ---
    field_mismatches = 0
    trailing_ws = 0
    fffd = 0
    figure_cards = []
    for qid, note in notes.items():
        head, question, choices_f, letter, text = note
        for part in note:
            if part != part.rstrip():
                trailing_ws += 1
            fffd += part.count('�')
        if '<img' in question:
            figure_cards.append((qid, re.findall(r'<img src="([^"]+)"', question)))
        if qid not in source:
            continue
        answer, q, ch = source[qid]
        if letter not in 'ABCD' or not text:
            failures.append('{}: empty/invalid answer.'.format(qid))
        if letter != answer:
            field_mismatches += 1
            failures.append('{}: answer letter {} != source {}.'.format(qid, letter, answer))
        if html.unescape(text).rstrip() != ch.get(letter, '').rstrip():
            field_mismatches += 1
            failures.append('{}: answer text mismatch.'.format(qid))
        q_clean = html.unescape(FIGURE_TAIL_RE.sub('', question)).rstrip()
        if q_clean != q.rstrip():
            field_mismatches += 1
            failures.append('{}: question text mismatch.'.format(qid))
        want = '<br>'.join('({}) {}'.format(k, html.escape(ch[k]).rstrip())
                           for k in sorted(ch))
        got = '<br>'.join(part.rstrip() for part in choices_f.split('<br>'))
        if got != want:
            field_mismatches += 1
            failures.append('{}: choices mismatch.'.format(qid))

    if fffd:
        failures.append('{} corrupted (U+FFFD) characters found.'.format(fffd))
    if trailing_ws:
        warnings.append('{} fields carry trailing whitespace (copied from source; harmless).'.format(trailing_ws))

    print('\nField comparison: {} content mismatches.'.format(field_mismatches))
    print('Figure cards ({}):'.format(len(figure_cards)))
    for qid, imgs in sorted(figure_cards):
        print('  {} -> {}'.format(qid, ', '.join(imgs)))

    for warning in warnings:
        print('\nWARNING: ' + warning)

    if failures:
        print('\nFAIL ({} problem(s)):'.format(len(failures)))
        for failure in failures:
            print('  - ' + failure)
        sys.exit(1)

    print('\nPASS: deck matches source across all {} questions.'.format(len(source)))


if __name__ == '__main__':
    main()
