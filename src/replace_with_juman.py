#coding:utf-8
import sys
import replace_lib

def sentence_func(juman_lines):
    orig_str = "".join([line.split(' ')[0] for line in juman_lines if line[0] != '@'])

    #まずは@を解消
    juman_lines_list = replace_lib.disambiguate_juman_line(juman_lines)

    #語の置き換え
    ans = []
    for disambiguated_juman_lines in juman_lines_list:
        enumerated_antonym_pairs = replace_lib.enumerate_antonym_pairs(disambiguated_juman_lines)
        # antonym_pairs_lst = extract_last_antonym_pairs(enumerated_antonym_pairs)
        antonym_pairs_lst = replace_lib.replace_one_word(enumerated_antonym_pairs)
        for antonym_pairs in   antonym_pairs_lst:
            s = replace_lib.replace_with_antonym_pairs(disambiguated_juman_lines, antonym_pairs)
            ans.append(s)

    ans = [s for s in ans if s != orig_str] #元の文は除く
    ans = list(set(ans)) #重複した文を削除
    for s in ans:
        print (orig_str + '\t' + s)


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
