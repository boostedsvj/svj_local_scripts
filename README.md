# Local processing of root files for boosted SVJ analysis

This repo has some scripts to perform certain reasonably fast operations locally.

## Setup

```
mkdir -p env/bin
mkdir -p env/lib/python3.6/site-packages
```

Then every time you open a new shell:

```
source activate.sh
```


## Signal HADDing: At .root level

```
python hadd_dirs.py -d root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/orthogonalitystudy/HADD/ root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/orthogonalitystudy/TREEMAKER/madpt300_* --chunksize 50
```


## BDT featurization

```
# Nov 2

# Copy features to local area (about 5-10 min):
xrdcp -r --parallel 4 root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/bdt_features/bkg_nov03/BDTFEATURES .

# Concatenate into single .npz files and copy to storage (<1 min):
python hadd_bdtbkgfeatures.py -d root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/bdt_features/bkg_nov03/HADD BDTFEATURES/*/*
```

For signal, there is no need to first copy the files; It's fast enough to just load them from the storage element directly. 

```
python signal_featurization.py -d root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/bdt_features/signal_nov02 root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/orthogonalitystudy/HADD/madpt300_*.root

python signal_featurization.py --cone -d root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/bdt_features/signal_nov02_truthcone root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/orthogonalitystudy/HADD/madpt300_*.root

# Nov 22: Using svj_ntuple_processing==0.7

python signal_featurization.py --cone -d root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/bdt_features/signal_nov22_truthcone root://cmseos.fnal.gov//store/user/lpcdarkqcd/boosted/orthogonalitystudy/HADD/madpt300_*.root
```
