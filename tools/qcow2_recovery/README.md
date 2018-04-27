# Qcow2 image recovery tool.

This tool is aiming for L2 table corrupt issue. Qcow2 arranges data in a
two-level indexed way and there is no backup for L1 and L2 tables. That
means if the entries in any table is corrupt, we could not recovery the
data corresponding the entry any more. This tool assumes that the L1 table
was OK, but some of the L2 table is corrupt due to disk was miss over-written,
the this tool will find all failed L2 entries and set them to zero which
represent the entry is unused. In this way, we'll get a 'correct' image while
some of the data area were lost.


## option:
 * -i: <broken disk/image path>
 * -c: check image only but not do modification
 
## usage example: 
 * check the image: `./qcow2_recovery.py -i /dev/dm-4 -c`
 * recovery image:  `./qcow2_recovery.py -i /dev/dm-4`
```

> a very crude script for qcow2 image recovery
