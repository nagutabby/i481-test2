from dataclasses import dataclass, field
import copy

from utils.buffer import *

class Acquire():
    def __init__(self,sen,act,sbuf):
        self.sen = sen
        self.act = act
        self.sbuf = sbuf
        self.svc = SV([0] * 4)
        self.avc = AV([0] * 4)

    # used as constants (cbuf is optional)
    dv = [2, 3, 4, 5]
    wv = [
        (50, 150, 10, -10),
        (150, 250, 20, -20),
        (250, 350, 30, -30),
        (350, 450, 40, -40)
    ]

    def m11e(self, cur: int, dvk: int, svk: int, svkc: C):
        if dvk == 0:
            return -1
        if cur % dvk == 0:
            svkc.val = svk
        return 0

    def m12e(self, cur: int, svk: int, wvk: tuple[int, int, int, int], avkc: C):
        sv_lb,sv_ub,av_lb,av_ub = wvk
        if sv_ub<sv_lb:
            return -1
        if svk<sv_lb:
            avkc.val = av_lb
        if sv_ub<svk:
            avkc.val = av_ub
        return 0

    def m11(self, cur: int, dv: list[int], sv: list[int], svc: list[int]):
        # 空のリストの場合は何もしない
        if not sv:
            return 0

        # エラー値（999）を検出した場合、デフォルト値（255）を設定
        if 999 in sv:
            svc[:] = [255, 0, 0, 0]
            return -1

        svkc = C(0)
        for k, dvk in enumerate(dv):
            svkc.val = svc[k]
            self.m11e(cur, dvk, sv[k], svkc)
            svc[k] = svkc.val
        return 0

    def m12(self, cur: int, wv: list[tuple[int, int, int, int]], sv: list[int], avc: list[int]):
        # 空のリストの場合は何もしない
        if not sv:
            return 0

        # m11でエラーが検出された場合（avc[0] == 255）、処理をスキップ
        if avc[0] == 255:
            return 0

        avkc = C(0)
        for k in range(4):
            avkc.val = avc[k]
            self.m12e(cur, sv[k], wv[k], avkc)
            avc[k] = avkc.val
        return 0


    # glue code: used for connecting thread code
    # buffer->value (m11) value ->buffer

    def m11_glue(self,t):
        sv = self.sen.get()
        print(f"\n  sv={sv} svc={self.svc} ",end='')
        self.m11(t, self.dv, sv, self.svc)
        print(f"\n  m11:svc={self.svc} avc={self.avc} ",end='')
        svn = copy.deepcopy(self.svc)
        self.sbuf.put(svn)
        print(f"\n  sbuf={self.sbuf}",end='')

    def m12_glue(self,t):
        svn = self.sbuf.get()
        self.m12(t, self.wv, svn, self.avc)
        print(f"\n  m12:avc={self.avc} ",end='')
        avn = copy.deepcopy(self.avc)
        self.act.put(avn)

    def main(self):
        for cur in range(0,self.sen.size()):
            print(f"\nt={cur}: ", end='')
            self.m11_glue(cur)
            # TODO: connection
            self.m12_glue(cur)
