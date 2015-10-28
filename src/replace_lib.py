#coding:utf-8
import re
import sexp
import itertools
import sys
import jctconv


#子音動詞サ行 5 基本連用形 8の(5,8)という情報から、("子音動詞サ行", "基本連用形")を得る
def get_katuyou_str_from_id(katuyou_type_ind, katuyou_form_ind):
    juman_dir = "/Users/sak/local/src/juman-7.01"
    # juman_dir = "/home/lr/tsakaki/local/src/juman-7.0"
    s_exp = sexp.get_sexp(juman_dir + "/dic/JUMAN.katuyou")

    ans = sexp.get_katuyou_str_from_id(s_exp, katuyou_type_ind, katuyou_form_ind)
    return ans

#活用させる
def change_katuyou(token_line, katuyou):
    juman_dir = "/Users/sak/local/src/juman-7.01"
    # juman_dir = "/home/lr/tsakaki/local/src/juman-7.0"

    s_exp = sexp.get_sexp(juman_dir + "/dic/JUMAN.katuyou")
    yomi = token_line.split(' ')[1]
    lemma = token_line.split(' ')[2]
    pos = token_line.split(' ')[3]
    detail_pos = token_line.split(' ')[5]
    orig_katuyou = token_line.split(' ')[9]
    katuyou_type = token_line.split(' ')[7]
    info = " ".join(token_line.split(' ')[11:]) #「"代表表記:歩く/あるく" <代表表記:歩く/あるく><正規化代表表記:歩く/あるく><文頭><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>」のように、スペースで区切られてしまっているのを結合する。

    kihon_katuyou_gobi = sexp.get_verb_katuyou(s_exp, katuyou_type, "基本形")
    kihon_katuyou_gobi = "" if kihon_katuyou_gobi == '*' else kihon_katuyou_gobi

    orig_katuyou_gobi = sexp.get_verb_katuyou(s_exp, katuyou_type, orig_katuyou)
    orig_katuyou_gobi = "" if orig_katuyou_gobi == "*" else orig_katuyou_gobi

    pat1 = re.compile("%s$" % kihon_katuyou_gobi)
    pat2 = re.compile("%s$" % orig_katuyou_gobi)
    gokan = re.sub(pat1, "", lemma) #基本形の部分を取る
    yomi_gokan = re.sub(pat2, "", yomi)

    try:
        katuyou_gobi = sexp.get_verb_katuyou(s_exp, katuyou_type, katuyou)
        katuyou_gobi = "" if katuyou_gobi == '*' else katuyou_gobi
        surf = gokan + katuyou_gobi
        new_yomi = yomi_gokan + katuyou_gobi
        return juman_like_str(surf, new_yomi, lemma, pos, info, katuyou, katuyou_type, detail_pos)

    except:
        #変換しない
        return token_line

#例: 「走るな」→「走りましょう」
def remove_negation_from_suruna(token_lines):
    ans_lines = [s for s in token_lines]

    #文末から見る
    lst = [tmp for tmp in enumerate(token_lines)]
    for ind, line in lst[::-1]:
        if ind > 0 and line == 'な な な 助詞 9 終助詞 4 * 0 * 0 NIL <文末><表現文末><かな漢字><ひらがな><付属>' and (ans_lines[ind-1].split(' ')[3] == '動詞' or ans_lines[ind-1].split(' ')[5] == '動詞性接尾辞') and ans_lines[ind-1].split(' ')[9] == "基本形":
            ans_lines[ind-1] = change_katuyou(ans_lines[ind-1], "基本連用形")
            ans_lines[ind] = 'ましょう ましょう ます 接尾辞 14 動詞性接尾辞 7 動詞性接尾辞ます型 31 意志形 4 "代表表記:ます/ます"'
            break
    return ans_lines

