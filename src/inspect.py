from dataclasses import dataclass, field
import copy

from src.acquire import *
from utils.buffer import *

class Inspect():
    def __init__(self,fbuf,cbuf,hbuf):
        self.fbuf = fbuf
        self.cbuf = cbuf
        self.hbuf = hbuf
        self.fvc = ((0,0),0,0) # rn=(b,e), dv, wv
        self.svc = SV([0] * 4)

    def f1(self,rnc,rne):
        cb,ce = rnc
        eb,ee = rne
        return eb >= ee

    def f2(self,rnc,rne):
        cb,ce = rnc
        eb,ee = rne
        return cb >= eb

    def f3(self,rnc,rne):
        cb,ce = rnc
        eb,ee = rne
        return not (ce==eb)

    def m21c(self,rnc,rne):
        if self.f1(rnc,rne):
            return -1
        if self.f2(rnc,rne):
            return -2
        if self.f3(rnc,rne):
            return -3
        return 0

    def m21e(self, t: int, fve: tuple[tuple[int, int], int], fvc: tuple[tuple[int, int], int], cve: tuple[int, tuple[int, int, int, int]], hve: tuple[int, tuple[int, int, int, int]]):
        rnc, *_ = fvc
        rne, *_ = fve
        return self.m21c(rnc, rne)


    def m21(self, lfv: list[tuple[tuple[int, int], int]], lcv: list[tuple[int, tuple[int, int, int, int]]], lhv: list[tuple[int, tuple[int, int, int, int]]]) -> int:
        """
        設定ファイルの各行をチェックし、cbufとhbufに送る値を設定する関数

        Args:
            lfv: 設定ファイルの全行のリスト [FVE]
            lcv: cbufに送る値のリスト [CVE] (出力)
            lhv: hbufに送る値のリスト [HVE] (出力)

        Returns:
            int: エラーがある場合は負の値、成功時は0
        """
        # lfvの各行についてチェック
        for i, fve in enumerate(lfv):
            # m21eを呼び出してチェック
            result = self.m21e(0, fve, self.fvc, lcv[i], lhv[i])
            if result < 0:
                return result  # エラーがあった場合は即座に終了

            # チェックが成功した場合、必要に応じてlcvとlhvを更新
            # ※ 具体的な更新ロジックはm21eの実装に依存

        return 0  # すべてのチェックが成功

    def m21_glue(self, t):
        pass

    # TODO: modify das122 to get cv=(dv,wv) from cbuf
    # m11(self, cur, dv, sv, svc):

    sen = Buffer()
    act = Buffer()
    sbuf = Buffer()
    acq = Acquire(sen,act,sbuf)

    dv = [2, 3, 4, 5]
    sv = SV([100,200,300,400])
    svc = SV([120,200,300,400])

    """
    # codes in das122
    dv = [2, 3, 4, 5] # must be get from cbuf
    def m11_glue(self,t):
        sv = self.sen.get()
        print(f"\n  sv={sv} svc={self.svc} ",end='')
        self.m11(t, self.dv, sv, self.svc)
        print(f"\n  m11:svc={self.svc} avc={self.avc} ",end='')
        svn = copy.deepcopy(self.svc)
        self.sbuf.put(svn)
        print(f"\n  sbuf={self.sbuf}",end='')
    """

    def m11_glue_tmp(self,t):
        # TODO: fix
        self.acq.m11(t, self.dv, self.sv, self.svc)

    def main(self):
        for t in range(0,self.fbuf.size()):
            print(f"\nt={t}: ", end='')
            self.m21_glue(t)
            # TODO: connect
            self.m11_glue_tmp(t)

