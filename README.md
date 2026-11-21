[![The Passport Page of a Country That Isn't There on make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Passport of Nowhere rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/blupoint44/passport-of-nowhere/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Passport of Nowhere reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/blupoint44/passport-of-nowhere/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

# Passport of Nowhere

A program that draws an invented passport spread — an open passport for the
**Republic of Auralis**, a maritime republic that does not exist — entirely in
code, and writes it to `entry.png`.

## What the entry draws

A two-page spread at 1024×768:

- **Left — the data page:** country name and coat of arms (a lighthouse over
  waves, for the Ministry of Tides and Harbours), passport number
  AUR 0482716, a drawn portrait of the holder Mira Solenne Vey of Port Lumen,
  bilingual Auralic/English field labels, issue 14 MAR 2021 and expiry
  14 MAR 2031, guilloche-style security linework, and a two-line
  machine-readable zone at the foot of the page.
- **Right — visas and endorsements:** a chronological, internally consistent
  travel history that all postdates the issue date — Velmarra arrival
  03 JUL 2022 and departure 18 JUL 2022, Ostravia (Kest Port) entry
  09 MAY 2023 and exit 27 MAY 2023, Kestrel Isles arrival 02 NOV 2024 — plus
  the telling paperwork detail: a **Tide Fee Paid** stamp and the Tide Law
  Art. 7 condition requiring the holder to register a tide table at each
  port of call, with harbour dues paid in Auralian litres.

Everything is drawn by `main.py` itself: a pure-Python raster canvas, a small
5×7 bitmap font, shape primitives, and a zlib PNG encoder. No external image
files, no image-generation tools, no network. Output is deterministic — the
same bytes on every run.

## How to run

```sh
python3 main.py
# writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png)
MAKEFUN_OUTPUT_DIR=./out python3 main.py
```

Requires Python 3.13 (stdlib only).

## Guide

- Bounty page: [The Passport Page of a Country That Isn't There](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
- Join make.fun with this referral link: https://make.fun/?ref=cc9ads3n
- Run the program, open `entry.png`, and check the spread reads as one
  coherent document: data page on the left, stamps and the tide-fee
  endorsement on the right, and the machine-readable strip along the bottom.

## License

MIT — see [LICENSE](LICENSE).
