#coding: utf-8
import re
import unittest
import replace_lib

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
        self.assertFalse(replace_lib.search_lemma(lemma, line))

    def test_search_lemma1(self):
        lemma = "来る"
        line = '(連体詞 ((読み きたるべき)(見出し語 来るべき きたるべき)(意味情報 "代表表記:来るべき/きたるべき")))'
        self.assertFalse(replace_lib.search_lemma(lemma, line))

    def test_search_lemma2(self):
        lemma = "来る"
        line = '(動詞 ((読み 来る)(見出し語 (来る 0.8))(活用型 カ変動詞来)(意味情報 "代表表記:来る/くる 反義:動詞:帰る/かえる")))'
        self.assertTrue(replace_lib.search_lemma(lemma, line))




    def test_get_katuyou_type0(self):
        lemma = "好く"
        pos = "動詞"
        self.assertEquals(replace_lib.get_katuyou_type(lemma, pos),"子音動詞カ行")

    def test_extract_antonym_from_token_line0(self):
        ind = 0
        token_line = '守る まもる 守る 動詞 2 * 0 子音動詞ラ行 10 基本形 2 "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる"'

        actual = replace_lib.extract_antonym_from_token_line(ind, token_line)
        expected = [(0, "動詞", "攻める", "せめる"), (0, "動詞", "破る", "やぶる")]
        self.assertEquals(actual, expected)


if __name__ == '__main__':
    unittest.main() # シンプルな出力でいい場合

    #詳細
    # unittest.main(verbosity=2, buffer=True)
