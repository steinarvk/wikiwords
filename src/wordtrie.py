class Trie(object):
    def __init__(self, words=()):
        self.child = {}
        for word in words:
            self.add(word)

    def add(self, word):
        if not word:
            return
        first = word[0]
        rest = word[1:]
        try:
            ch = self.child[first]
        except KeyError:
            ch = Trie()
            self.child[first] = ch
        ch.add(rest)
    
    def export(self):
        return {k: v.export() for k, v in self.child.items()}
