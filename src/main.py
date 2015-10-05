#coding:utf-8
import sys
import re
import sexp
import itertools

#見出し語と品詞を引数として、詳細な品詞を返す(例:ナノ形容詞)
#品詞を指定するのは、内容語と接尾辞で辞書ファイルが異なるため
def get_katuyou_type(lemma, pos):
    pat = re.compile("見出し語 [^)]*%s[ )]" % lemma) #%s[ )]としているのは、「来る」に対して「来るべき(きたるべき)」がヒットしないようにするため。
    pat2 = re.compile("\(活用型 (?P<pos>[^\)]+)\)")

    if "接尾辞" in pos:
        for line in open("/Users/sak/local/src/juman-7.01/dic/Suffix.dic").readlines():
                    line = line.rstrip()
                    if pat.search(line):
                        return pat2.search(line).group("pos")
    else:
        for line in open("/Users/sak/local/src/juman-7.01/dic/ContentW.dic").readlines():
            line = line.rstrip()
            if pat.search(line):
                # print lemma
                # print line
                return pat2.search(line).group("pos")

    #例外
    # print lemma
    # print pos
    raise lemma

#Jumanの出力から@を取り除く
#具体的には、あらゆるパターンを列挙
#[[String]]を返す
def disambiguate_juman_line(juman_lines):
    ans = [[""]]
    ambiguous_mrphs = []
    prev_mrph_is_at = False

    #後ろから見る
    for line in juman_lines[::-1]:
        if line[0] == '@':
            ambiguous_mrphs.append(line[2:]) #@の除去
            prev_mrph_is_at = True
        elif prev_mrph_is_at:
            ambiguous_mrphs.append(line)
            ans = [[at_line] + lst for lst in ans for at_line in ambiguous_mrphs]
            ambiguous_mrphs = []
        else:
            ans = [[line] + lst  for lst in ans] #FIXME:リストの和、遅そう

    return ans

#何をしたかったんだ、このメソッド…
#しばらく経っても使わないならば、消しましょう
# def extract_antonym_pairs(enum_antonym_pairs):
#     ans = []


#     # return ans
#     #「広い」の場合
#     return [[(0,"形容詞", "小さい")], (4, "動詞", "攻める")] #FIXME


#「-してはいけません」の直後(にあるはず?)の語を置き換える
#反義語を持つ単語のうち、一番文末に近い語のみ置き換える
#FIXME repalce_one_wordと名前に統一感がない
def extract_last_antonym_pairs(enumerated_antonym_pairs):
    ans = []
    if len(enumerated_antonym_pairs) == 0:
        return []
    else:
        return [[p] for p in enumerated_antonym_pairs[-1]]

#1語だけ置き換える
# [[(0,形容詞, 小さい)], [(3, 動詞, 攻める), (3, 動詞, 破る)]]
# →
# [[(0,形容詞, 小さい)], [(3, 動詞, 攻める)], [(3, 動詞, 破る)]]
#FIXME extract_last_antonym_pairsと名前に統一感がない
def replace_one_word(enumerated_antonym_pairs):
    ans = []
    for antonym_pairs_lst in enumerated_antonym_pairs:
        for pair in antonym_pairs_lst:
            ans.append([pair])

    return ans


#まず反義語を持つものを列挙
#例:「大きい村を守らないでください」
#→[[(0,形容詞, 小さい)], [(3, 動詞, 攻める), (3, 動詞, 破る)]]
def enumerate_antonym_pairs(disambiguated_juman_lines):
    ans = []

    #パターン減らせるかもしれない。
    antonym_pat1 = re.compile("反義:[^ \"]+[^ \"$]")
    antonym_pat2 = re.compile("[^:;]+:[^/]+/[^ \";]+")
    antonym_pat3 = re.compile("[^:;]+:(?P<lemma>[^/]+)/[^ \";]+")
    antonym_pat4 = re.compile("(?P<pos>[^:;]+)-?[^:]*:[^/]+/[^ \";]+")

    for ind, line in enumerate(disambiguated_juman_lines):
        match_obj = antonym_pat1.search(line)

        if match_obj:
            matched_list = antonym_pat2.findall(match_obj.group().replace("反義:", ""))
            antonym_list = []
            for antonym in matched_list:
                lemma = antonym_pat3.search(antonym).group("lemma")
                pos = antonym_pat4.search(antonym).group("pos")
                antonym_list.append((ind, pos, lemma))
            ans.append(antonym_list)
        else:
            pass

    return ans


