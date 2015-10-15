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
        yomi = 'よく'
        line = '(副詞 ((読み おりよく)(見出し語 折好く おり好く 折よく おりよく)(意味情報 "代表表記:折好く/おりよく")))'
        self.assertFalse(replace_lib.search_lemma(lemma, yomi, line))

    def test_search_lemma1(self):
        lemma = "来る"
        yomi = "くる"
        line = '(連体詞 ((読み きたるべき)(見出し語 来るべき きたるべき)(意味情報 "代表表記:来るべき/きたるべき")))'
        self.assertFalse(replace_lib.search_lemma(lemma, yomi, line))


    #ContentW.dicの「来る/くる」に対応する行は読みが「来る」(漢字)になっているため、
    #ヒットしない
    #FIXME 問い合わせた。
    # def test_search_lemma2(self):
    #     lemma = "来る"
    #     yomi = "くる"

    #     #「読み」に漢字が入っている。バグ? → 森田さんに問い合わせた。
    #     # line = '(動詞 ((読み 来る)(見出し語 (来る 0.8))(活用型 カ変動詞来)(意味情報 "代表表記:来る/くる 反義:動詞:帰る/かえる")))'
    #     self.assertTrue(replace_lib.search_lemma(lemma, yomi, line))

    def test_search_lemma3(self):
        lemma = "歩く"
        yomi = "あるく"
        line = '(動詞 ((読み あるく)(見出し語 歩く あるく)(活用型 子音動詞カ行)(意味情報 "代表表記:歩く/あるく")))'

        self.assertTrue(replace_lib.search_lemma(lemma, yomi, line))


    def test_get_katuyou_type0(self):
        lemma = "好く"
        yomi = "すく"
        pos = "動詞"
        self.assertEquals(replace_lib.get_katuyou_type(lemma, yomi, pos),"子音動詞カ行")

    # def test_get_katuyou_type1(self):
    #     lemma = "不"
    #     pos = "動詞"
    #     self.assertEquals(replace_lib.get_katuyou_type(lemma, pos),"子音動詞カ行")

    def test_extract_antonyms_from_token_line0(self):
        ind = 0
        token_line = '守る まもる 守る 動詞 2 * 0 子音動詞ラ行 10 基本形 2 "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる"'

        actual = replace_lib.extract_antonyms_from_token_line(ind, token_line)
        expected = [(0, "動詞", "攻める", "せめる"), (0, "動詞", "破る", "やぶる")]
        self.assertEquals(actual, expected)

    #UNNEED
    # def test_search_word_from_juman_dic0():
    #     pos = "動詞"
    #     lemma = "歩く"
    #     yomi = "あるく"
    #     actual = replace_lib.search_word_from_juman_dic(pos, lemma, yomi)
    #     expected = '歩く あるく 歩く 動詞 * * * 子音動詞カ行 * 基本形 * "代表表記:歩く/あるく"'

if __name__ == '__main__':
    unittest.main() # シンプルな出力でいい場合

    #詳細
    # unittest.main(verbosity=2, buffer=True)
