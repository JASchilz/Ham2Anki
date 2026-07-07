import os
import tempfile
import unittest
import zipfile

from reader import NCEVDocx


def _paragraph(text):
    return (
        '<w:p><w:r><w:t xml:space="preserve">{}</w:t></w:r></w:p>'.format(text)
    )


def _make_docx(path, blocks):
    """Write a minimal .docx whose document.xml holds the given text blocks.

    Each block is a list of paragraph strings; blocks are separated by an empty
    paragraph, mirroring the blank line between questions in an NCVEC release.
    """
    body = []
    for i, block in enumerate(blocks):
        if i:
            body.append(_paragraph(''))
        body.extend(_paragraph(line) for line in block)

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body>{}</w:body></w:document>'
    ).format(''.join(body))

    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('word/document.xml', document_xml)


class TestNCEVDocxReader(unittest.TestCase):

    def test_parses_questions_from_docx(self):
        path = os.path.join(tempfile.mkdtemp(), 'pool.docx')
        _make_docx(path, [
            ['T1A01 (C) [97.1]', 'First question?',
             'A. one', 'B. two', 'C. three', 'D. four', '~~'],
            ['T1A02 (B) [97.2]', 'Second question?',
             'A. one', 'B. two', 'C. three', 'D. four', '~~'],
        ])

        questions, rejected, errors = NCEVDocx().extract_questions(path)

        self.assertEqual(2, len(questions))
        self.assertEqual([], rejected)
        self.assertEqual([], errors)
        self.assertEqual('T1A01 (C) [97.1]', questions[0].head)
        self.assertEqual('C', questions[0].answer_key)
        self.assertEqual('three', questions[0].choices['C'])


if __name__ == '__main__':
    unittest.main()