#例:「走ってはいけません」→「走らなければいけません」
#「なければ」という否定は入っているが、禁止ではない。
def remove_negation_from_ikemasen(token_lines):
    ans_lines = [s for s in token_lines]

    #文末から見る
    lst = [tmp for tmp in enumerate(token_lines)]
    for ind, line in lst[::-1]:
        cond_ikemasen = (ind-4 >= 0 and (ans_lines[ind-4].split(' ')[3] == '動詞' or ans_lines[ind-4].split(' ')[5] == '動詞性接尾辞') and ans_lines[ind-4].split(' ')[9] == 'タ系連用テ形' and ans_lines[ind-3].split(' ')[0] == 'は' and (ans_lines[ind-2].split(' ')[0] == 'いけ' or ans_lines[ind-2].split(' ')[0] == 'なり') and ans_lines[ind-1].split(' ')[0] == 'ませ' and ans_lines[ind].split(' ')[0] == 'ん')
        cond_naranai = ind-3 >= 0 and (ans_lines[ind-3].split(' ')[3] == '動詞' or ans_lines[ind-3].split(' ')[5] == '動詞性接尾辞') and ans_lines[ind-3].split(' ')[9] == 'タ系連用テ形' and ans_lines[ind-2].split(' ')[0] == 'は' and ans_lines[ind-1].split(' ')[0] == 'なら' and ans_lines[ind].split(' ')[0] == 'ない'
        cond_ikenai = ind-2 >= 0 and (ans_lines[ind-2].split(' ')[3] == '動詞' or ans_lines[ind-2].split(' ')[5] == '動詞性接尾辞') and ans_lines[ind-2].split(' ')[9] == 'タ系連用テ形' and ans_lines[ind-1].split(' ')[0] == 'は' and ans_lines[ind].split(' ')[0] == 'いけない'
        if cond_ikemasen:
            new_ind = ind - 4
            ans_lines_before= [] if new_ind == 0 else ans_lines[0:new_ind]
            ans_lines_after =  ans_lines[ind-2:]
            verb = change_katuyou(ans_lines[new_ind], "未然形")
            ans = ans_lines_before
            ans.append(verb)
            ans.append('なければ なければ ない 接尾辞 14 形容詞性述語接尾辞 5 イ形容詞アウオ段 18 基本条件形 6 "代表表記:ない/ない"')
            ans.extend(ans_lines_after)
            return ans

        elif cond_naranai:
            new_ind = ind - 3
            ans_lines_before= [] if new_ind == 0 else ans_lines[0:new_ind]
            ans_lines_after =  ans_lines[ind-1:]
            verb = change_katuyou(ans_lines[new_ind], "未然形")
            ans = ans_lines_before
            ans.append(verb)
            ans.append('なければ なければ ない 接尾辞 14 形容詞性述語接尾辞 5 イ形容詞アウオ段 18 基本条件形 6 "代表表記:ない/ない"')
            ans.extend(ans_lines_after)
            return ans

        elif cond_ikenai:
            new_ind = ind - 2
            ans_lines_before= [] if new_ind == 0 else ans_lines[0:new_ind]
            ans_lines_after =  ans_lines[ind:]
            verb = change_katuyou(ans_lines[new_ind], "未然形")
            ans = ans_lines_before
            ans.append(verb)
            ans.append('なければ なければ ない 接尾辞 14 形容詞性述語接尾辞 5 イ形容詞アウオ段 18 基本条件形 6 "代表表記:ない/ない"')
            ans.extend(ans_lines_after)
            return ans




    return ans_lines


def remove_negation_from_naide_kudasai(token_lines):
    ans_lines = [s for s in token_lines]



    #文末から見る
    lst = [tmp for tmp in enumerate(token_lines)]
    for ind, line in lst[::-1]:
        cond = ind-2 >= 0 and (ans_lines[ind-2].split(' ')[3] == '動詞' or ans_lines[ind-2].split(' ')[5] == '動詞性接尾辞') and ans_lines[ind-2].split(' ')[9] == '未然形' and ans_lines[ind-1].split(' ')[0] == 'ないで' and (ans_lines[ind].split(' ')[1] == 'ください' or ans_lines[ind].split(' ')[0] == 'ね' or ans_lines[ind].split(' ')[0] == 'よ' or ans_lines[ind].split(' ')[0] == 'くれ')
        if cond:
            ans_lines_before= [] if ind-2 == 0 else ans_lines[0:ind-2]
            ans_lines_after =  ans_lines[ind:]
            verb = change_katuyou(ans_lines[ind-2], "タ系連用テ形")
            ans = ans_lines_before
            ans.append(verb)
            ans.extend(ans_lines_after)
            return ans

    return ans_lines

