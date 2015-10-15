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
        pos = "動詞"
        lemma = "好く"
        yomi = "すく"

        expected = '(動詞 ((読み すく)(見出し語 好く すく)(活用型 子音動詞カ行)(意味情報 "代表表記:好く/すく 反義:動詞:嫌う/きらう")))'
        actual = replace_lib.search_lemma(pos, lemma, yomi)
        self.assertEquals(actual, expected)

    def test_get_katuyou_type_and_info_from_juman_dic0(self):
        lemma = "好く"
        yomi = "すく"
        pos = "動詞"
        actual_katuyou, actual_info = replace_lib.get_katuyou_type_and_info_from_juman_dic(pos, lemma, yomi)
        self.assertEquals(actual_katuyou, "子音動詞カ行")
        self.assertEquals(actual_info, '"代表表記:好く/すく 反義:動詞:嫌う/きらう"')

    def test_extract_antonyms_from_token_line0(self):
        ind = 0
        token_line = '守る まもる 守る 動詞 2 * 0 子音動詞ラ行 10 基本形 2 "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる" <代表表記:守る/まもる><反義:動詞:攻める/せめる;動詞:破る/やぶる><正規化代表表記:守る/まもる><文頭><文末><表現文末><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>'

        actual = replace_lib.extract_antonyms_from_token_line(ind, token_line)
        expected = [(0, "動詞", "攻める", "せめる"), (0, "動詞", "破る", "やぶる")]
        self.assertEquals(actual, expected)

    def test_replace_juman_line_with_antonym0(self):
        line = '守る まもる 守る 動詞 2 * 0 子音動詞ラ行 10 基本形 2 "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる" <代表表記:守る/まもる><反義:動詞:攻める/せめる;動詞:破る/やぶる><正規化代表表記:守る/まもる><文頭><文末><表現文末><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>'
        pos = "動詞"
        lemma = "攻める"
        yomi = "せめる"

        actual = replace_lib.replace_juman_line_with_antonym(line, pos, lemma, yomi)
        expected = '攻める せめる 攻める 動詞 * * * 母音動詞 * 基本形 * "代表表記:攻める/せめる ドメイン:スポーツ 反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ"'
        self.assertEquals(actual, expected)


    def test_replace_juman_line_with_antonym1(self):
        line = '攻めて せめて 攻める 動詞 2 * 0 母音動詞 1 タ系連用テ形 14 "代表表記:攻める/せめる ドメイン:スポーツ 反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ" <代表表記:攻める/せめる><ドメイン:スポーツ><反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ><正規化代表表記:攻める/せめる><文頭><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>'
        pos = "動詞"
        lemma = "守る"
        yomi = "まもる"

        actual = replace_lib.replace_juman_line_with_antonym(line, pos, lemma, yomi)
        expected = '守って まもって 守る 動詞 * * * 子音動詞ラ行 * タ系連用テ形 * "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる"'
        self.assertEquals(actual, expected)




    def test_replace_with_antonym_pairs0(self):
        token_lines = ['あ あ あ 感動詞 12 * 0 * 0 * 0 "代表表記:あ/あ"']
        antonym_pairs = []
        actual = replace_lib.replace_with_antonym_pairs(token_lines, antonym_pairs)
        expected = ['あ あ あ 感動詞 12 * 0 * 0 * 0 "代表表記:あ/あ"']
        self.assertEquals(actual, expected)

    def test_replace_with_antonym_pairs1(self):
        token_lines = ['攻める せめる 攻める 動詞 2 * 0 母音動詞 1 基本形 2 "代表表記:攻める/せめる ドメイン:スポーツ 反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ" <代表表記:攻める/せめる><ドメイン:スポーツ><反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ><正規化代表表記:攻める/せめる><文頭><文末><表現文末><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>']
        antonym_pairs = [(0, "動詞", "守る", "まもる")]
        actual = replace_lib.replace_with_antonym_pairs(token_lines, antonym_pairs)
        expected = ['守る まもる 守る 動詞 * * * 子音動詞ラ行 * 基本形 * "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる"']
        self.assertEquals(actual, expected)

    def test_replace_with_antonym_pairs2(self):
        token_lines = ['攻めろ せめろ 攻める 動詞 2 * 0 母音動詞 1 命令形 6 "代表表記:攻める/せめる ドメイン:スポーツ 反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ" <代表表記:攻める/せめる><ドメイン:スポーツ><反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ><正規化代表表記:攻める/せめる><文頭><文末><表現文末><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>']
        antonym_pairs = [(0, "動詞", "守る", "まもる")]
        actual = replace_lib.replace_with_antonym_pairs(token_lines, antonym_pairs)
        expected = ['守れ まもれ 守る 動詞 * * * 子音動詞ラ行 * 命令形 * "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる"']
        self.assertEquals(actual, expected)

    def test_replace_with_antonym_pairs3(self):
        token_lines = ['攻めて せめて 攻める 動詞 2 * 0 母音動詞 1 タ系連用テ形 14 "代表表記:攻める/せめる ドメイン:スポーツ 反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ" <代表表記:攻める/せめる><ドメイン:スポーツ><反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ><正規化代表表記:攻める/せめる><文頭><文末><表現文末><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>']
        antonym_pairs = [(0, "動詞", "守る", "まもる")]
        actual = replace_lib.replace_with_antonym_pairs(token_lines, antonym_pairs)
        expected = ['守って まもって 守る 動詞 * * * 子音動詞ラ行 * タ系連用テ形 * "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる"']
        self.assertEquals(actual, expected)

    def test_replace_with_antonym_pairs4(self):
        token_lines = ['攻めて せめて 攻める 動詞 2 * 0 母音動詞 1 タ系連用テ形 14 "代表表記:攻める/せめる ドメイン:スポーツ 反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ" <代表表記:攻める/せめる><ドメイン:スポーツ><反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ><正規化代表表記:攻める/せめる><文頭><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>', 'は は は 助詞 9 副助詞 2 * 0 * 0 NIL <文末><表現文末><かな漢字><ひらがな><付属>']
        antonym_pairs = [(0, "動詞", "守る", "まもる")]
        actual = replace_lib.replace_with_antonym_pairs(token_lines, antonym_pairs)
        expected = ['守って まもって 守る 動詞 * * * 子音動詞ラ行 * タ系連用テ形 * "代表表記:守る/まもる 反義:動詞:攻める/せめる;動詞:破る/やぶる"', 'は は は 助詞 9 副助詞 2 * 0 * 0 NIL <文末><表現文末><かな漢字><ひらがな><付属>']
        self.assertEquals(actual, expected)

    def test_remove_negation_from_banning(self):
        token_lines = ['歩く あるく 歩く 動詞 2 * 0 子音動詞カ行 2 基本形 2 "代表表記:歩く/あるく" <代表表記:歩く/あるく><正規化代表表記:歩く/あるく><文頭><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>', 'な な な 助詞 9 終助詞 4 * 0 * 0 NIL <文末><表現文末><かな漢字><ひらがな><付属>']

        actual = replace_lib.remove_negation_from_banning(token_lines)
        expected = ['歩き あるき 歩き 動詞 2 * 0 子音動詞カ行 2 基本連用形 8 "代表表記:歩く/あるく" <代表表記:歩く/あるく><正規化代表表記:歩く/あるく><文頭><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>', 'ましょう ましょう ます 接尾辞 14 動詞性接尾辞 7 動詞性接尾辞ます型 31 意志形 4 "代表表記:ます/ます"']
        self.assertEquals(actual, expected)

    def test_change_katuyou0(self):
        token_line = '歩く あるく 歩く 動詞 2 * 0 子音動詞カ行 2 基本形 2 "代表表記:歩く/あるく" <代表表記:歩く/あるく><正規化代表表記:歩く/あるく><文頭><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>'
        katuyou = '基本連用形'
        actual = replace_lib.change_katuyou(token_line, katuyou)
        expected = '歩き あるき 歩く 動詞 * * * 子音動詞カ行 * 基本連用形 * "代表表記:歩く/あるく" <代表表記:歩く/あるく><正規化代表表記:歩く/あるく><文頭><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>'
        self.assertEquals([actual], [expected])
        # self.assertEquals(actual, expected)




if __name__ == '__main__':
    unittest.main() # シンプルな出力でいい場合

    #詳細
    # unittest.main(verbosity=2, buffer=True)
