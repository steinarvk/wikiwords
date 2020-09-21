import click
import logging
import string
import sys
import json

import parse
import sharding
import freqlist
import wordtrie

logging.basicConfig(level="INFO")

@click.group()
def main():
    pass

@main.command()
@click.argument("filename")
def read_dump(filename):
    n = 0
    for word in parse.words_in_dump(filename):
        n += 1
    print(n, "words processed")

@main.command()
@click.option("--shard", default=None, type=str)
@click.option("--limit", default=None, type=int)
@click.argument("filename")
def count_words_in_dump(filename, shard, limit):
    sharder = sharding.compose(sharding.from_spec(shard), sharding.limiter(limit))
    wc = parse.count_words_in_dump(filename, sharder=sharder)
    for word, count in wc.most_common():
        print(word, count)

@main.command()
@click.argument("filename")
def count_words_in_article(filename):
    with open(filename, "r") as f:
        wt = f.read()
        wc = parse.count_words(parse.words_in_article(wt))
        for word, count in wc.most_common():
            print(word, count)

@main.command()
@click.argument("filename")
def clean_article(filename):
    with open(filename, "r") as f:
        wt = f.read()
        print(parse.clean_wiki_article(wt))

@main.command()
def word_list_to_letter_distribution():
    inp = sys.stdin
    ctr = freqlist.letter_distribution(freqlist.read(inp))
    total = sum(ctr.values())
    for letter, count in ctr.most_common():
        print(letter, 100 * count/total)

@main.command()
def word_list_to_trie():
    inp = sys.stdin
    out = sys.stdout
    json.dump(wordtrie.Trie(w for w, _ in freqlist.read(inp)).export(), out)

@main.command()
@click.argument("words")
def intersect_word_list(words):
    rv = set()
    with open(words, "r") as f:
        for line in f:
            word = line.strip().lower()
            rv.add(word)
    inp = sys.stdin
    for word, count in freqlist.read(inp):
        if word in rv:
            print(word, count)

@main.command()
@click.option("--max-length", default=None, type=int)
@click.option("--min-length", default=None, type=int)
@click.option("--only-letters", default=None, type=str)
@click.option("--only-extra-letters", default=None, type=str)
@click.option("--min-freq", default=None, type=int)
@click.option("--contains-any-of", default=None, type=str)
@click.option("--regex-blocklist-filename", default=None, type=str)
def clean_word_list(max_length, min_length, only_letters, only_extra_letters, min_freq, regex_blocklist_filename, contains_any_of):
    filts = []
    if max_length:
        filts.append(freqlist.MaxLength(max_length))
    if min_length:
        filts.append(freqlist.MinLength(min_length))
    if only_letters:
        filts.append(freqlist.ContainingOnlyLetters(only_letters.lower()))
    if only_extra_letters:
        filts.append(freqlist.ContainingOnlyLetters(string.ascii_lowercase + only_extra_letters.lower()))
    if contains_any_of:
        filts.append(freqlist.ContainsAnyOfFilter(contains_any_of))
    if min_freq:
        filts.append(freqlist.MinFreq(min_freq))
    if regex_blocklist_filename:
        with open(regex_blocklist_filename, "r") as f:
            regexes = []
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                regexes.append(line)
        filts.append(freqlist.RegexBlocklistFilter(regexes))
    filt = freqlist.CompositeFilter(*filts)
    inp = sys.stdin
    out = sys.stdout
    freqlist.write(freqlist.filter(freqlist.read(inp), filt), out)
    
if __name__ == "__main__":
    main()