def remove_negation_from_go_naranaide(token_lines):
    ans_lines = [s for s in token_lines]

    #文末から見る
    lst = [tmp for tmp in enumerate(token_lines)]
    for ind, line in lst[::-1]:
        cond_ni = ind-4 >= 0 and (ans_lines[ind-4].split(' ')[0] == 'お' or ans_lines[ind-4].split(' ')[0] == 'ご') and (ans_lines[ind-3].split(' ')[3] == '動詞' or ans_lines[ind-3].split(' ')[5] == '動詞性接尾辞') and ans_lines[ind-3].split(' ')[9] == '基本連用形' and ans_lines[ind-2].split(' ')[0] == 'に' and ans_lines[ind-1].split(' ')[0] == 'なら' and ans_lines[ind].split(' ')[0] == 'ないで'

        cond_niha = ind-5 >= 0 and (ans_lines[ind-5].split(' ')[0] == 'お' or ans_lines[ind-5].split(' ')[0] == 'ご') and (((ans_lines[ind-4].split(' ')[3] == '動詞' or ans_lines[ind-4].split(' ')[5] == '動詞性接尾辞') and ans_lines[ind-4].split(' ')[9] == '基本連用形') or (ans_lines[ind-4].split(' ')[3] == '名詞')) and ans_lines[ind-3].split(' ')[0] == 'に' and ans_lines[ind-2].split(' ')[0] == 'は' and ans_lines[ind-1].split(' ')[0] == 'なら' and ans_lines[ind].split(' ')[0] == 'ないで'

        if cond_ni:
            ans_lines_before= ans_lines[0:ind-1]
            ans_lines_after = ans_lines[ind+1:]
            verb = change_katuyou(ans_lines[ind-1], "タ系連用テ形")
            ans = ans_lines_before
            ans.append(verb)
            ans.extend(ans_lines_after)
            return ans

        elif cond_niha:
            ans_lines_before= ans_lines[0:ind-2]
            ans_lines_after = ans_lines[ind+1:]
            verb = change_katuyou(ans_lines[ind-1], "タ系連用テ形")
            ans = ans_lines_before
            ans.append(verb)
            ans.extend(ans_lines_after)
            return ans

    return ans_lines

def remove_negation_from_naiyouni(token_lines):
    ans_lines = [s for s in token_lines]

    #文末から見る
    lst = [tmp for tmp in enumerate(token_lines)]
    for ind, line in lst[::-1]:
        cond = ind-4 >= 0 and (ans_lines[ind-4].split(' ')[3] == '動詞' or ans_lines[ind-4].split(' ')[5] == '動詞性接尾辞') and ans_lines[ind-3].split(' ')[0] == 'ない' and ans_lines[ind-2].split(' ')[0] == 'ように' and ans_lines[ind-1].split(' ')[0] == 'して' and ans_lines[ind].split(' ')[1] == 'ください'

        if cond:
            ans_lines_before= [] if ind-4 == 0 else ans_lines[0:ind-4]
            ans_lines_after =  ans_lines[ind-2:]
            verb = change_katuyou(ans_lines[ind-4], "基本形")
            ans = ans_lines_before
            ans.append(verb)
            ans.extend(ans_lines_after)
            return ans

    return ans_lines

    return ["hage"]

def remove_negation_from_banning(token_lines):
    orig_str = "".join(line.split(' ')[0] for line in token_lines)

    if ("はいけません" in orig_str) or ("はなりません" in orig_str) or ("てはならな" in orig_str) or ("てはいけな" in orig_str):
        return remove_negation_from_ikemasen(token_lines)
    elif ("ないようにしてください" in orig_str):
        return remove_negation_from_naiyouni(token_lines)
    elif (("にならな" in orig_str) or ("にはならな" in orig_str)) and (("お" in orig_str) or "ご" in orig_str):
        return remove_negation_from_go_naranaide(token_lines)
    elif ("ないでよ" in orig_str) or ("ないでく" in orig_str) or ("ないで下" in orig_str) or ("ないでね" in orig_str) or ("ないでよ" in orig_str):
        return remove_negation_from_naide_kudasai(token_lines)
    elif ("な" in orig_str):
        return remove_negation_from_suruna(token_lines)
    else:
        return token_lines

