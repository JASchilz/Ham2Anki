[![Build Status](https://travis-ci.com/JASchilz/Ham2Anki.svg?branch=master)](https://travis-ci.com/JASchilz/Ham2Anki)
[![Maintainability](https://api.codeclimate.com/v1/badges/17923d3985b4809caaf4/maintainability)](https://codeclimate.com/github/JASchilz/Ham2Anki/maintainability)
[![Coverage Status](https://coveralls.io/repos/github/JASchilz/Ham2Anki/badge.svg?branch=master)](https://coveralls.io/github/JASchilz/Ham2Anki?branch=master)

# Ham2Anki
Script to process ham radio exam questions from [http://ncvec.org](http://ncvec.org) into Anki flash cards.

You may be able to find Anki decks produced with the help of this script at [https://ankiweb.net/shared/decks/ham%20radio](https://ankiweb.net/shared/decks/ham%20radio)

## Use

Install the dependencies first:
```
$ pip install -r requirements.txt
```

Then see `python main.py --help`.

For example:
```
$ python main.py etc/questions.txt out.txt -r ncev-txt -w anki-tsv
```

Produces `out.txt`:
```
E1A01 (D) [97.301, 97.305]	When using a transceiver that displays the carrier frequency of phone signals, which of the following displayed frequencies represents the highest frequency at which a properly adjusted USB emission will be totally within the band?	(A) The exact upper band edge<br>(B) 300 Hz below the upper band edge<br>(C) 1 kHz below the upper band edge<br>(D) 3 kHz below the upper band edge	D	3 kHz below the upper band edge
E1A02 (D) [97.301, 97.305]	When using a transceiver that displays the carrier frequency of phone signals, which of the following displayed frequencies represents the lowest frequency at which a properly adjusted LSB emission will be totally within the band?	(A) The exact lower band edge<br>(B) 300 Hz above the lower band edge<br>(C) 1 kHz above the lower band edge<br>(D) 3 kHz above the lower band edge	D	3 kHz above the lower band edge
E1A03 (C) [97.301, 97.305]	With your transceiver displaying the carrier frequency of phone signals, you hear a station calling CQ on 14.349 MHz USB. Is it legal to return the call using upper sideband on the same frequency?	(A) Yes, because you were not the station calling CQ<br>(B) Yes, because the displayed frequency is within the 20 meter band<br>(C) No, the sideband will extend beyond the band edge<br>(D) No, U.S. stations are not permitted to use phone emissions above 14.340 MHz	C	No, the sideband will extend beyond the band edge
E1A04 (C) [97.301, 97.305] 	With your transceiver displaying the carrier frequency of phone signals, you hear a DX station calling CQ on 3.601 MHz LSB. Is it legal to return the call using lower sideband on the same frequency?	(A) Yes, because the DX station initiated the contact<br>(B) Yes, because the displayed frequency is within the 75 meter phone band segment<br>(C) No, the sideband will extend beyond the edge of the phone band segment<br>(D) No, U.S. stations are not permitted to use phone emissions below 3.610 MHz	C	No, the sideband will extend beyond the edge of the phone band segment
E1A05 (C) [97.313]	What is the maximum power output permitted on the 60 meter band?	(A) 50 watts PEP effective radiated power relative to an isotropic radiator<br>(B) 50 watts PEP effective radiated power relative to a dipole<br>(C) 100 watts PEP effective radiated power relative to the gain of a half-wave dipole<br>(D) 100 watts PEP effective radiated power relative to an isotropic radiator	C	100 watts PEP effective radiated power relative to the gain of a half-wave dipole
E1A06 (B) [97.15]	Where must the carrier frequency of a CW signal be set to comply with FCC rules for 60 meter operation?	(A) At the lowest frequency of the channel<br>(B) At the center frequency of the channel<br>(C) At the highest frequency of the channel<br>(D) On any frequency where the signal’s sidebands are within the channel	B	At the center frequency of the channel

...
```

You can produce a file like `questions.txt` by copying all of the text from a NCEV question pool release document into a text file and saving it to your computer. Alternatively, the `ncev-docx` reader reads the questions directly from the NCVEC Word (`.docx`) release, so no manual text extraction is needed:

```
$ python main.py pool.docx out.apkg -r ncev-docx -w anki-apkg
```

The `anki-tsv` writer produces a tab-separated file suitable for import into Anki. There are five columns of data written in `out.txt`:

| Column        | Example                                                |
| ------------- | ------------------------------------------------------ |
| Head          | Z1A15 (T) [104.301, 208.305]                           |
| Question      | Which of the following does a radio help you do?       |
| Choices       | (A) Cook\<br\>(B) Talk\<br\>(C) Sleep\<br\>(D) Bathe   |
| Answer Letter | B                                                      |
| Answer Text   | Talk                                                   |

From these five columns of data, you could construct any of multiple card types. For example, you might prefer to construct a card type which includes the multiple choices on the front of the card, or you might prefer to construct cards which do not include these multiple choices.

I have included a multiple choice card type in the deck export `etc/amatuer_radio_question.apkg`. You can import the file produced by `anki-tsv` into this card type.

### Producing a ready-to-import deck with figures (`anki-apkg`)

The `anki-apkg` writer produces a finished `.apkg` deck directly, with the
question-pool figures embedded and automatically attached to the cards that
reference them — no manual image work in Anki required. It reads the note type at
build time from a sample package (`etc/amateur_radio_question.apkg` by default,
or `--template-apkg <file>`), reusing that card type's id, fields, templates, and
CSS. So imported cards join the "Amateur Radio Pool Question" card type and update
in place rather than creating a duplicate. Because that note type has no dedicated
image field, referenced figures are placed in the question field, between the
question text and the choices.

```
$ python main.py questions.txt technician.apkg \
    -r ncev-txt -w anki-apkg \
    -f figures/ -d "Technician 2026-2030"
```

* `-f/--figures-dir` points at a directory of figure images. Name each file
  after its figure label as it appears in the pool, e.g. `T-1.png`, `T-2.png`,
  `T-3.png` (a leading `figure_` and any case/spacing differences are ignored,
  so `figure_t-1.png` also works). Supported extensions: `.png`, `.jpg`,
  `.jpeg`, `.gif`, `.bmp`, `.svg`.
* `-d/--deck-name` sets the deck name shown in Anki.

The NCVEC diagram exports ship with large blank borders. `scripts/crop_figures.py`
auto-trims each image to its content (plus a small margin) and can rename them to
the figure labels the writer expects:

```
$ python scripts/crop_figures.py "Diagram T1.jpg" "Diagram T2.jpg" "Diagram T3.jpg" \
    --out-dir figures --names T-1,T-2,T-3
```

Putting it together, a Technician deck can be built in two commands — crop the
figures, then read the `.docx` and write the deck:

```
$ python scripts/crop_figures.py Diagram*.jpg --out-dir figures --names T-1,T-2,T-3
$ python main.py pool.docx technician.apkg \
    -r ncev-docx -w anki-apkg -f figures -d "Technician 2026-2030"
```

For each question, the writer scans the question and its choices for references
like "Figure T-1" and injects the matching image into the card. Questions that
reference no figure, or a figure not present in the figures directory, are
written as plain text cards. Re-importing a regenerated deck updates existing
cards (notes are keyed on the question number) rather than duplicating them.

The `.apkg` deck is self-contained, so you can quality-check it by importing it
into Anki directly.

## Extending

This project uses the strategy pattern for flexible strategies for importing and exporting cards. You can replace or augment `ncev-txt` reader or the `anki-csv` writer with other reading and writing strategies. For example, you could create a reader which reads questions from a NCEV Microsoft Word document, or a writer which produces a `.apkg` Anki file.

