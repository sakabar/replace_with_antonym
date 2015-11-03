#coding: utf-8
from sexpdata import loads, dumps, Symbol
import sys

def get_sexp(f):
    s = "(" + open(f).read() + ")"
    s_exp = loads(s)
    return s_exp

def get_verb_katuyou(sexp, katuyou_type, verb_form):
    for verb_type_sexp in sexp:
        verb_type = verb_type_sexp[0]
        verb_form_sexp = verb_type_sexp[1]

        if verb_type == Symbol(katuyou_type):
            for sexp2 in verb_form_sexp:
                cond = False
                if (katuyou_type == "ナ形容詞" or katuyou_type == "ナノ形容詞" or katuyou_type == "ナ形容詞特殊") and (verb_form != "基本形") and (verb_form != "語幹") and not ("ダ列" in verb_form):
                        cond = sexp2[0] == Symbol("ダ列" + verb_form)
                else:
                    cond = sexp2[0] == Symbol(verb_form)

                if cond:
                    return dumps(sexp2[1]).encode('utf-8')

    #例外
    # print katuyou_type
    # print verb_form
    raise Exception("%s, %s" % (katuyou_type, verb_form))

def get_katuyou_str_from_id(s_exp, katuyou_type_ind, katuyou_form_ind):
    ans1 = s_exp[katuyou_type_ind-1][0]
    ans2 = s_exp[katuyou_type_ind-1][1][katuyou_form_ind-1][0]
    return (dumps(ans1).encode('utf-8'), dumps(ans2).encode('utf-8'))