#jumanの辞書をサーチして、ヒットした行を返す
#品詞を指定するのは、内容語と接尾辞で辞書ファイルが異なるため
def search_lemma(pos, lemma, yomi):
    #「来る」だけはContentW.dicで例外的に読みに漢字が含まれているため、別に扱う必要がある。
    if pos == "動詞" and lemma == "来る" and yomi == "くる":
        return '(動詞 ((読み 来る)(見出し語 (来る 0.8))(活用型 カ変動詞来)(意味情報 "代表表記:来る/くる 反義:動詞:帰る/かえる")))'

    juman_dir = "/Users/sak/local/src/juman-7.01"
    # juman_dir = "/home/lr/tsakaki/local/src/juman-7.0"

    pat1 = re.compile("見出し語[^\)]* %s[ \)]" % lemma)

    #(動詞 ((読み 来る)(見出し語 (来る 0.8))(活用型 カ変動詞来)(意味情報 "代表表記:来る/くる 反義:動詞:帰る/かえる")))
    #のように、見出し語に重みが付いている場合
    pat2 = re.compile("見出し語[^\)]* \(%s [0-9\.]+\)" % lemma)
    pat3 = re.compile("\(読み %s\)" % yomi)


    if "接尾辞" in pos:
        for line in open(juman_dir + "/dic/Suffix.dic"): # .readlines(): readlines()を使うと一気に読み込まれて負荷がかかる。どうせ1行ずつforで読み込んでいるので、readlinesがなくても変わらない。
            line = line.rstrip()

            if (pat1.search(line) or pat2.search(line)) and pat3.search(line):
                return line

    else:
        for line in open(juman_dir + "/dic/ContentW.dic"):
            line = line.rstrip()

            if (pat1.search(line) or pat2.search(line)) and pat3.search(line):
                return line

    raise Exception("No Hit (%s, %s, %s)" % (pos, lemma, yomi))



#元々は、get_katuyou_type
#見出し語と品詞を引数として、詳細な品詞を返す(例:ナノ形容詞)
#品詞を指定するのは、内容語と接尾辞で辞書ファイルが異なるため
#Jumanに付属する辞書で単語を検索し、活用型と意味情報を要素とするタプルを返す
def get_katuyou_type_and_info_from_juman_dic(pos, lemma, yomi):

    regex_of_katuyou_type = re.compile("\(活用型 (?P<katuyou_type>[^\)]+)\)")
    regex_of_meaning_info = re.compile("\(意味情報 (?P<info>\"[^\)]+\")\)")

    line = search_lemma(pos, lemma, yomi)
    m1 = regex_of_katuyou_type.search(line)
    m2 = regex_of_meaning_info.search(line)
    katuyou_type = m1.group("katuyou_type") if m1 else ""
    meaning_info = m2.group("info") if m2 else ""

    return (katuyou_type, meaning_info)

#表層の文字だけしか取っていなかったので、読みも取ってくるように変更
def extract_antonyms_from_token_line(ind, token_line):
    regex = re.compile('[ \"]反義:([^:]+:[^/]+/[^;\" >]+;?)+?[\" ]') #KNPによって付加された<反義:動詞:守る/まもる;動詞:防ぐ/ふせぐ>のような部分ではなく、Jumanの出力の段階で付与された意味情報を見るようにする (欲張らないマッチ)
    match_obj = regex.search(token_line)

    if match_obj:
        #例: "反義:動詞:攻める/せめる;動詞:破る/やぶる"
        #→  "動詞:攻める/せめる;動詞:破る/やぶる"
        #→  ["動詞:攻める/せめる", "動詞:破る/やぶる"]

        tmp_antonyms = re.sub("^.+反義:", "", match_obj.group(0))
        antonyms = re.sub("[\" ]$" ,"", tmp_antonyms).split(';')
        ans = [(ind, antonym.split(':')[0], antonym.split(':')[1].split('/')[0], antonym.split(':')[1].split('/')[1]) for antonym in antonyms]

        return ans
    else:
        return []

