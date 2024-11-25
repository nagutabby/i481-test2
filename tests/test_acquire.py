import pytest # type: ignore[import-not-found]

from src.acquire import *
from utils.buffer import *

def setup_test_data():
    # テストデータの準備
    sv0 = SV([120, 220, 320, 420])
    sv1 = SV([130, 230, 330, 430])
    avn0 = AV([10, 20, 30, 40])
    avn1 = AV([10, 20, 30, 40])
    sverr = SV([999, 0, 0, 0])
    avndef = AV([255, 0, 0, 0])

    args_m11_m12_seq = [
        # 1. 空のリスト
        ([], []),

        # 2. 単一要素の正常系
        ([(2, sv0)], [(2, avn0)]),

        # 3. 複数要素の正常系
        ([(2, sv0), (3, sv1)], [(2, avn0), (3, avn1)]),

        # 4. エラー値のみ
        ([(2, sverr)], [(2, avndef)]),

        # 5. エラー値と正常値の組み合わせ（エラー値が先）
        ([(2, sverr), (3, sv1)], [(2, avndef), (3, avn1)]),

        # 6. エラー値と正常値の組み合わせ（正常値が先）
        ([(2, sv0), (3, sverr)], [(2, avn0), (3, avndef)]),
    ]
    return args_m11_m12_seq


class TestAcquire():
    sen = Buffer()
    act = Buffer()
    sbuf = Buffer()
    acq = Acquire(sen, act, sbuf)
    args_m11_m12_seq = setup_test_data()

    @pytest.fixture()
    def trace(self, **args):
        # setup
        print(f"\nsetup :")
        self.sen.clear()
        self.act.clear()
        self.sbuf.clear()
        yield
        # teardown
        print(f"\nteardown :")

    @pytest.mark.parametrize("test_input", args_m11_m12_seq)
    def test_m11_m12(self, test_input):
        current_value = 10

        # WVの定義
        wv0 = (95, 105, -10, 10)
        wv1 = (195, 205, -20, 20)
        wv2 = (295, 305, -30, 30)
        wv3 = (395, 405, -40, 40)
        m12_wv = WV([wv0, wv1, wv2, wv3])
        m11_m12_dv = DV([1,1,1,1])

        lsv, lavn = test_input

        # 空のリストのテストケース
        if not lsv:
            # 初期値を持つSVとAVを作成
            sv_empty = SV([])
            av_empty = AV([])
            # コピーを作成
            sv_copy = SV(sv_empty.val[:])
            av_copy = AV(av_empty.val[:])
            # 空のリストで実行
            self.acq.m11(current_value, m11_m12_dv.val, sv_copy.val, av_copy.val)
            self.acq.m12(current_value, m12_wv.val, sv_copy.val, av_copy.val)
            # 値が変更されていないことを確認
            assert sv_copy.val == sv_empty.val, "Empty list should not change SV values"
            assert av_copy.val == av_empty.val, "Empty list should not change AV values"
            return

        # その他のテストケース
        for (timing, sv), (_, av) in zip(lsv, lavn):
            sv_copy = SV(sv.val[:])
            av_copy = AV(av.val[:])

            self.acq.m11(current_value, m11_m12_dv.val, sv_copy.val, av_copy.val)
            self.acq.m12(current_value, m12_wv.val, sv_copy.val, av_copy.val)

            # エラー値かどうかでアサーション
            if sv.val[0] == 999:  # エラー値の場合
                assert av_copy.val == [255, 0, 0, 0], f"Error case with timing {timing} failed"
            else:  # 正常値の場合
                assert av_copy.val == av.val, f"Normal case with timing {timing} failed"
