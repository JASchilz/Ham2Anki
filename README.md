# Ham2Anki
Script to process ham radio exam questions from `http://ncvec.org` into Anki flash cards.

## Use

See `python main.py --help`.

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

The output produced by `anki-tsv` produces a tab-separated file suitable for import into Anki. There are five columns of data written in `out.txt`:

| Column        | Example                                                |
| ------------- | ------------------------------------------------------ |
| Head          | Z1A15 (T) [104.301, 208.305]                           |
| Question      | Which of the following does a radio help you do?       |
| Choices       | (A) Cook\<br\>(B) Talk\<br\>(C) Sleep\<br\>(D) Bathe   |
| Answer Letter | B                                                      |
| Answer Text   | Talk                                                   |

These five columns afford the flexibility to construct multiple card types. For example, you could construct cards which display the multiple A-B-C-D choices on the front, or cards which do not display these choices.

I have included a multiple choice card type in the deck export `etc/amatuer_radio_question.apkg`. You can import the file produced by `anki-tsv` into this card type.
