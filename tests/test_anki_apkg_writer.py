import os
import tempfile
import unittest

from question import Question
from writer import AnkiAPKG
from writer.anki_apkg import _normalize_figure_key, load_model


class TestAnkiAPKGWriter(unittest.TestCase):

    def test_model_is_read_from_sample_package(self):
        """The note type is derived from etc/amateur_radio_question.apkg."""
        model = load_model()
        field_names = [field['name'] for field in model.fields]

        self.assertEqual(1433221774348, model.model_id)
        self.assertEqual('Amateur Radio Pool Question', model.name)
        self.assertEqual(
            ['head', 'question', 'choices', 'answer_letter', 'answer_text'],
            field_names)

    def test_normalize_figure_key(self):
        """Figure labels and file stems reduce to the same comparable key."""
        self.assertEqual('t1', _normalize_figure_key('Figure T-1'))
        self.assertEqual('t1', _normalize_figure_key('T-1'))
        self.assertEqual('t1', _normalize_figure_key('figure_t1'))
        self.assertEqual('e52', _normalize_figure_key('Figure E5-2'))

    def test_referenced_figure_keys(self):
        """A question referencing a figure yields its normalized key."""
        with_figure = Question(
            'T1A01 (A)',
            'Which point in Figure T-1 is the antenna?',
            {'A': 'Point 1', 'B': 'Point 2', 'C': 'Point 3', 'D': 'Point 4'},
            'A',
        )
        without_figure = Question(
            'T1A02 (B)',
            'What is the capital of amateur radio?',
            {'A': 'Foo', 'B': 'Bar', 'C': 'Baz', 'D': 'Qux'},
            'B',
        )

        self.assertEqual({'t1'}, AnkiAPKG._referenced_figure_keys(with_figure))
        self.assertEqual(set(), AnkiAPKG._referenced_figure_keys(without_figure))

    def test_build_deck_attaches_only_referenced_figures(self):
        """Only questions that reference an available figure get an image."""
        figures_dir = tempfile.mkdtemp()
        # A tiny valid 1x1 PNG.
        png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00'
            b'\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc'
            b'\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        with open(os.path.join(figures_dir, 'T-1.png'), 'wb') as handle:
            handle.write(png)

        questions = [
            Question('T1A01 (A)', 'See Figure T-1.',
                     {'A': '1', 'B': '2', 'C': '3', 'D': '4'}, 'A'),
            Question('T1A02 (B)', 'No figure here.',
                     {'A': '1', 'B': '2', 'C': '3', 'D': '4'}, 'B'),
        ]

        deck, media_files = AnkiAPKG().build_deck(questions, figures_dir)

        # The note type has no image field, so figures are folded into the
        # question field (index 1).
        self.assertEqual(2, len(deck.notes))
        self.assertIn('<img src="T-1.png">', deck.notes[0].fields[1])
        self.assertNotIn('<img', deck.notes[1].fields[1])
        self.assertEqual(1, len(media_files))


if __name__ == '__main__':
    unittest.main()
