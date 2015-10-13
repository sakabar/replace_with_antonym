#coding:utf-8
import sys
import re

#ドキュメント情報(#から始まる行)と<格解析結果>の行が含まれたテキストを
#標準入力から読み込み、述語とその項の数を出力する

regex = re.compile("^<格解析結果")


def split_and_print(line):
    regex = "<格解析結果:([^/]+/[^:]+:[^:]+)\d+:([^>]+)>"
    p = re.compile(regex)
    m = p.search(line)
    if m:
        pred = m.group(1)
        count = len([l for l in m.group(2).split(';') if not ("/U/" in l)])
        print "%s;%s" % (pred, count)
        # if count >= 4:
        #     print line
    else:
        print "No-match"
        sys.exit(1)
    # return 

for line in sys.stdin:
    line = line.rstrip()

    if line[0] == '#':
        print line
    elif regex.search(line):
        split_and_print(line)
    else:
        raise Exception('bug?')
