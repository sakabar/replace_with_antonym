#coding:utf-8
import sys
import re
import replace_lib

#KNPの出力(print-num付き)を標準入力から読み込んで、
#1. headの動詞
#2. headの動詞の項の名詞
#3. headの動詞の項にかかっている動詞・形容詞など
#の3種類を反義語に置き換える

#チャンクなどの行から、正規化代表表記の部分を正規表現でとってくる。
#チャンクに正規化代表表記がなかったら、エラーを返す。うまくキャッチしてね?
def get_normalized_cand_form(knp_line):
    pattern = re.compile("<正規化代表表記:([^>]*)>")
    ans = pattern.search(knp_line)
    if ans:
        return ans.group(1)
    else:
        raise Exception('Error:' + knp_line)


#indとhead_token_lineで指定したトークンに反義語が存在した場合、反義語を置き換えてリストにして返す
#FIXME どう考えても、token_lines[ind] == head_token_lineの関係があるから、重複しているのでは…
def replace_token_with_antonym(token_lines, ind, head_token_line):
    if any([(not replace_lib.is_token(line)) for line in token_lines]):
        raise Exception('argument error')

    antonym_lst = replace_lib.extract_antonyms_from_token_line(ind, head_token_line)
    # print "B--antonym_lst--"
    # for antonym_tpl in antonym_lst:
    #     for a in antonym_tpl:
    #         print a
    # print "E--antonym_lst--"

    return [replace_lib.replace_with_antonym_pairs(token_lines, [antonym_pair]) for antonym_pair in antonym_lst]


#あるチャンクの主辞のトークンを返す
#なかったら空文字列を返す
def get_head_token_of_chunk(knp_lines, chunk_ind):
    chunk_line = knp_lines[chunk_ind]

    if (not replace_lib.is_chunk(chunk_line)):
        raise Exception('arg is not chunk')

    chunk_line = knp_lines[chunk_ind]

    normalized_cand_form = ""
    try:
        normalized_cand_form = get_normalized_cand_form(chunk_line)
        #「間接/かんせつ+的だ/てきだ」のような複合語は、最初のものをとってくる
        #FIXME よくない場合がありそう。
        #あと、?でつながっている場合は?
    except:
        return ""

    if ("+" in normalized_cand_form):
        normalized_cand_form = normalized_cand_form.split('+')[0]

    ans = [knp_lines[i] for i in xrange(chunk_ind, len(knp_lines)) if replace_lib.is_token(knp_lines[i]) and normalized_cand_form in knp_lines[i]]
    return "" if len(ans) == 0 else ans[0]



def get_pos_of_token(knp_line):
    if (not replace_lib.is_token(knp_line)):
        raise Exception('arg is not token')

    return knp_line.split(' ')[3]


def remove_unchanged_str(orig_str, token_lines_lst):
    ans = []
    for tokens in token_lines_lst:
        s = "".join([token.split(' ')[0] for token in tokens])
        if s != orig_str:
            ans.append(tokens)

    return ans
    # return [tokens for tokens in token_lines_lst if "".join([token.split(' ')[0] for token in tokens]) != orig_str]


