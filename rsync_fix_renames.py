#!/bin/python -ttu

# Fix file renaming after an rsync, to use hardlinks. This is necessary since rsync's "--fuzzy" option is useless under most conditions.
#
# Add the following line to /etc/rsnapshot.conf:
# cmd_postexec    /root/rsync_fix_renames.py /.snapshots/hourly.1/ /.snapshots/hourly.0/
#
# Note that this script will not do much of anything useful if a backup source contains significant amounts of file data where the files
# had identical modification times and identical file sizes. If there's some actual real-world case where that happens, it would need some
# unknown change to cope with that.

import filecmp, os, sys

srce_path, dest_path = sys.argv[1:3]
print "Scanning source '%s' -> destination '%s' for renames/moves..." % (srce_path, dest_path)
if os.stat(srce_path).st_mtime > os.stat(dest_path).st_mtime:
    raise Exception('source "%s" newer than destination "%s"' % (srce_path, dest_path))

### For source and destination, get every mtime/size key, and point it to a filename/inode.

def get_entries(path):
    ret = {}
    for (dirpath, _, filenames) in os.walk(path):
        for filename in filenames:
            fpath = os.path.join(dirpath, filename)
            stat = os.stat(fpath)
            ret[(stat.st_mtime, stat.st_size)] = (fpath, stat.st_ino)
    return ret

srce_entries = get_entries(srce_path)
dest_entries = get_entries(dest_path)

### Weed out all the entries that are already correctly a hardlink, and assess the amount of work to be done in comparisons.

cmp_list = []
cmp_bytes = 0
for key in srce_entries:
    if key in dest_entries:
        if srce_entries[key][1] == dest_entries[key][1]:
            pass #print "already hard link:\n%s\n%s\n" % (srce_entries[key], dest_entries[key])
        else:
            cmp_list.append((srce_entries[key][0], dest_entries[key][0], key[1]))
            cmp_bytes += key[1]

### Go through list, compare and make hardlink for matches.

if cmp_list:
    print "Comparing: %d files, %d bytes" % (len(cmp_list), cmp_bytes)
    cur_bytes = 0
    for cmper_n, cmper in enumerate(cmp_list):
        cur_bytes += cmper[2]
        if filecmp.cmp(cmper[0], cmper[1], shallow=False):
            print "file %5.3f%% bytes %5.3f%% file %d/%d bytes %d/%d, link:\n%s\n%s\n" % (
                100.0*cmper_n/len(cmp_list), 100.0*cur_bytes/cmp_bytes,
                cmper_n, len(cmp_list), cur_bytes, cmp_bytes, cmper[0], cmper[1])
            os.link(cmper[0], cmper[1]+'.rsync_fix_renames.tmp')
            os.rename(cmper[1]+'.rsync_fix_renames.tmp', cmper[1])
        else:
            print "false positive on:\n%s\n%s\n" % (cmper[0], cmper[1])