#まず反義語を持つものを列挙
#例:「大きい村を守らないでください」
#→[[(0,形容詞, 小さい)], [(3, 動詞, 攻める), (3, 動詞, 破る)]]
#replace_with_juman.pyでしか使っていなかったので、カット。
#今後はreplace_with_knp.pyのみを使いましょう。
# def enumerate_antonym_pairs(disambiguated_juman_lines):
#     ans = []

#     for ind, line in enumerate(disambiguated_juman_lines):
#         #FIXME antonym
#         antonym_list = extract_antonyms_from_token_line(ind, line)
#         if len(antonym_list) != 0:
#             ans.append(antonym_list)

#     return ans


#にくい にくい にくい 接尾辞 14 形容詞性述語接尾辞 5 イ形容詞アウオ段 18 基本形 2 "代表表記:にくい/にくい 反義:接尾辞-形容詞性述語接尾辞:やすい/やすい"
#引数の順番注意! infoは途中にある
def juman_like_str(surf, yomi, lemma, pos, info="NIL", katuyou="*", katuyou_type="*", detail_pos="*"):
    return "%s %s %s %s * %s * %s * %s * %s" % (surf, yomi, lemma, pos, detail_pos, katuyou_type, katuyou, info)

def replace_juman_line_with_antonym(orig_line, pos, lemma, yomi):
    basic_pos = "".join(list(itertools.takewhile(lambda ch: ch != '-', pos))) #動くと思うけど、もっといい書き方ありそう
    detail_pos = "".join(list(itertools.dropwhile(lambda ch: ch != '-', pos))[1:])

    #「ウソ(名詞)」→「本当だ(形容詞)」など
    #語幹に置き換える
    if orig_line.split(' ')[3] == '名詞' and basic_pos == '形容詞':
        # katuyou = orig_line.split(' ')[9]
        katuyou_type_of_ant, info_of_ant = get_katuyou_type_and_info_from_juman_dic(basic_pos, lemma, yomi)
        if katuyou_type_of_ant == 'ナノ形容詞' or katuyou_type_of_ant == 'ナ形容詞':
            antonym_juman_like_str = juman_like_str(lemma, yomi, lemma, basic_pos, info_of_ant, '基本形', katuyou_type_of_ant)
            return change_katuyou(antonym_juman_like_str, '語幹')
        else:
            return orig_line

    #「本当だ(形容詞)」→「嘘(名詞)だ」
    #基本形の場合からの変換のみを扱う
    elif orig_line.split(' ')[3] == '形容詞' and orig_line.split(' ')[9] == '基本形' and basic_pos == '名詞':
        # katuyou = orig_line.split(' ')[9]
        katuyou_type_of_ant, info_of_ant = get_katuyou_type_and_info_from_juman_dic(basic_pos, lemma, yomi)
        return juman_like_str(lemma, yomi, lemma, basic_pos, info_of_ant, '*', '*', detail_pos)

    #KNPによって品詞変更がされている場合: 元の語の情報を利用する
    elif "<品詞変更:" in orig_line:
        #'<品詞変更:伸ばし-のばし-伸ばす-2-0-5-8-"代表表記:伸ばす/のばす 自他動詞:自:伸びる/のびる 反義:動詞:曲げる/まげる;動詞:縮める/ちぢめる">' のような部分
        pat = re.compile("<品詞変更:([^>]+)>")
        pos_change_info = pat.search(orig_line).group(1)

        #FIXME ここ、10行くらい後と同じコードになっているので後でリファクタリング。関数でくくりましょう。
        katuyou_type_of_ant, info_of_ant = get_katuyou_type_and_info_from_juman_dic(basic_pos, lemma, yomi)
        antonym_juman_like_str = juman_like_str(lemma, yomi, lemma, basic_pos, info_of_ant, '基本形', katuyou_type_of_ant)

        _, katuyou = get_katuyou_str_from_id(int(pos_change_info.split('-')[5]), int(pos_change_info.split('-')[6]))
        return change_katuyou(antonym_juman_like_str, katuyou)

    elif basic_pos == orig_line.split(' ')[3] and orig_line.split(' ')[7] == '*':
        #それ以外の、活用がない場合
        #活用がない → 反義語も活用しない
        #とりあえず、活用のことは考えず、単に置き換える

        #腕は伸ばし(名詞)→腕は縮める(原形)となってしまう…
        #「腕は伸ばし手を広げないようにしてください。」
        #FIXME
        katuyou_type_of_ant, info_of_ant = get_katuyou_type_and_info_from_juman_dic(basic_pos, lemma, yomi)
        return juman_like_str(lemma, yomi, lemma, basic_pos, info_of_ant, '*', '*', detail_pos)

    elif basic_pos != orig_line.split(' ')[3]:
        #上記以外の場合で、
        #同じ品詞でない場合は変換しない
        #FIXME
        return orig_line

    else:
        #活用がある
        katuyou = orig_line.split(' ')[9]
        katuyou_type_of_ant, info_of_ant = get_katuyou_type_and_info_from_juman_dic(basic_pos, lemma, yomi)
        antonym_juman_like_str = juman_like_str(lemma, yomi, lemma, basic_pos, info_of_ant, '基本形', katuyou_type_of_ant)
        return change_katuyou(antonym_juman_like_str, katuyou)


