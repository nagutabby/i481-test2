from dataclasses import dataclass, field
import copy

@dataclass
class Event():
    _r:int = 0
    _v = [1,2,4,8,16,32,64,128]
    def set(self,k):
        self._r |= self._v[k]

    def reset(self,k):
        self._r &= ~self._v[k]

    def isSet(self,k):
        return (self._r & self._v[k])>0

    def __str__(self):
        return ''.join("-o"[self.isSet(k)] for k in range(8))

def main():
    e1 = Event()
    e2 = Event()
    print(f"e1={e1} e2={e2}")
    e1.set(0)
    print(f"e1={e1} e2={e2}")
    e1.set(2)
    print(f"e1={e1} e2={e2}")
    e2.set(1)
    print(f"e1={e1} e2={e2}")
    e2.set(3)
    print(f"e1={e1} e2={e2}")
    e1.reset(0)
    print(f"e1={e1} e2={e2}")
    e1.reset(2)
    print(f"e1={e1} e2={e2}")
    print(f"{e1.isSet(1)} {e2.isSet(1)}")

    print(e2._r)

if __name__ == '__main__':
    main()
