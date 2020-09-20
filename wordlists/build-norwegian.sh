#!/bin/bash
SOURCE="nowiki-latest-pages-articles-multistream.xml.bz2"
TARGET_RAW="norwegian.freq.raw.txt"
TARGET_CLEAN="norwegian.freq.txt"
TARGET_LDIST="norwegian.letterdist.txt"
sha256sum "${SOURCE}" > "norwegian.source.sha256.txt"
python ../src/main.py count-words-in-dump "${SOURCE}" > "${TARGET_RAW}"
python ../src/main.py clean-word-list \
  --min-freq 100 \
  --only-extra-letters æøå \
  --regex-blocklist-filename ../blocklists/non-norwegian.blocklist \
  --contains-any-of aeiouyæøå < "${TARGET_RAW}" > "${TARGET_CLEAN}"
python ../src/main.py word-list-to-letter-distribution < "${TARGET_CLEAN}" > "${TARGET_LDIST}"
