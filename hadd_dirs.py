"""
Like hadd.py, but takes (remote) directories and creates 1 hadded file per directory.
"""
import glob, os.path as osp, tempfile
import seutils
from hadd import logger, hadd_chunks, uid

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dst', type=str, default='.')
    parser.add_argument('directories', nargs='+', type=str)
    parser.add_argument('-n', '--nthreads', default=10, type=int)
    parser.add_argument('-c', '--chunksize', default=10, type=int)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    # Take care of any wildcards, remote or local
    directories = []
    for pat in args.directories:
        if '*' in pat:
            if seutils.path.has_protocol(pat):
                directories.extend(seutils.ls_wildcard(pat))
            else:
                directories.extend(glob.glob(pat))
        else:
            directories.append(pat)

    # Run the hadding per directory
    with tempfile.TemporaryDirectory('hadd', dir='.') as tmpdir:
        for directory in directories:

            # Gather input rootfiles
            if seutils.path.has_protocol(directory):
                rootfiles = seutils.ls_wildcard(directory + '/*.root')
            else:
                rootfiles = glob.glob(directory + '/*.root')

            dst = osp.join(args.dst, osp.basename(directory) + '.root')

            if args.debug:
                print(f'directory={directory}, #rootfiles={len(rootfiles)}, dst={dst}')
                continue

            hadd_chunks(rootfiles, dst, args.nthreads, args.chunksize, tmpdir)