#antonym_pairsとは: 例 [(0, 動詞, 攻める, せめる), (1, 形容詞, 大きい, おおきい), (3, 接尾辞-形容詞性述語接尾辞, やすい, やすい)]
#antonym_pairsに従って置き換えた後の文字列に対応する、jumanの行っぽいものを返す。
def replace_with_antonym_pairs(token_lines, antonym_pairs):
    ans_lines = [line for line in token_lines]

    #antonym_pairsの中に、同じ単語を複数の反義語に置き換えるようなペアが入っていないかどうかチェック
    #例: [守る→破る, 守る→攻める]
    ind_lst = [ind for ind, pos, lemma, yomi in antonym_pairs]
    if len(ind_lst) != len(set(ind_lst)):
        raise Exception("Replace to more than two words")

    if len(antonym_pairs) == 0:
        return token_lines
    else:
        for ind, pos, lemma, yomi in antonym_pairs:
            ans_lines[ind] = replace_juman_line_with_antonym(token_lines[ind], pos, lemma, yomi)

        return ans_lines

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

def is_chunk(knp_line):
    return knp_line[0] == '*'

def is_basic_phrase(knp_line):
    return knp_line[0] == '+'

def is_doc_info(knp_line):
    return knp_line[0] == '#'

def is_EOS(knp_line):
    return knp_line == "EOS"

def is_token(knp_line):
    return (not is_chunk(knp_line)) and (not is_basic_phrase(knp_line)) and (not is_doc_info(knp_line)) and (not is_EOS(knp_line))


def get_mod_chunk_and_mod_chunk_ind_lst(knp_lines, chunk_num):
    return [(ind, line) for ind, line in enumerate(knp_lines) if is_chunk(line) and line.split(' ')[2] == (str(chunk_num) + "D")]


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

#チャンクの通し番号(0から始まる)を返す。
#KNPのprint-numオプションで表示される情報
def get_chunk_num(chunk_line):
    if (not is_chunk(chunk_line)):
        raise Exception('arugment error')

    ans = 0
    try:
        ans = int(chunk_line.split(' ')[1])
    except:
        raise Exception('Use -print-num option when running KNP')

    return ans

