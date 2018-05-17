import unittest

from reader import NCEVTxt


class TestNCEVTxtReader(unittest.TestCase):

    def test_questions(self):
        """
        The included questions.txt file contains 712 questions. Test that the NCEVTxt reader
        parses all of them.
        """
        questions, possible_but_rejected, error_questions = NCEVTxt().extract_questions("tests/questions.txt")

        self.assertEqual(712, len(questions))

    def test_possible_but_rejected(self):
        """
        The included questions.txt file contains 10 regions that look like they might be
        questions, but the NCEVTxt reader should reject them.
        """
        questions, possible_but_rejected, error_questions = NCEVTxt().extract_questions("tests/questions.txt")

        self.assertEqual(10, len(possible_but_rejected))