def sentence_func(knp_lines):
    tokens = [line for line in knp_lines if replace_lib.is_token(line)]
    orig_str = "".join([line.split(' ')[0] for line in tokens])

    #最後の文節のインデックス, その正規化代表表記
    last_chunk_ind, last_chunk_line = [(ind, line) for ind, line in enumerate(knp_lines) if replace_lib.is_chunk(line) and ("-1D" in line)][0]
    last_chunk_num = replace_lib.get_chunk_num(last_chunk_line)

    #最後の文節内のheadのトークン
    head_token_line = ""
    try:
        head_token_line = get_head_token_of_chunk(knp_lines, last_chunk_ind)
    except:
        Exception('No head token')
        # print orig_str + '\t' + 'ERROR'
        return #FIXME 本当はこうしたくないけど、仕方ない。


    ans = []

    #否定されている動詞は反義語を持つか?
    if "反義" in head_token_line:
        #最後の文節内のトークンを取るので、もし同一のトークンが複数あった場合は最後のものを取る
        head_token_ind = [ind for ind, line in enumerate(tokens) if line == head_token_line][-1]

        #ヲ格をニ格に変換した文を生成し、反義語を置き換える
        #「席を立たないでください」→「席に座ってください」
        wo_to_ni_case_tokens = [line for line in replace_lib.change_case(knp_lines, 'ヲ', 'ニ', last_chunk_ind) if replace_lib.is_token(line)]
        if len(wo_to_ni_case_tokens) != 0:
            ans.extend(replace_token_with_antonym(wo_to_ni_case_tokens, head_token_ind, head_token_line))

        #ニ格をカラ格に変換した文を生成し、反義語を置き換える
        #「波打ち際に近づかないでください」→「波打ち際から遠ざかってください」
        ni_to_kara_case_tokens = [line for line in replace_lib.change_case(knp_lines, 'ニ', 'カラ', last_chunk_ind) if replace_lib.is_token(line)]
        if len(ni_to_kara_case_tokens) != 0:
            ans.extend(replace_token_with_antonym(ni_to_kara_case_tokens, head_token_ind, head_token_line))

        ans.extend(replace_token_with_antonym(tokens, head_token_ind, head_token_line))


    arg_chunks = [(ind, line) for ind, line in enumerate(knp_lines) if replace_lib.is_chunk(line) and line.split(' ')[2] == (str(last_chunk_num) + "D") and re.search("<係:[^>]+>", line)]
    for arg_chunk_ind, arg_chunk in arg_chunks:
        head_token_of_arg = get_head_token_of_chunk(knp_lines, arg_chunk_ind)
        if head_token_of_arg == "":
            pass
        else:

            # pat_case = re.compile("<係:[^>]+格>")
            # if ("<修飾>" in arg_chunk) or pat_case.search(arg_chunk):
            #まず、argの主辞に反義語が存在するかどうか?
            if ("反義" in head_token_of_arg):
                token_ind = get_token_ind(knp_lines, arg_chunk_ind, head_token_of_arg)
                ans.extend(replace_token_with_antonym(tokens, token_ind, head_token_of_arg))

        #次に、そのチャンクにかかっている動詞or名詞or形容詞に反義語が存在するか?
        #FIXME これだと、「分かりにくい表現を使わないでください」が変換できない
        chunk_num = replace_lib.get_chunk_num(arg_chunk)
        for mod_chunk_ind, mod_chunk in replace_lib.get_mod_chunk_and_mod_chunk_ind_lst(knp_lines, chunk_num):
            mod_chunk_token = get_head_token_of_chunk(knp_lines, mod_chunk_ind)
            if mod_chunk_token == "":
                pass
            else:
                if (get_pos_of_token(mod_chunk_token) == "名詞" or get_pos_of_token(mod_chunk_token) == "形容詞") and ("<係:連格>" in mod_chunk_token):
                    # print "DEBUG:hit"
                    if "反義" in mod_chunk_token:
                        tok_ind = get_token_ind(knp_lines, mod_chunk_ind, mod_chunk_token)
                        # print "DEBUG: hit"
                        ans.extend(replace_token_with_antonym(tokens, tok_ind, mod_chunk_token))


    #この段階で、変換が起こらなかった文を排除する
    ans = remove_unchanged_str(orig_str, ans)
    ans = ["".join([token_line.split(' ')[0] for token_line in replace_lib.remove_negation_from_banning(token_lines)]) for token_lines in ans]
    ans = [s for s in ans if s != orig_str] #元の文は除く
    ans = list(set(ans)) #重複した文を削除
    for s in ans:
        print (orig_str + '\t' + s)

#トークンだけで数えた時のインデックスを返す
def get_token_ind(knp_lines, chunk_ind, token_line):
    return [tok_ind for (tok_ind, (ind, line)) in enumerate([(i,knp_line) for i, knp_line in enumerate(knp_lines) if replace_lib.is_token(knp_line)]) if ind > chunk_ind and line == token_line][0]

def main():
    knp_lines = []

    for line in sys.stdin:
        line = line.rstrip()

        if line == "EOS":
            sentence_func(knp_lines)
            knp_lines = []
        else:
            knp_lines.append(line)


if __name__ == "__main__":
    main()
