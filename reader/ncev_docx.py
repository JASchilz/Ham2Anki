import zipfile
import xml.etree.ElementTree as ET

from .ncev_txt import NCEVTxt


# WordprocessingML namespace.
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


class NCEVDocx(NCEVTxt):
    """Reads an NCVEC question pool straight from the released Word (.docx) file.

    The NCVEC .docx release lays each question out exactly like the plain-text
    release (question head, question, four choices, then a "~~" sentinel, blank
    line between questions), so this reader just recovers that text from the
    document's paragraphs and hands it to the NCEVTxt parsing logic.
    """

    @staticmethod
    def _document_text(path):
        with zipfile.ZipFile(path) as archive:
            document_xml = archive.read('word/document.xml')

        root = ET.fromstring(document_xml)
        paragraphs = [
            ''.join(node.text for node in paragraph.iter(W + 't') if node.text)
            for paragraph in root.iter(W + 'p')
        ]
        return '\n'.join(paragraphs)

    @classmethod
    def extract_questions(cls, path):
        return cls.extract_from_text(cls._document_text(path))
