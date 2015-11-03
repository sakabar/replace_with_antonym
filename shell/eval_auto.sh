#!/bin/zsh

set -ue

#反義語対の生成→RNNLMでの評価という一例の処理をボタン一発で行う
#実行は、
#$cd /path/to/replace_with_antonym
#$./shell/eval_auto.sh

#ログを取る
function logging(){
    if [ $# -ne 3 ]; then
	echo "argument error: logging"
	exit 1
    fi
    str=$1
    gdate_command=$2
    logfile=$3

    echo `$gdate_command +"%Y/%m/%d %H:%M:%S : "`$str | tee -a $logfile >&2
}


if [ $# -ne 1 ]; then
    echo "argument error">&2
    exit 1
fi
knp_file_name=$1 #禁止表現を含む文を構文解析したKNPファイル

antonym_replace_dir=~/work/replace_with_antonym #反義語置き換えに関するディレクトリ

#dateコマンドはGNUのdateコマンドを利用する
date_command=gdate
if `which $date_command >/dev/null`; then
    #gdateがあればオーケー
else
    #なければ、通常のdateコマンドがGNU dateかどうかをチェック
    if [ `date --version | grep -c "GNU"` -gt 0 ]; then
	#オーケー。
	date_command=date
    else
	#NG。このdateはGNU dateではない。
	echo "Please install GNU date.">&2
	exit 1
    fi
fi


# #実験した日付・時刻のディレクトリを作成
eval_file_dir=eval_`$date_command +"%Y%m%d_%H%M_%S"`
logfile=$antonym_replace_dir/$eval_file_dir/log.txt

mkdir $eval_file_dir
logging "create $eval_file_dir" $date_command $logfile
touch $logfile

cp $knp_file_name $eval_file_dir #入力したKNPファイルも念のためコピーしておく

logging "start antonym replacing" $date_command $logfile
cat $knp_file_name | python src/main_replace_with_antonym.py > $eval_file_dir/output.txt 
logging "end antonym replacing" $date_command $logfile

rnnlm_dir=~/work/use_rnnlm
logging "move to $rnnlm_dir/$eval_file_dir" $date_command $logfile
cd $rnnlm_dir
./shell/setup.sh $eval_file_dir
logging "rnnlm_dir setup" $date_command $logfile

cp $antonym_replace_dir/$eval_file_dir/output.txt $rnnlm_dir/$eval_file_dir/data/output.txt

# cd $rnnlm_dir
lv $eval_file_dir/data/output.txt | awk '{print $1}' > $eval_file_dir/data/orig.txt
lv $eval_file_dir/data/output.txt | awk '{print $2}' > $eval_file_dir/data/changed.txt

logging "rnnlm_dir/shell/exe.sh start" $date_command $logfile
./shell/exe.sh $eval_file_dir
logging "rnnlm_dir/shell/exe.sh end" $date_command $logfile

logging "moving files from $rnnlm_dir to $antonym_replace_dir" $date_command $logfile
mv -i $rnnlm_dir/$eval_file_dir/* $antonym_replace_dir/$eval_file_dir/
rmdir $rnnlm_dir/$eval_file_dir/
