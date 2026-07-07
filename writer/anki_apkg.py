import os
import re
from html import escape

import genanki


# This is the model (note type) ID of the user's existing "Amateur Radio Pool
# Question" card type, extracted from etc/amateur_radio_question.apkg. Reusing
# the same ID, field list, and templates means an imported deck attaches to that
# existing note type and updates in place rather than creating a duplicate.
MODEL_ID = 1433221774348

# Arbitrary but stable deck ID. Generated with random.randrange(1 << 30, 1 << 31).
DECK_ID = 2059400110

# Image file extensions we will treat as figures when scanning a figures directory.
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')

# Matches references like "figure T-1", "Figure T1", "in Figure E5-2", etc.
FIGURE_REFERENCE = re.compile(r'Figure\s+([A-Za-z]+-?\d+(?:-\d+)?)', re.IGNORECASE)

# Faithful reproduction of the user's existing note type so that the produced
# deck renders identically and merges with their collection on import.
MODEL = genanki.Model(
    MODEL_ID,
    'Amateur Radio Pool Question',
    fields=[
        {'name': 'head'},
        {'name': 'question'},
        {'name': 'choices'},
        {'name': 'answer_letter'},
        {'name': 'answer_text'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{question}}\n<br>\n{{choices}}\n<hr id=answer>',
            'afmt': '{{FrontSide}}\n\n\n\n({{answer_letter}}) {{answer_text}}',
        },
    ],
    css=(
        '.card {\n font-family: arial;\n font-size: 20px;\n text-align: left;\n'
        ' color: black;\n background-color: white;\n}\n\n'
        '.code {\n\tfont-family: "Courier New", Courier, monospace;\n'
        '       text-align:left;\n}\n'
    ),
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

    def __init__(self, deck_name='Ham Radio Question Pool'):
        self.deck_name = deck_name

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

        for question in questions:
            choices_html = '<br>'.join(
                '({}) {}'.format(escape(key), escape(question.choices[key]))
                for key in sorted(question.choices.keys())
            )

            note = genanki.Note(
                model=MODEL,
                fields=[
                    escape(question.head),
                    self._question_html(question, available_figures, used_media),
                    choices_html,
                    escape(question.answer_key),
                    escape(question.choices.get(question.answer_key, '')),
                ],
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
