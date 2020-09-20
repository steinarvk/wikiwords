import collections
import re
import sys

def read(f):
    for line in f:
        word, freq = line.strip().split()
        freq = int(freq)
        yield word, freq

def write(lst, f):
    for word, freq in lst:
        print(word, freq)

class ContainingOnlyLetters(object):
    def __init__(self, letters):
        self.letters = letters

    def __call__(self, word, freq):
        return not (set(word) - set(self.letters))

class MinLength(object):
    def __init__(self, min_length):
        self.min_length = min_length

    def __call__(self, word, freq):
        return len(word) >= self.min_length

class MaxLength(object):
    def __init__(self, max_length):
        self.max_length = max_length

    def __call__(self, word, freq):
        return len(word) <= self.max_length

class MinFreq(object):
    def __init__(self, min_freq):
        self.min_freq = min_freq

    def __call__(self, word, freq):
        return freq >= self.min_freq

class CompositeFilter(object):
    def __init__(self, *filts):
        self.filts = filts

    def __call__(self, word, freq):
        for filt in self.filts:
            if not filt(word, freq):
                return False
        return True

class RegexBlocklistFilter(object):
    def __init__(self, block_patterns):
        self.patterns = [re.compile(pat) for pat in block_patterns]

    def __call__(self, word, freq):
        for pat in self.patterns:
            if pat.match(word):
                return False
        return True

class ContainsAnyOfFilter(object):
    def __init__(self, letters):
        self.letters = letters

    def __call__(self, word, freq):
        if not (set(word) & set(self.letters)):
            return False
        return True

def filter(lst, filt):
    for word, freq in lst:
        if filt(word, freq):
            yield word, freq

def letter_distribution(lst):
    ctr = collections.Counter()
    for word, freq in lst:
        for letter in word:
            ctr[letter] += freq
    return ctr
