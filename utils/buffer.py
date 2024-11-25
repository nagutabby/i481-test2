from dataclasses import dataclass, field
import copy
import sys

@dataclass
class C(): # generic container
    val:int = 0

@dataclass
class _V(): # abstract base class for vectors
    val:list[int] = field(default_factory=list)

    def __str__(self):
        return f"{self.__class__.__name__}({self.val})"

    def __getitem__(self,k):
        return self.val[k]

    def __setitem__(self,k,v):
        self.val[k]=v

@dataclass()
class SV(_V):
    pass

@dataclass()
class AV(_V):
    pass

@dataclass()
class DV(_V):
    pass

@dataclass()
class WV(_V):
    pass

@dataclass
class Buffer():
    len: int = 0
    rp: int = 0
    wp: int = 0
    rep: list[_V] = field(default_factory=list)

    # temporally
    def __post_init__(self):
        if self.len == 0:
            self.len = 16
        if len(self.rep) == 0:
            self.rep = [0] * self.len
        self.len = len(self.rep)

    def clear(self):
        self.rp = self.wp = 0

    def all(self):
        if self.rp <= self.wp:
            return self.rep[self.rp:self.wp]
        else:
            return self.rep[self.wp:(self.rp+self.len)]

    def size(self):
        if self.rp <= self.wp:
            return self.wp - self.rp
        else:
            return (self.wp+self.len) - self.rp

    def __str__(self):
        return f"Buffer(rp={self.rp}, wp={self.wp}, rep={self.rep[:self.wp]})"

    def put(self,v):
        self.rep[self.wp] = v
        self.wp += 1
        if self.wp >= self.len:
            self.wp -= self.len

    def get(self):
        v = self.rep[self.rp]
        self.rp += 1
        if self.rp >= self.len:
           self.rp -= self.len
        return v

    def cmp(self,lv):
        r = True
        for l in range(self.size()):
            if not (self.rep[l] == lv[l]):
                r = False
        return r

# usage
def main():
    c = C(0)
    print(f"c={c}")
    c.val = "abc"
    print(f"c={c}")
    print()
    b1 = Buffer()
    print(f"b1={b1!r}")
    b2 = Buffer(len=32)
    print(f"b2={b2}")

    b1.put([1])
    print(f"b1={b1}")
    b2.put([[1,2],[3,4]])
    print(f"b2={b2}")
    b1.rep = [1, 2, 3] # illegal
    b1.rp = 2 # illegal
    print(f"b1={b1}")
    print(f"b1.all()={b1.all()}")

if __name__ == '__main__':
    main()