#あるチャンク(動詞を含む)の項の格を変える
#変換後の「トークン列」を返す
#これは、チャンク情報などと矛盾させないようにするため。
#扱いに注意!
#格は「カタカナ」で与える。
def change_case(knp_lines, prev_case_katakana, new_case_katakana, verb_chunk_ind):
    chunk_line = knp_lines[verb_chunk_ind]
    chunk_num = get_chunk_num(chunk_line)

    #もし同じ項が2つあったときには、後ろ側(より述語に近い方)を取る (ないと思うけど…)
    #例: (変な文) 山を海を愛す → 「海を」
    prev_case_chunks = [(mod_chunk_ind, mod_chunk_line) for (mod_chunk_ind, mod_chunk_line) in get_mod_chunk_and_mod_chunk_ind_lst(knp_lines, chunk_num) if (("<係:%s格>" % prev_case_katakana) in mod_chunk_line)]

    #なかったら、空リストを返す
    if len(prev_case_chunks) == 0:
        return []

    prev_case_chunk_ind, prev_case_chunk_line = prev_case_chunks[-1]

    #条件に一致する行(格助詞のトークン行)を変換する。
    #トークン行で、prev_case_chunk_indより後ろで、verb_chunk_indより前のもので、「prev_case」に一致する行をnew_caseに直す?
    #他の行はそのまま返す
    def loc_map_func(ind, line, prev_case_chunk_ind, verb_chunk_ind, prev_case_hiragana, new_case_hiragana):
        if prev_case_chunk_ind < ind < verb_chunk_ind:
            if is_token(line) and line.startswith('%s %s %s 助詞 9 格助詞' % (prev_case_hiragana, prev_case_hiragana, prev_case_hiragana)):
                return "%s %s %s 助詞 9 格助詞 1 * 0 * 0 NIL" % (new_case_hiragana, new_case_hiragana, new_case_hiragana)
            else:
                return line
        else:
            return line


    prev_case_hiragana =  jctconv.kata2hira(prev_case_katakana.decode('utf-8')).encode('utf-8')
    new_case_hiragana =  jctconv.kata2hira(new_case_katakana.decode('utf-8')).encode('utf-8')

    tmp_knp_lines = map(lambda (ind, line): loc_map_func(ind, line, prev_case_chunk_ind, verb_chunk_ind, prev_case_hiragana, new_case_hiragana), enumerate(knp_lines))

    return [line for line in tmp_knp_lines if is_token(line)]


#indとhead_token_lineで指定したトークンに反義語が存在した場合、反義語を置き換えてリストにして返す
#FIXME どう考えても、token_lines[ind] == head_token_lineの関係があるから、重複しているのでは…
def replace_token_with_antonym(token_lines, ind, head_token_line):
    if any([(not is_token(line)) for line in token_lines]):
        raise Exception('argument error')

    antonym_lst = extract_antonyms_from_token_line(ind, head_token_line)
    # print "B--antonym_lst--"
    # for antonym_tpl in antonym_lst:
    #     for a in antonym_tpl:
    #         print a
    # print "E--antonym_lst--"

    return [replace_with_antonym_pairs(token_lines, [antonym_pair]) for antonym_pair in antonym_lst]



#「反義語で置き換えたトークンのリスト」のリストを得る
def get_tokens_lst_replaced_with_antonym(tokens, ind, head_token_line):
    tokens_lst = replace_token_with_antonym(tokens, ind, head_token_line)
    ans = []
    ans.extend(tokens_lst)

    for tokens in tokens_lst:
        verb_lst = [(ind, token_line) for ind, token_line in enumerate(tokens) if token_line.split(' ')[3] == '動詞']

        #動詞が文中に存在した場合、末尾の動詞を「タ系連用テ形」に変え、動詞性接尾辞「ミル」「オク」「イル」「シマウ」を末尾の動詞の活用形にして結合する。
        if len(verb_lst) != 0:
            last_verb_ind, last_verb_token = verb_lst[-1]
            last_verb_katuyou_form = last_verb_token.split(' ')[9]
            last_verb_te_renyou = change_katuyou(last_verb_token, "タ系連用テ形")

            verb_like_suffix_words = """
いる いる いる 接尾辞 14 動詞性接尾辞 7 母音動詞 1 基本形 2 "代表表記:いる/いる"
みる みる みる 接尾辞 14 動詞性接尾辞 7 母音動詞 1 基本形 2 "代表表記:みる/みる"
おく おく おく 接尾辞 14 動詞性接尾辞 7 子音動詞カ行 2 基本形 2 "代表表記:おく/おく"
しまう しまう しまう 接尾辞 14 動詞性接尾辞 7 子音動詞ワ行 12 基本形 2 "代表表記:しまう/しまう"
""".split('\n')[1:-1]

            for verb_like_suffix_token_line in verb_like_suffix_words:
                verb_like_token = change_katuyou(verb_like_suffix_token_line, last_verb_katuyou_form)

                local_ans = []
                local_ans.extend(tokens[0:last_verb_ind])
                local_ans.append(last_verb_te_renyou)
                local_ans.append(verb_like_token)
                local_ans.extend(tokens[last_verb_ind+1:])
                ans.append(local_ans)

    return ans
