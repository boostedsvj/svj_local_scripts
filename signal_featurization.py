import argparse, os, os.path as osp, re
import seutils

from hadd import expand_wildcards, logger
import svj_ntuple_processing as svj


def metadata_from_path(path):
    meta = {}
    path = osp.basename(path)

    match = re.search(r'year(\d+)', path)
    if match:
        meta['year'] = int(match.group(1))
    else:
        meta['year'] = 2018

    match = re.search(r'madpt(\d+)', path)
    if match:
        meta['madpt'] = int(match.group(1))

    match = re.search(r'genjetpt(\d+)', path)
    if match:
        meta['genjetpt'] = int(match.group(1))

    match = re.search(r'mz(\d+)', path)
    if match:
        meta['mz'] = int(match.group(1))

    match = re.search(r'mdark(\d+)', path)
    if match:
        meta['mdark'] = int(match.group(1))

    match = re.search(r'rinv([\d\.]+)', path)
    if match:
        meta['rinv'] = float('.'.join(match.group(1).split('.')[:2]))

    return meta


def process_rootfile(tup):
    rootfile, dst, do_zprime_in_cone = tup
    array = svj.open_root(rootfile)
    array.metadata = metadata_from_path(rootfile)
    array = svj.filter_preselection(array)
    if do_zprime_in_cone:
        array = svj.filter_zprime_in_cone(array)
        array.metadata['zprimecone'] = True
    cols = svj.bdt_feature_columns(array)
    cols.save(dst)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dst', type=str, default='.')
    parser.add_argument('rootfiles', nargs='+', type=str)
    parser.add_argument('-n', '--nthreads', default=10, type=int)
    parser.add_argument('--cone', action='store_true', help='Filter signal with truth info')
    args = parser.parse_args()

    rootfiles = expand_wildcards(args.rootfiles)

    fn_args = []
    for rootfile in rootfiles:
        dst = osp.join(args.dst, osp.basename(rootfile).replace('.root', '.npz'))
        if seutils.path.has_protocol(dst) and seutils.isfile(dst):
            logger.info('File %s exists, skipping', dst)
            continue
        fn_args.append((rootfile, dst, bool(args.cone)))

    import multiprocessing as mp
    p = mp.Pool(args.nthreads)
    p.map(process_rootfile, fn_args)
    p.close()
    p.join()




if __name__ == '__main__':
    main()