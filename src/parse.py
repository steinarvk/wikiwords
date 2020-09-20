import bz2
import defusedxml.ElementTree
import mwparserfromhell
import sys
import logging
import nltk.tokenize
import re
import collections

def count_words(xs):
    return collections.Counter(xs)

def article_to_tokens(article):
    plaintext = clean_wiki_article(article)
    for word in nltk.tokenize.wordpunct_tokenize(plaintext):
        yield word

def words_in_article(article):
    for tok in article_to_tokens(article):
        if not tok.isalpha():
            continue
        if tok[0].isupper():
            # A crude filter to avoid proper nouns.
            continue
        yield tok.lower()

def articles_to_words(articles):
    for article in articles:
        for word in words_in_article(article):
            yield word

def _children(node):
    try:
        return node.nodes
    except AttributeError:
        return node.__children__()

def _visible_children(node):
    if node.__class__ == mwparserfromhell.nodes.Wikilink:
        yield (node.text or node.title)
    else:
        for x in _children(node):
            yield x

def show_wiki_tree(node, indent="", f=None):
    try:
        name = node.tag
    except AttributeError:
        name = None
    print(indent, node.__class__.__name__, name, repr(str(node)[:30]), file=f)
    for sub in _children(node):
        show_wiki_tree(sub, indent=indent + "  ", f=f)

_ERROR_MESSAGE_SNIPPET_LENGTH = 1024

def visit_wiki_tree(node, allow_types, allow_tags, exclude_links_pattern, visitor):
    ok = node.__class__.__name__ in allow_types
    if node.__class__ == mwparserfromhell.nodes.Tag:
        ok = ok and (node.tag.lower() in allow_tags)
    if ok and exclude_links_pattern:
        if node.__class__ == mwparserfromhell.nodes.Wikilink:
            target = str(node.title)
            hit = exclude_links_pattern.match(target)
            ok = not hit
    if node.__class__ == mwparserfromhell.nodes.text.Text:
        if str(node).strip().startswith("{|"):
            logging.warning("Bad parse in article, near: %s", repr(str(node)[:_ERROR_MESSAGE_SNIPPET_LENGTH]))
    if not ok:
        return
    visitor(node)
    for sub in _visible_children(node):
        visit_wiki_tree(sub, allow_types, allow_tags, exclude_links_pattern, visitor)

def text_in_wiki_node(node):
    rv = []
    bad_parse_workaround = [0]
    def visit(x):
        if x.__class__ == mwparserfromhell.nodes.text.Text:
            t = str(x)
            # Sometimes sections containing {| |} (notably tables) are parsed
            # as Text nodes. This probably shouldn't happen -- or maybe the
            # markup is technically somehow incorrect such that it's actually
            # the correct parse. Either way, we don't want that table data.
            # Exclude it.
            bad_parse_workaround[0] += t.count("{|")
            if not bad_parse_workaround[0]:
                rv.append(t)
            bad_parse_workaround[0] -= t.count("|}")
    visit_wiki_tree(node,
        allow_types=("Text", "Tag", "Wikicode", "Wikilink"),
        allow_tags=("li", "b", "i"),
        exclude_links_pattern=re.compile(".*:.*"),
        visitor=visit,
    )
    return "".join(rv)

def clean_wiki_article(article):
    parsed = mwparserfromhell.parse(article)
    return text_in_wiki_node(parsed)

def _raw_articles_in_dump(bz2filename):
    with bz2.BZ2File(bz2filename) as f:
        last_title = None
        for _, el in defusedxml.ElementTree.iterparse(f):
            if el.tag.endswith("}title"):
                last_title = el.text
            if not el.tag.endswith("}text"):
                continue
            yield last_title, el.text
            last_title = None

def articles_in_dump(bz2filename, sharder=None):
    rv = _raw_articles_in_dump(bz2filename)
    if sharder:
        rv = sharder(rv)
    return rv

def wordsequences_in_dump(bz2filename, sharder=None):
    totalbytes, totalwords, totalarts = 0, 0, 0
    for title, art in articles_in_dump(bz2filename, sharder=sharder):
        if not art:
            logging.warning("Article %s is missing body", title)
            continue
        thisbytes = len(art)
        words = list(words_in_article(art))
        thiswords = len(words)
        yield title, words
        logging.info("Processed %s (#%d): %d words (%d unique) and %d bytes, %d total words seen, %d total bytes", repr(title), totalarts, len(words), len(set(words)), thisbytes, totalwords, totalbytes)
        totalarts += 1
        totalwords += len(words)
        totalbytes += thisbytes

def words_in_dump(bz2filename):
    for title, wordseq in wordsequences_in_dump(bz2filename):
        for word in wordseq:
            yield word

def count_words_in_dump(bz2filename, sharder=None):
    ctr = collections.Counter()
    for title, wordseq in wordsequences_in_dump(bz2filename, sharder=sharder):
        for word in wordseq:
            ctr[word] += 1
        logging.info("Processed %s: %d unique words seen", repr(title), len(ctr))
    return ctr
