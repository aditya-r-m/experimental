class VebTree():
    def __init__(self, lg_u):
        self.lg_u = lg_u
        self.mn = self.mx = None
        if lg_u > 1:
            self.children = [VebTree(lg_u>>1) for _ in range(0, 1<<(lg_u>>1))]
            self.aux = VebTree(lg_u>>1)

    def _split_bits(self, v):
        return v>>(self.lg_u>>1), v&((1<<(self.lg_u>>1)) - 1)

    def _merge_bits(self, l, r):
        return l<<(self.lg_u>>1) | r

    def is_empty(self):
        return self.mn == None

    def successor(self, v):
        if self.is_empty(): return None
        if v < self.mn: return self.mn
        if v >= self.mx: return None
        if self.lg_u == 1: return self.mx
        l, r = self._split_bits(v)
        s = self.children[l].successor(r)
        if s is not None: return self._merge_bits(l, s)
        m = self.aux.successor(l)
        return self._merge_bits(m, self.children[m].mn)

    def insert(self, v):
        if v < 0 or v >= 1<<self.lg_u: raise "insertion out of range"
        if self.is_empty():
            self.mn = self.mx = v
            return
        if v < self.mn:
            v, self.mn = self.mn, v
        if v > self.mx:
            self.mx = v
        if self.lg_u == 1: return
        l, r = self._split_bits(v)
        if self.children[l].is_empty(): self.aux.insert(l)
        self.children[l].insert(r)

    def delete(self, v):
        if v < self.mn or v > self.mx: return
        if self.mn == self.mx:
            self.mn = self.mx = None
            return
        if self.lg_u == 1:
            if v == self.mn: self.mn = self.mx
            else: self.mx = self.mn
            return
        if v == self.mn:
            v = self.mn = self._merge_bits(self.aux.mn, self.children[self.aux.mn].mn)
        l, r = self._split_bits(v)
        self.children[l].delete(r)
        if self.children[l].is_empty(): self.aux.delete(l)
        if v == self.mx:
            if self.aux.is_empty(): self.mx = self.mn
            else: self.mx = self._merge_bits(self.aux.mx, self.children[self.aux.mx].mx)

if __name__ == "__main__":
    tree = VebTree(1<<(1<<(1<<1)))
    while True:
        o, v = input().split()
        if o == 'i': tree.insert(int(v))
        if o == 'd': tree.delete(int(v))
        if o == 's': print(tree.successor(int(v)))

