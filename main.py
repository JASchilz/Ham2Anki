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

questions = readers[args.reader]().extract_questions(vars(args)["in"])
writers[args.writer]().write_questions(questions, vars(args)["out"])

