def parse_spec(s):
  a, b = s.split("/")
  return int(a), int(b)

def compose(*sharders):
    sharders = [x for x in sharders if x]
    if not sharders:
        return identity
    def f(stream):
        for sharder in sharders:
            stream = sharder(stream)
        return stream
    return f

def from_spec(spec):
    if spec:
        a, b = parse_spec(spec)
        return sharder(a, b)

def identity(x):
    return x

def limiter(n):
    def f(stream):
        ctr = 0
        for x in stream:
            ctr += 1
            if ctr > n:
                break
            yield x
    return f

def sharder(a, b):
    assert b > 0
    assert 0 <= a < b
    def f(stream):
        ctr = 0
        for x in stream:
            if (ctr % b) == a:
                yield x
            ctr += 1
    return f
