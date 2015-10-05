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


def get_changed_sentences(juman_lines):
    ans = [""]
    s_exp = sexp.get_sexp("/Users/sak/local/src/juman-7.01/dic/JUMAN.katuyou")

    antonym_pat1 = re.compile("反義:[^ \"]+[^ \"$]")
    antonym_pat2 = re.compile("[^:;]+:[^/]+/[^ \";]+")
    antonym_pat3 = re.compile("[^:;]+:(?P<lemma>[^/]+)/[^ \";]+")
    antonym_pat4 = re.compile("(?P<pos>[^:;]+)-?[^:]*:[^/]+/[^ \";]+")
    pos_pat = re.compile("(?P<basic_pos>[^-]+)-.*")

    for line in juman_lines:
        match_obj = antonym_pat1.search(line)
        if match_obj:
            matched_list = antonym_pat2.findall(match_obj.group().replace("反義:", ""))
            form = line.split(' ')[9]
            antonym_list = []
            for antonym in matched_list:
                lemma = antonym_pat3.search(antonym).group("lemma")
                pos = antonym_pat4.search(antonym).group("pos")
                basic_pos = "".join(list(itertools.takewhile(lambda ch: ch != '-', pos))) #動くと思うけど、もっといい書き方ありそう

                if line.split(' ')[7] == '*':
                    #活用がない
                    antonym_list.append(lemma)
                elif (basic_pos and basic_pos != line.split(' ')[3]):
                    #同じ品詞でない場合は変換しない(本当だ[形]→ウソ[名])
                    #「ウソだと思わないでください」→「本当だと思ってください」
                    #を変換しないということなので、ぐぬぬ…良くないぞ。
                    #FIXME
                    continue
                else:
                    #活用がある
                    # print line
                    # print pos
                    katuyou_type = get_katuyou_type(lemma, pos)
                    # print katuyou_type
                    kihon = sexp.get_verb_katuyou(s_exp, katuyou_type, "基本形")

                    pat1 = re.compile("%s$" % kihon)
                    gokan = re.sub(pat1, "", lemma) #基本形の部分を取る

                    try:
                        katuyou = sexp.get_verb_katuyou(s_exp, katuyou_type, form)
                        katuyou = "" if katuyou == '*' else katuyou
                        antonym_list.append(gokan+katuyou)
                    except:
                        #antonym_listに何もせずに、次の対義語に進む
                        continue

            if len(antonym_list) == 0:
                #例外が発生して変換できなかった場合は、元の語をそのまま置く
                word = line.split(' ')[0]
                ans = [s + word for s in ans]

            else:
                ans = [s + ant for s in ans for ant in antonym_list]

        else:
            word = line.split(' ')[0]
            ans = [s + word for s in ans]

    return ans

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

def sentence_func(juman_lines):
    orig_str = "".join([line.split(' ')[0] for line in juman_lines if line[0] != '@'])

    #まずは@を解消
    juman_lines_list = disambiguate_juman_line(juman_lines)

    ans = []
    for lst in [get_changed_sentences(d_juman_lines) for d_juman_lines in juman_lines_list]:
        ans.extend(lst)
    ans = list(set(ans)) #重複した文を削除

    for s in ans:
        print s
        # if s != orig_str:
            # print s #出力



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
