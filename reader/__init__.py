"""
All readers shall:

1. Have a method `extract_questions`
2. The `extract_questions` method shall accept a path, and return:
  a. A list of questions (see the Question class in the question module)
  b. A list of printable elements, representing text which the reader rejected
     as questions during parsing, but which may be malformed questions.
  c. A list of printable elements, representing text which the reader believes
     to be questions but that it encountered errors on while processing.
"""

from .ncev_txt import NCEVTxt