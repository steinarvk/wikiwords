# wikiwords

Software to extract a word list from a Wikipedia data dump.

This software was written to construct a quick-and-dirty
word list with frequency information and no stemming or
lemmatization (i.e. including inflected forms -- suitable for
applications such as spellchecking or word games).

The software was written with Norwegian (nowiki) in mind,
but the same process would likely work for other similar
languages. It was not written with the scale of something
like enwiki in mind.

The accuracy of the generated word lists, including the one(s)
distributed along with the program, cannot be guaranteed.
Invalid words may be included and valid words may be excluded.
If your application requires high accuracy, use a different
approach.

## How to generate a word list

See wordlists/ for an example generated word list and the
script that generates it. You will need to download a
wiki data dump to use as a data source, e.g. from:
  https://dumps.wikimedia.org/nowiki/latest/ 
