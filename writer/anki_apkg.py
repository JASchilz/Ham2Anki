import json
import os
import re
import sqlite3
import tempfile
import zipfile
from html import escape

import genanki


# Arbitrary but stable deck ID. Generated with random.randrange(1 << 30, 1 << 31).
DECK_ID = 2059400110

# The card type is not hardcoded: it is read at build time from this sample
# package, so the produced deck always matches whatever "Amateur Radio Pool
# Question" note type lives there (same model id, fields, templates, and CSS).
# Resolved relative to this file so it works regardless of the caller's cwd.
DEFAULT_TEMPLATE_APKG = os.path.join(
    os.path.dirname(__file__), os.pardir, 'etc', 'amateur_radio_question.apkg')

# Image file extensions we will treat as figures when scanning a figures directory.
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')

# Matches references like "figure T-1", "Figure T1", "in Figure E5-2", etc.
FIGURE_REFERENCE = re.compile(r'Figure\s+([A-Za-z]+-?\d+(?:-\d+)?)', re.IGNORECASE)


def load_model(template_apkg=DEFAULT_TEMPLATE_APKG):
    """Build a genanki Model from the note type stored in an .apkg.

    Reusing the sample package's model id, fields, templates, and CSS means an
    imported deck attaches to that existing note type and updates in place
    rather than creating a duplicate.
    """
    if not os.path.exists(template_apkg):
        raise FileNotFoundError(
            'Template package not found: {}. It supplies the Anki note type.'
            .format(template_apkg))

    with zipfile.ZipFile(template_apkg) as archive:
        collection_bytes = archive.read('collection.anki2')

    collection_path = os.path.join(tempfile.mkdtemp(), 'collection.anki2')
    with open(collection_path, 'wb') as handle:
        handle.write(collection_bytes)

    connection = sqlite3.connect(collection_path)
    try:
        models = json.loads(connection.execute('select models from col').fetchone()[0])
    finally:
        connection.close()

    # Prefer a model that looks like the question note type; fall back to the
    # first one defined.
    model_id, model = next(
        ((mid, m) for mid, m in models.items()
         if {'question', 'answer_letter'} <= {f['name'] for f in m['flds']}),
        next(iter(models.items())),
    )

    return genanki.Model(
        int(model_id),
        model['name'],
        fields=[{'name': f['name']}
                for f in sorted(model['flds'], key=lambda f: f['ord'])],
        templates=[{'name': t['name'], 'qfmt': t['qfmt'], 'afmt': t['afmt']}
                   for t in sorted(model['tmpls'], key=lambda t: t['ord'])],
        css=model.get('css', ''),
    )


def _normalize_figure_key(label):
    """Reduce a figure label or file stem to a comparable key.

    "Figure T-1" -> "t1", "T-1" -> "t1", "figure_e5-2" -> "e52".
    A leading "figure" on file stems is stripped so that "T-1.png" and
    "figure_t-1.png" both match a "Figure T-1" reference.
    """
    key = re.sub(r'[^a-z0-9]', '', label.lower())
    if key.startswith('figure'):
        key = key[len('figure'):]
    return key


class AnkiAPKG(object):

    def __init__(self, deck_name='Ham Radio Question Pool',
                 template_apkg=DEFAULT_TEMPLATE_APKG):
        self.deck_name = deck_name
        self.model = load_model(template_apkg)

    @staticmethod
    def _discover_figures(figures_dir):
        """Map normalized figure keys to image paths for a directory."""
        figures = {}
        if not figures_dir or not os.path.isdir(figures_dir):
            return figures

        for filename in os.listdir(figures_dir):
            stem, extension = os.path.splitext(filename)
            if extension.lower() not in IMAGE_EXTENSIONS:
                continue
            figures[_normalize_figure_key(stem)] = os.path.join(figures_dir, filename)

        return figures

    @staticmethod
    def _referenced_figure_keys(question):
        """Return the set of normalized figure keys a question refers to."""
        text = ' '.join([question.question] + list(question.choices.values()))
        return {
            _normalize_figure_key(match.group(1))
            for match in FIGURE_REFERENCE.finditer(text)
        }

    def _question_html(self, question, available_figures, used_media):
        """Question text with any referenced figure images appended.

        The note type has no dedicated image field, so figures are folded into
        the question field. They land between the question text and the choices
        (the template renders {{question}} then {{choices}}).
        """
        html = escape(question.question)
        for key in sorted(self._referenced_figure_keys(question)):
            image_path = available_figures.get(key)
            if image_path:
                used_media.add(image_path)
                html += '<br><img src="{}">'.format(escape(os.path.basename(image_path)))
        return html

    def build_deck(self, questions, figures_dir=None):
        """Return a (deck, media_files) pair built from the questions."""
        available_figures = self._discover_figures(figures_dir)
        used_media = set()

        deck = genanki.Deck(DECK_ID, self.deck_name)

        field_names = [field['name'] for field in self.model.fields]

        for question in questions:
            choices_html = '<br>'.join(
                '({}) {}'.format(escape(key), escape(question.choices[key]))
                for key in sorted(question.choices.keys())
            )

            # Map values by field name so we stay correct even if the note
            # type's field order changes. Figures fold into the question field
            # (the note type has no dedicated image field).
            values = {
                'head': escape(question.head),
                'question': self._question_html(question, available_figures, used_media),
                'choices': choices_html,
                'answer_letter': escape(question.answer_key),
                'answer_text': escape(question.choices.get(question.answer_key, '')),
            }

            note = genanki.Note(
                model=self.model,
                fields=[values.get(name, '') for name in field_names],
                # Key on the question number (e.g. "T1A01") so that pool
                # revisions to citations or wording update the existing card
                # rather than creating a duplicate.
                guid=genanki.guid_for(question.head.split()[0]),
            )
            deck.add_note(note)

        return deck, sorted(used_media)

    def write_questions(self, questions, path, figures_dir=None):
        deck, media_files = self.build_deck(questions, figures_dir)
        genanki.Package(deck, media_files=media_files).write_to_file(path)
