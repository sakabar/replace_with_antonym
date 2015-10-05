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
                if sexp2[0] == Symbol(verb_form):
                    return dumps(sexp2[1]).encode('utf-8')
    #例外
    # print katuyou_type
    # print verb_form
    raise

