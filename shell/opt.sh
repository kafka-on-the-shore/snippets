#!/usr/bin/sh
buffer="null"
while getopts ":d:ji" opt; do
        case $opt in
        d)
                buffer=$OPTARG                 # get the value
                ;;
        i)
                echo "opt index is $OPTIND" # return the index of opt 'i'
                ;;
        j)
                # you can use -ij, but not -ji. Because after j option, it would exit.
                echo "I'm j"
                exit 1
                ;;
        ?)
                echo "Usage: $0 [-d DAY]"   # when use -h or --help, must be the last one
                exit 1
                ;;
       esac
done

echo "Your input is $buffer"

