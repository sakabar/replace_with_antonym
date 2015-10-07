#coding: utf-8
import re
import unittest
import main

class TestMain(unittest.TestCase):
    # def setUp(self):
    #   #初期化処理
    #   pass

    # def tearDown(self):
    #   #終了処理
    #   pass

    def test_search_lemma0(self):
        lemma = "好く"
        line = '(副詞 ((読み おりよく)(見出し語 折好く おり好く 折よく おりよく)(意味情報 "代表表記:折好く/おりよく")))'
        self.assertFalse(main.search_lemma(lemma, line))

    def test_search_lemma1(self):
        lemma = "来る"
        line = '(連体詞 ((読み きたるべき)(見出し語 来るべき きたるべき)(意味情報 "代表表記:来るべき/きたるべき")))'
        self.assertFalse(main.search_lemma(lemma, line))

    def test_search_lemma2(self):
        lemma = "来る"
        line = '(動詞 ((読み 来る)(見出し語 (来る 0.8))(活用型 カ変動詞来)(意味情報 "代表表記:来る/くる 反義:動詞:帰る/かえる")))'
        self.assertTrue(main.search_lemma(lemma, line))




    def test_get_katuyou_type0(self):
#         disamgibuated_juman_lines ="""
# あの あの あの 指示詞 7 連体詞形態指示詞 2 * 0 * 0 NIL
# 料理 りょうり 料理 名詞 6 サ変名詞 2 * 0 * 0 "代表表記:料理/りょうり カテゴリ:人工物-食べ物;抽象物 ドメイン:料理・食事"
# を を を 助詞 9 格助詞 1 * 0 * 0 NIL
# 嫌って きらって 嫌う 動詞 2 * 0 子音動詞ワ行 12 タ系連用テ形 14 "代表表記:嫌う/きらう 反義:動詞:好く/すく"
# いた いた いる 接尾辞 14 動詞性接尾辞 7 母音動詞 1 タ形 10 "代表表記:いる/いる"
# 。 。 。 特殊 1 句点 1 * 0 * 0 NIL
# EOS
# """[1:-1].split('\n') #初めの改行をカット
        lemma = "好く"
        pos = "動詞"
        self.assertEquals(main.get_katuyou_type(lemma, pos),"子音動詞カ行")


if __name__ == '__main__':
    unittest.main() # シンプルな出力でいい場合

    #詳細
    # unittest.main(verbosity=2, buffer=True)