#antonym_pairsに従って置き換えた後の文字列を返す
#antonym_pairsに従うので、返す型は文字列のリストではない。1つのみ。
def replace_with_antonym_pairs(disambiguated_juman_lines, antonym_pairs):
    ans_lines = [line.split(' ')[0] for line in disambiguated_juman_lines]

    #FIXME
    #antonym_pairsの中に、同じ単語を複数の反義語に置き換えるようなペアが入っていないかどうかチェック
    #例: [守る→破る, 守る→攻める]


    for ind, pos, lemma in antonym_pairs:
        basic_pos = "".join(list(itertools.takewhile(lambda ch: ch != '-', pos))) #動くと思うけど、もっといい書き方ありそう
        line = disambiguated_juman_lines[ind]

        if line.split(' ')[7] == '*':
            #活用がない → 反義語も活用しない
            #というのはウソで、「ウソ(名詞)」→「本当だ(形容詞)」というパターンがある
            #とりあえず、活用のことは考えず、単に置き換える
            #FIXME
            ans_lines[ind] = lemma

        elif basic_pos != line.split(' ')[3]:
            #同じ品詞でない場合は変換しない(本当だ[形]→ウソ[名])
            #「ウソだと思わないでください」→「本当だと思ってください」
            #を変換しないということなので、ぐぬぬ…良くないぞ。
            #FIXME
            continue

        else:
            #活用がある
            s_exp = sexp.get_sexp("/Users/sak/local/src/juman-7.01/dic/JUMAN.katuyou")
            form = line.split(' ')[9]
            katuyou_type = get_katuyou_type(lemma, pos)
            kihon = sexp.get_verb_katuyou(s_exp, katuyou_type, "基本形")

            pat1 = re.compile("%s$" % kihon)
            gokan = re.sub(pat1, "", lemma) #基本形の部分を取る

            try:
                katuyou = sexp.get_verb_katuyou(s_exp, katuyou_type, form)
                katuyou = "" if katuyou == '*' else katuyou
                ans_lines[ind] = gokan + katuyou
            except:
                #何もせずに、次の対義語ペアに進む
                continue

    return "".join(ans_lines)



def sentence_func(juman_lines):
    orig_str = "".join([line.split(' ')[0] for line in juman_lines if line[0] != '@'])

    #まずは@を解消
    juman_lines_list = disambiguate_juman_line(juman_lines)

    #語の置き換え
    ans = []
    for disambiguated_juman_lines in juman_lines_list:
        enumerated_antonym_pairs = enumerate_antonym_pairs(disambiguated_juman_lines)
        # antonym_pairs_lst = extract_last_antonym_pairs(enumerated_antonym_pairs)
        antonym_pairs_lst = replace_one_word(enumerated_antonym_pairs)
        for antonym_pairs in   antonym_pairs_lst:
            s = replace_with_antonym_pairs(disambiguated_juman_lines, antonym_pairs)
            ans.append(s)

    ans = [s for s in ans if s != orig_str] #元の文は除く
    ans = list(set(ans)) #重複した文を削除
    for s in ans:
        print s

def main():
    juman_lines = []

    for line in sys.stdin:
        line = line.rstrip()

        if line == "EOS":
            #"EOS"はjuman_linesに含めない
            sentence_func(juman_lines)
            juman_lines = []
        else:
            juman_lines.append(line)


if __name__ == "__main__":
    main()
