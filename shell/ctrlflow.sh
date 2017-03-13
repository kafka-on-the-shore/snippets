#!/bin/bash

# some variables
# $0: command itself
# $1 ~ n: the n opt
# $#: number of parameters, not include command itself
# $@ param list, not include command itself. It's a array

a_array=(one two three)
for item in ${a_array[@]}; do
        echo "hi, $item"
done

# truncate string
# # means truncate minimal; double# means truncate from right.
# % means truncate greedly; double% means from right
str="http://www.abc.com/index.html"
echo $str
echo "str#*/:"${str#*/} # return www.abc.com/index.html
echo "str##*/:"${str##*/} #retrun index.html
echo "str%/*:"${str%/*} # return http://www.abc.com
echo "str%%/*:"${str%%/*} # return http


# IF
#
# [ -a FILE]: if file exist
# [ -b FILE]: if exist and a block-specific file. Similar if exist and:
#               -c for char, -d for directory, -f for regular, -h(-L) symbolic link
#               -p for pipe, -r for readable, -w for writable, -x for executable
#               -S for socket
#
# [ -z STRING]: string is zero length(empty), -n for non-zero, = or == for equal, != for not equal
#
# [ ARG1 OP ARG2 ]: -eq, -ne, -lt, -le, -gt, -ge. ARG1 and ARG2 are integers.
# [ !EXPR ]: if not
# [ (EXPR) ]: return the value of EXPR
# [ EXPR1 -a EXPR2 ]: if (expr1 && expr2)
# [ EXPR1 -o EXPR2 ]: if (expr1 || expr2)
#
# [] vs. [[]]
# [[ prevent word splitting of variable value, also it prevent pathname expansion.
# !!!! use [[ ]] instead of [], for bash only !!!!

if [[ $(whoami) != 'root' ]]; then
        echo "must be root to run $0"
else
        echo "run as root"
fi

if [[ $1 =~ ^yes(abc)?$ ]]; then
        echo "there"
else
        echo "here"
fi


# simple
case $2 in
        [1-6]*)
                msg="low"
                ;;
        [7-8]*)
                msg="normal"
                ;;
        9[1-8])
                msg="high"
                ;;
        99)
                msg="die"
                ;;
        *)
                msg="invlid"
                ;;
esac

echo "second param msg: ${msg}"

# initscript example
case "$1" in
        start)
                start
                ;;
        stop)
                stop
                ;;
        restart)
                start
                stop
                ;;
        *)
                echo $"Usage: $0 {start|stop|restart|status}"
                #exit 1
esac


# for
for arg in $@; do
        echo "for : $arg"
done

# while
wholist=(
        'Bob <bob@abc.com>'
        'Job <job@edf.com>'
        'Larray <larray@ghi.com>'
)

count=0
while [[ "x${wholist[count]}" != "x" ]]; do
        count=$(( $count + 1))
done
echo "total $count in wholist"
echo "length of wholist ${#wholist}"
        
