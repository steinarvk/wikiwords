import click
import logging

import parse
import sharding

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
    
if __name__ == "__main__":
    main()

