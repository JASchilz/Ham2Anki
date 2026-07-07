import argparse

import reader
import writer

readers = {
    'ncev-txt': reader.NCEVTxt,
    'ncev-docx': reader.NCEVDocx,
}

writers = {
    'anki-tsv': writer.AnkiTSV,
    'anki-apkg': writer.AnkiAPKG,
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
parser.add_argument(
    "-f",
    "--figures-dir",
    help="Directory of figure images to embed (anki-apkg writer only). "
         "Name each file after its figure label, e.g. 'T-1.png'.",
    default=None,
)
parser.add_argument(
    "-d",
    "--deck-name",
    help="Name of the deck to produce (anki-apkg writer only).",
    default="Ham Radio Question Pool",
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


writer_class = writers[args.writer]
if args.writer == 'anki-apkg':
    writer_instance = writer_class(deck_name=args.deck_name)
else:
    writer_instance = writer_class()

writer_instance.write_questions(questions, vars(args)["out"], figures_dir=args.figures_dir)

