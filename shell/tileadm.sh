#!/bin/bash

tile_list=(
        "appserver|16M"
        "webserver|16M"
        "iotserver|16M"
        "batchserver|20M"
)

vg=""
id=""
src_id=""
action=""
do_copy="false"

        
while getopts ":c:d:lg:x:s:" opt; do
        case $opt in
        c)
                action="create"        
                id=$OPTARG
                ;;
        d)
                action="delete"
                id=$OPTARG
                ;;
        l)
                action="list"
                lvdisplay
                exit 1
                ;;
        g)
                vg=$OPTARG
                ;;
        x)
                action="copy"
                id=$OPTARG
                ;;
        s)
                src_id=$OPTARG
                ;;
        ?)
                echo "Usage:"
                echo "create: $0 -c <id> -g <vg_name>"
                echo "delete: $0 -d <id> -g <vg_name>"
                echo "list:   $0 -l -g <vg_name>"
                echo "copy:   $0 -x <id> -g <vg_name> -s <src_id>"
                exit 1
                ;;
        esac
done

function affirm()
{
        echo "-----------------------------"
        echo "You are taking !$1! operation"
        echo "vg: ${vg}"
        echo "tile id: ${id}"
        echo "-----------------------------"
        if [[ $action = "copy" ]]; then
                echo "src tile id: ${src_id}"
        fi
        echo "-----------------------------"
        read -p "Apply operation [y|n], default n:"
        if [[ $REPLY != 'y' ]]; then
                exit 1
        fi
}

affirm $action

for tile in ${tile_list[@]}; do
        name=${tile%%|*}
        size=${tile#*|}

        if [[ $action = "create" && -n $vg && -n $id ]]; then
                echo "create: ${name}${id}, $size"
                lvcreate -y -L $size -n ${name}${id} $vg
        fi

        if [[ $action = "copy" && -n $vg && -n $id && -n $src_id ]]; then
                echo "copy: from ${name}${src_id} to ${name}${id}, $size"
                dd if=/dev/$vg/${name}${src_id} of=/dev/$vg/${name}${id} bs=4M
        fi

        if [[ $action = "delete" && -n $vg && -n $id ]]; then
                echo "remove: ${name}${id}"
                lvremove -y /dev/$vg/${name}${id}
        fi
done

