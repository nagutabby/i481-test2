import pytest # type: ignore[import-not-found]

from src.acquire import *
from src.inspect import *
from utils.buffer import *

def setup_test_data():
    # テストデータの準備
    # fvの定義 - 連続する時刻範囲 (HHMM形式、10分間隔)
    fv0 = ((1200, 1210), 1)    # 12:00から12:10
    fv1 = ((1210, 1220), 1)    # 12:10から12:20
    fverr = ((1210, 1200), 1)  # エラーケース：終了時刻が開始時刻より小さい

    # cvの定義
    cv0 = (1, (95, 105, -10, 10))    # (timing, window values)
    cv1 = (2, (195, 205, -20, 20))
    cvdef = (1, (0, 100, -50, 50))   # デフォルト値
    cverr = (1, (0, 0, 0, 0))        # エラー時の値

    # sv, svnの定義（m11用）
    sv0 = SV([10, 20, 30, 40])
    sv1 = SV([15, 25, 35, 45])
    svn0 = SV([10, 20, 30, 40])  # sv0と同じ値
    svn1 = SV([15, 25, 35, 45])  # sv1と同じ値

    return [
        # 1. 空のリスト - 正常系
        (
            [],             # lfv
            [cvdef],       # lcv
            [sv0],         # lsv
            [svn0]         # lsvn
        ),
        # 2. 単一要素 - 正常系
        (
            [fv0],         # lfv
            [cv0],         # lcv
            [sv0],         # lsv
            [svn0]         # lsvn
        ),
        # 3. 複数要素 - 正常系
        (
            [fv0, fv1],    # lfv: 1200->1210->1220 と10分間隔で連続
            [cv0, cv1],    # lcv
            [sv0, sv1],    # lsv
            [svn0, svn1]   # lsvn
        ),
        # 4. 異常系
        (
            [fv0, fverr],  # lfv
            [cv0, cverr],  # lcv
            [sv0, sv1],    # lsv
            [svn0, svn1]   # lsvn
        )
    ]

class TestInspect():
    fbuf = Buffer()
    cbuf = Buffer()
    hbuf = Buffer()
    isp = Inspect(fbuf,cbuf,hbuf)

    # for m11 (temporally)
    sen = Buffer()
    act = Buffer()
    sbuf = Buffer()
    acq = Acquire(sen, act, sbuf)

    args_m21_m11_seq = setup_test_data()

    @pytest.fixture()
    def trace(self, **args):
        # setup
        print(f"\nsetup :")
        self.fbuf.clear()
        self.cbuf.clear()
        self.hbuf.clear()
        self.sbuf.clear()
        yield
        # teardown
        print(f"\nteardown :")

    @pytest.mark.parametrize("test_input", args_m21_m11_seq)
    def test_m21_m11(self, test_input):
        # テストデータの展開
        lfv, lcv, lsv, lsvn = test_input

        # m21の実行
        lhv = [(1, (0, 0, 0, 0)) for _ in range(max(1, len(lfv)))]

        # テストケースごとにfvcを初期化
        if not lfv:
            # 空のリストの場合
            self.isp.fvc = ((0, 0), 0, 0)
            result = self.isp.m21(lfv, lcv, lhv)
            assert result == 0, "Empty list case should return 0"
            return
        else:
            # 最初のfvの1つ前の10分間を設定
            first_start = lfv[0][0][0]  # 最初のfvの開始時刻
            prev_start = first_start - 10  # 10分前
            self.isp.fvc = ((prev_start, first_start), 1, 0)

        result = self.isp.m21(lfv, lcv, lhv)

        # m21の結果の検証
        def check_conditions(rnc, rne):
            cb, ce = rnc
            eb, ee = rne
            # 3つの条件をすべて満たすか確認
            return (eb < ee) and (cb < eb) and (ce == eb)

        is_error = False
        if len(lfv) > 0:
            # 最初のケースは現在のfvc状態と比較
            cb, ce = self.isp.fvc[0]
            eb, ee = lfv[0][0]
            if not check_conditions((cb, ce), (eb, ee)):
                is_error = True

            # 連続するfvの時刻関係をチェック
            for i in range(len(lfv)-1):
                cb, ce = lfv[i][0]        # 現在のfv
                eb, ee = lfv[i+1][0]      # 次のfv
                if not check_conditions((cb, ce), (eb, ee)):
                    is_error = True
                    break

        if is_error:  # エラーケース
            assert result < 0, "Error case should return negative value"
            return
        else:
            assert result == 0, "Normal case should return 0"

        # m11の実行と検証
        for sv, svn in zip(lsv, lsvn):
            sv_copy = SV(sv.val[:])
            svn_copy = SV(svn.val[:])

            dv = DV([1,1,1,1])
            self.acq.m11(0, dv.val, sv_copy.val, svn_copy.val)

            # m11の結果の検証
            assert svn_copy.val == svn.val, "m11 should set correct values"

    def test_m21e(self):
        # 基本となるテストデータ
        t = 100
        cve = (90, (10, 20, 30, 40))
        hve = (95, (15, 25, 35, 45))

        # ケース1: 正常系 (戻り値: 0)
        # 条件: eb < ee, cb < eb, ce == eb
        fvc = ((1205, 1210), 45)   # rnc = (5, 10)
        fve = ((1210, 1220), 50)  # rne = (10, 20)

        result = self.isp.m21e(t, fve, fvc, cve, hve)
        assert result == 0, "正常系のテストが失敗"

        # ケース2: エラー系 (戻り値: -1)
        # 条件: eb >= ee をテスト
        fvc = ((1205, 1220), 45)   # rnc = (5, 20)
        fve = ((1220, 1210), 50)  # rne = (20, 10): 開始時刻 >= 終了時刻
        result = self.isp.m21e(t, fve, fvc, cve, hve)
        assert result == -1, "f1のエラーケースのテストが失敗"

        # ケース3: エラー系 (戻り値: -2)
        # 条件: cb >= eb をテスト
        fvc = ((1215, 1225), 45)  # rnc = (15, 25): 現在の開始時刻 >= 次の開始時刻
        fve = ((1210, 1220), 50)  # rne = (10, 20)
        result = self.isp.m21e(t, fve, fvc, cve, hve)
        assert result == -2, "f2のエラーケースのテストが失敗"

        # ケース4: エラー系 (戻り値: -3)
        # 条件: ce != eb をテスト
        fvc = ((1205, 1210), 45)   # rnc = (5, 10): 現在の終了時刻 != 次の開始時刻
        fve = ((1215, 1225), 50)  # rne = (15, 25)
        result = self.isp.m21e(t, fve, fvc, cve, hve)
        assert result == -3, "f3のエラーケースのテストが失敗"
