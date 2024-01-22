import argparse

import reader
import writer

readers = {
    'ncev-txt': reader.NCEVTxt,
}

writers = {
    'anki-tsv': writer.AnkiTSV,
}

parser = argparse.ArgumentParser(description="Parse a Ham radio question pool file into flash cards.")
parser.add_argument("in", help="Location of question pool file.")
parser.add_argument("out", help="Destination to write flash card file.")
parser.add_argument(
    "-r",
    "--reader",
    help="The format of the input file.",
    required=True,
    choices=readers.keys(),
)
parser.add_argument(
    "-w",
    "--writer",
    help="The desired format of the output file.",
    required=True,
    choices=writers.keys()
)
args = parser.parse_args()

questions, possible_but_rejected, error_questions = readers[args.reader]().extract_questions(vars(args)["in"])

if possible_but_rejected:
    print("\nTHE READER ENCOUNTERED AND REJECTED THE FOLLOWING POSSIBLE QUESTIONS:")
    for question in possible_but_rejected:
        print(question + "\n")

if error_questions:
    print("\nTHE READER ENCOUNTERED ERRORS WHILE PROCESSING THE FOLLOWING QUESTIONS:")
    for question in error_questions:
        print(question + "\n")

section_count = {}
for question in questions:
    section = question.head[0:2]
    try:
        section_count[section] += 1
    except KeyError:
        section_count[section] = 1

print("\nFOUND THE FOLLOWING NUMBER OF QUESTIONS PER SECTION:")
print(section_count)


writers[args.writer]().write_questions(questions, vars(args)["out"])

