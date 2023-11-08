"""
Like hadd.py, but takes (remote) directories and creates 1 hadded file per directory.
"""
import glob, os, os.path as osp, tempfile, shutil
import seutils
from hadd import WORKDIR, logger, expand_wildcards, PooledMerger, uid, ntuplenpz_concatenate
import svj_ntuple_processing as svj


def process_directory(tup):
    directory, dst = tup
    #print(dst, '*'*5, directory)
    npzfiles = glob.glob(directory + '*.npz')
    logger.info('Processing %s -> %s (%s files)', directory, dst, len(npzfiles))
    # try:
    cols = []
    for f in npzfiles:
        try:
            cols.append(svj.Columns.load(f, encoding='latin1'))
        except Exception as e:
            logger.error('Failed for file %s, error:\n%s', f, e)
    concatenated = svj.concat_columns(cols)
    concatenated.save(dst)
    # except Exception as e:
    #     logger.error('Failed for directory %s, error:\n%s', directory, e)


def dst(stageout, directory):
    return osp.join(
        stageout, osp.basename(osp.dirname(directory)), osp.basename(directory) + '.npz'
        )

'''def dst(stageout, directory):
    #return osp.join(stageout, osp.basename(osp.dirname(directory)))
    return osp.basename(osp.dirname(directory)) + '.npz'''

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dst', type=str, default='.')
    parser.add_argument('directories', nargs='+', type=str)
    parser.add_argument('-n', '--nthreads', default=10, type=int)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--dry', action='store_true')
    args = parser.parse_args()

    directories = expand_wildcards(args.directories)

    fn_args = []
    for d in directories:
        #print('directory is: ', d, ' stageout: ', args.dst)
        #print(args.dst)
        #outfile = dst(args.dst, d)
        outfile = osp.join(osp.basename(osp.dirname(d))+'.npz')
        #print('*'*5, ' the outfile is: ', outfile)
        '''if seutils.isfile(outfile):
            logger.info('File %s exists; skipping %s', outfile, d)
            continue'''
        fn_args.append((d, outfile))
        #print(fn_args)
        

    import multiprocessing as mp
    p = mp.Pool(args.nthreads)
    p.map(process_directory, fn_args)
    p.close()
    p.join()
