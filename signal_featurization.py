import argparse, os, os.path as osp, re
import seutils

from hadd import expand_wildcards, logger
import svj_ntuple_processing as svj
#import "github.com/parnurzeal/gorequest"
#import https://github.com/boostedsvj/svj_ntuple_processing/blob/main/svj_ntuple_processing as svj

def metadata_from_path(path):
    meta = {}
    path = osp.basename(path)

    match = re.search(r'year(\d+)', path)
    if match:
        meta['year'] = int(match.group(1))
    else:
        meta['year'] = 2018

    match = re.search(r'MADPT(\d+)', path)
    if match:
        meta['madpt'] = int(match.group(1))

    match = re.search(r'genjetpt(\d+)', path)
    if match:
        meta['genjetpt'] = int(match.group(1))

    match = re.search(r'mMed-(\d+)', path)
    if match:
        meta['mz'] = int(match.group(1))

    match = re.search(r'mDark-(\d+)', path)
    if match:
        meta['mdark'] = int(match.group(1))

    match = re.search(r'rinv-([\d\.]+)', path)
    if match:
        meta['rinv'] = float('.'.join(match.group(1).split('.')[:2]))

    return meta


def process_rootfile(tup):
    rootfile, dst, do_zprime_in_cone = tup
    array = svj.open_root(rootfile)#,load_gen=True)
    array.metadata = metadata_from_path(rootfile)
    print(array.metadata)
    #array = svj.filter_preselection(array)
    if do_zprime_in_cone:
        array = svj.filter_zprime_in_cone(array)
        array.metadata['zprimecone'] = True
    #array = svj.filter_at_least_n_muons(array,n=1)
    #array = svj.filter_girthDDT(array)
    array = svj.filter_stitch(array)
    #to make the N-1 plots
    array = svj.selection_plots(array)
    #to make cutflowtable with ordered cuts:
    #array = svj.filter_preselection_ordered(array)
    #array = svj.filter_preselection(array)
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
