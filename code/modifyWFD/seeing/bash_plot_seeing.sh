#!/bin/bash

# source sims_maf
source /global/common/software/lsst/cori-haswell-gcc/stack/setup_current_sims.sh
# set up my own version rn
setup sims_maf -r /global/homes/a/awan/LSST/lsstRepos/sims_maf

# run the script
# OpSim seeing
python /global/homes/a/awan/LSST/lsstRepos/ObsStrat/code/modifyWFD/seeing/plot_seeing_maps.py \
                                --db_path='/global/cscratch1/sd/awan/dbs_wp_unzipped' \
                                --outDir='/global/cscratch1/sd/awan/lsst_output/seeing/' \
                                --baseline_and_wide_only --nside=256 &
# Eric N.'s outputs
for tag  in ow6 ow6c ow7 ow7c
do
    python /global/homes/a/awan/LSST/lsstRepos/ObsStrat/code/modifyWFD/seeing/plot_seeing_maps.py \
                                --db_path=/global/cscratch1/sd/awan/owsee_outputs/${tag} \
                                --outDir='/global/cscratch1/sd/awan/lsst_output/seeing/' \
                                --baseline_and_wide_only --nside=256 &
done