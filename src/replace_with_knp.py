#coding:utf-8
import sys
import re
import replace_lib

#KNPの出力(print-num付き)を標準入力から読み込んで、
#1. headの動詞
#2. headの動詞の項の名詞
#3. headの動詞の項にかかっている動詞・形容詞など
#の3種類を反義語に置き換える

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


#チャンクなどの行から、正規化代表表記の部分を正規表現でとってくる。
#チャンクに正規化代表表記がなかったら、エラーを返す。うまくキャッチしてね?
def get_normalized_cand_form(knp_line):
    pattern = re.compile("<正規化代表表記:([^>]*)>")
    ans = pattern.search(knp_line)
    if ans:
        return ans.group(1)
    else:
        raise Exception('Error:' + knp_line)

#文末の文節に反義語があった場合、反義語を置き換えてリストにして返す
def replace_token_with_antonym(token_lines, ind, head_token_line):
    if any([(not is_token(line)) for line in token_lines]):
        raise Exception('argument error')

    ind = [ind for ind, token_line in enumerate(token_lines) if token_line == head_token_line][0]
    antonym_lst = replace_lib.extract_antonym_from_token_line(ind, head_token_line)

    return [replace_lib.replace_with_antonym_pairs(token_lines, [antonym_pair]) for antonym_pair in antonym_lst]


def get_head_token_of_chunk(knp_lines, chunk_ind):
    chunk_line = knp_lines[chunk_ind]

    if (not is_chunk(chunk_line)):
        raise Exception('arg is not chunk')

    chunk_line = knp_lines[chunk_ind]

    normalized_cand_form = ""
    try:
        normalized_cand_form = get_normalized_cand_form(chunk_line)
        #「間接/かんせつ+的だ/てきだ」のような複合語は、最初のものをとってくる
        #FIXME よくない場合がありそう。
        #あと、?でつながっている場合は?
    except:
        raise Exception('in get_normalized_cand_form()')

    if ("+" in normalized_cand_form):
        normalized_cand_form = normalized_cand_form.split('+')[0]

    return [knp_lines[i] for i in xrange(chunk_ind, len(knp_lines)) if is_token(knp_lines[i]) and normalized_cand_form in knp_lines[i]][0]



def get_pos_of_token(knp_line):
    if (not is_token(knp_line)):
        raise Exception('arg is not token')

    return knp_line.split(' ')[3]


def sentence_func(knp_lines):
    tokens = [line for line in knp_lines if is_token(line)]
    orig_str = "".join([line.split(' ')[0] for line in tokens])

    #最後の文節のインデックス, その正規化代表表記
    last_chunk_ind, last_chunk_line = [(ind, line) for ind, line in enumerate(knp_lines) if is_chunk(line) and ("-1D" in line)][0]
    last_chunk_num = get_chunk_num(last_chunk_line)

    #最後の文節内のheadのトークン
    head_token_line = ""
    try:
        head_token_line = get_head_token_of_chunk(knp_lines, last_chunk_ind)
    except:
        # print orig_str + '\t' + 'ERROR'
        return #FIXME 本当はこうしたくないけど、仕方ない。


    ans = []

    if "反義" in head_token_line:
        #最後の文節内のトークンを取るので、もし同一のトークンが複数あった場合は最後のものを取る
        head_token_ind = [ind for ind, line in enumerate(tokens) if line == head_token_line][-1]
        ans.extend(replace_token_with_antonym(tokens, head_token_ind, head_token_line))


    arg_chunks = [(ind, line) for ind, line in enumerate(knp_lines) if is_chunk(line) and line.split(' ')[2] == (str(last_chunk_num) + "D") and re.search("<係:[^>]+>", line)]
    for arg_chunk_ind, arg_chunk in arg_chunks:
        try:
            head_token_of_arg = get_head_token_of_chunk(knp_lines, arg_chunk_ind)
            if get_pos_of_token(head_token_of_arg) == "名詞" or ("<修飾>" in arg_chunk):
                #まず、argの主辞の名詞に反義語が存在するかどうか?
                if "反義" in head_token_of_arg:
                    token_ind = get_token_ind(knp_lines, arg_chunk_ind, head_token_of_arg)
                    ans.extend(replace_token_with_antonym(tokens, token_ind, head_token_of_arg))

        except:
            pass #FIXME ひどくない?

        #次に、そのチャンクにかかっている動詞or名詞or形容詞に反義語が存在するか?
        #FIXME これだと、「分かりにくい表現を使わないでください」が変換できない
        chunk_num = get_chunk_num(arg_chunk)
        for mod_chunk_ind, mod_chunk in [(ind, line) for ind, line in enumerate(knp_lines) if is_chunk(line) and line.split(' ')[2] == (str(chunk_num) + "D")]:
            try:
                mod_chunk_token = get_head_token_of_chunk(knp_lines, mod_chunk_ind)
                if get_pos_of_token(mod_chunk_token) == "名詞" or get_pos_of_token(mod_chunk_token) == "形容詞" or get_pos_of_token(mod_chunk_token) == "動詞":
                    if "反義" in mod_chunk_token:
                        tok_ind = get_token_ind(knp_lines, mod_chunk_ind, mod_chunk_token)
                        ans.extend(replace_token_with_antonym(tokens, tok_ind, mod_chunk_token))
            except:
                pass #FIXME ひどくない?

    ans = [s for s in ans if s != orig_str] #元の文は除く
    ans = list(set(ans)) #重複した文を削除
    for s in ans:
        print (orig_str + '\t' + s)

#トークンだけで数えた時のインデックスを返す
def get_token_ind(knp_lines, chunk_ind, token_line):
    return [tok_ind for (tok_ind, (ind, line)) in enumerate([(i,knp_line) for i, knp_line in enumerate(knp_lines) if is_token(knp_line)]) if ind > chunk_ind and line == token_line][0]


def get_chunk_num(chunk_line):
    if (not is_chunk(chunk_line)):
        raise Exception('arugment error')

    ans = 0
    try:
        ans = int(chunk_line.split(' ')[1])
    except:
        raise Exception('Use -print-num option when running KNP')

    return ans


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
