# Roboto, unused

Twelve Roboto TTFs, Thin through Black with italics, added on 2026-09-06 while considering a
typeface change. **Nothing in the build references them.**

The platform self-hosts its faces as subset **woff2** in `web/public/fonts/`, written by
`scripts/fetch_fonts.py`, because the demo makes zero network calls. These are unsubset TTFs at
about 167 KB each against roughly 20 KB for a woff2 weight, so they would need converting and
subsetting to latin before they could ship.

They are kept here rather than deleted so the option stays open. If the swap ever happens,
`scripts/fetch_fonts.py` and `web/public/fonts.css` are the two files that own it.
