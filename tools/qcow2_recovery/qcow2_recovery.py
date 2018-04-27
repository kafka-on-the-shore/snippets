#!/usr/bin/python

'''
Qcow2 image recovery tool.

This tool is aiming for L2 table corrupt issue. Qcow2 arranges data in a
two-level indexed way and there is no backup for L1 and L2 tables. That
means if the entries in any table is corrupt, we could not recovery the
data corresponding the entry any more. This tool assumes that the L1 table
was OK, but some of the L2 table is corrupt due to disk was miss over-written,
the this tool will find all failed L2 entries and set them to zero which
represent the entry is unused. In this way, we'll get a 'correct' image while
some of the data area were lost.

how it works
1. open device
2. seek L1 table
3. iterate L1 table with Xupack
4. read all L2 table element
5.     if L2 element is invalid, remember it and set it to zero
6. if qcow2 version == 3 and incompatible_features bits were set, clear them.

option:
 * -i: <broken disk/image path>
 * -c: check image only but not do modification
 
usage example: 
 * check the image: `./qcow2_recovery.py -i /dev/dm-4 -c`
 * recovery image:  `./qcow2_recovery.py -i /dev/dm-4`
''' 

import struct
import argparse

qcow2_header_format = {
    'magic':                (0x0,  '3s'),
    'version':              (0x4,  '>I'),
    'cluster_bits':         (0x14, '>I'),
    'size':                 (0x18, '>Q'),
    'l1_size':              (0x24, '>I'),
    'l1_table_offset':      (0x28, '>Q'),
    'incompatible_features':(0x48, '>Q'),
    '__length':             0x50
}

qcow2_l1_entry_format = {
    'l1_entry':             (0x0, '>Q'),
    '__length':             0x8
}

qcow2_l2_entry_format = {
    'l2_entry':             (0x0, '>Q'),
    '__length':             0x8
}

ENTRY_MASK=0x3fffffffffffffff

class Xunpack:
    def __init__(self, object_layout, f, offset):
        self._layout = object_layout
        self._raw = self.__get_raw(f, offset)

    def __get_raw(self, f, offset):
        f.seek(offset)
        return f.read(self._layout['__length'])                                                                                                           

    def __getitem__(self, var):
        return self.get(var)

    def get(self, var, length=None):
        offset, fmt = self._layout[var]
        if length:
            # we need to dedicate the length exactly for strings
            fmt = str(length) + fmt
        ret = struct.unpack_from(fmt, self._raw, offset)
        if len(ret) == 0:
            return None
        elif len(ret) == 1:
            return ret[0]
        else:
            return ''.join(ret)

    def length(self):
        return self._layout['__length']

    def dump(self):
        out = {}
        for k, v in self._layout.items():
            #print "%s:%s" % (k, hex(self.get(k)))
            temp = self.get(k) 
            if type(temp) == int:
                temp = hex(temp)
            out[k] = temp
        return out

def l2_entry_check(l2_offset, entry):
    # check if l2 entry was valid: it should be aligned with cluster size
    if entry['l2_entry'] & 0xffff:
        print "bad l2_entry: {:x} at {:x}".format(entry['l2_entry'] & ENTRY_MASK, l2_offset)
        return False
    else:
        return True

def parse_image(devpath, do_check_only):
    cluster_counter = 0
    bad_l2_entries = []
    incompatible_features = 0
    with open(devpath, 'rb') as f:
        header = Xunpack(qcow2_header_format, f, 0)
        if header['magic'] != 'QFI':
            print "Wrong format for there is not QCOW2 magic"
            return
        else:
            print "input image is QCOW2 format version %d" % header['version']

        # Read information from header
        cluster_size = 2 ** header['cluster_bits']
        qcow2_size = header['size']
        l1_size = header['l1_size']
        l1_table_offset = header['l1_table_offset']
        l2_clusters_per_entry = 2 ** (header['cluster_bits'] - 3)
        if header['version'] == 3:
            incompatible_features = header['incompatible_features']

        print "--------------- image info ----------------"
        print "image size:           0x{:x}".format(qcow2_size)
        print "cluster size:         0x{:x}".format(cluster_size)
        print "L1 entry size:        0x{:x}".format(l1_size)
        print "L1 table address:     0x{:x}".format(l1_table_offset)
        print "L2 cluster per table: 0x{:x}".format(l2_clusters_per_entry)
        if incompatible_features:
            if incompatible_features & 0x1:
                print "incompatible_features \"Dirty bit\" is set"
            if incompatible_features & 0x2:
                print "incompatible_features \"Corrupt bit\" is set"
        print "-------------------------------------------"

        # iterate all L1 and L2 tables
        for i in range(0, l1_size):
            l1_offset = l1_table_offset + i*8
            l1_entry = Xunpack(qcow2_l1_entry_format, f, l1_offset)
            #print "l1: {:x}".format(l1_entry['l1_entry'] & ENTRY_MASK)
            if l1_entry['l1_entry'] == 0:
                continue

            l2_offset = l1_entry['l1_entry'] & ENTRY_MASK
            for j in range(0, l2_clusters_per_entry):
                #print "{:x}:".format(l2_offset),
                #print"l2_entry_offset: {:x}".format(l2_offset)
                l2_entry = Xunpack(qcow2_l2_entry_format, f, l2_offset)
                l2_offset += 8

                #print "l2: {:x}".format(l2_entry['l2_entry'] & ENTRY_MASK)
                if l2_entry['l2_entry'] == 0:
                    continue

                cluster_counter += 1
                if not l2_entry_check(l2_offset - 8, l2_entry):
                    bad_l2_entries.append(l2_offset - 8)

    if not do_check_only:
        # clear all corrupt L2 table entries
        with open(devpath, 'r+') as f:
            for entry in bad_l2_entries:
                f.seek(entry, 0)
                f.write(struct.pack('Q', 0))

        # clear corrupt bits
        if incompatible_features:
            with open(devpath, 'r+') as f:
                f.seek(0x48, 0)
                f.write(struct.pack('Q', 0))

    print "image count: {:x}".format(cluster_counter*65536)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="qcow2 recovery tool")
    p.add_argument("-i", "--img", action="store", help="qcow2 image to recovery")
    p.add_argument("-c", "--check_only", action="store_true", default=False, help="only do check, do not recovery the image")
    args = p.parse_args()
    if args.img:
        parse_image(args.img, args.check_only)
