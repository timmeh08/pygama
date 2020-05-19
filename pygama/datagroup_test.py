#!/usr/bin/env python3
import os
from parse import parse
from pprint import pprint
from string import Formatter

def main():
    """
    testing for datagroup.
    organize files from different experiments into a searchable stucture,
    using some rules about filenames and which directories to include.

    NOTES:
    - this gets complicated when we lose 1-to-1 matching between unique
      file keys, i.e. given a key (row of the master DF), it's not possible
      to get all the raw/dsp/hit files.  this kind of happens w/ LEGEND when we
      split apart by subsystem.

    - we want a mode where we cache a list of unique keys.  this is kinda
      like an early version of a run database.  it should probably be a JSON
      format, maybe eventually stored in legend-metadata for each experimental
      configuration.

    row 1 [daq file] [raw file] [dsp file] [dsp exists?] [hit file] [expt cols] [calib const file] [aoe cut value file]
    """
    group_lpgta()
    # group_cage()
    # group_surf()


def group_lpgta():
    """
    todo: move this stuff to config files: LPGTA.json, LPGTA_runDB.json
    """
    # base DAQ and LH5 directories
    daq_dir = '/global/cfs/cdirs/legend/data/lngs/pgt'
    lh5_dir = '/global/cfs/cdirs/legend/users/wisecg/LPGTA'

    config = './LPGTA.json' # pygama/experiments/lpgta
    runDB = './LPGTA_runDB.json'
    fileDB = './fileDB.json' # DataFrame.to_json

    # templates and unique key
    # note: run info is part of the folder structure here.
    # daq_tmp = '{YYYYmmdd}-{hhmmss}-{rtp}.fcio'
    daq_tmp = '/run{run:0>4d}-{label}/{YYYYmmdd}-{hhmmss}-{rtp}.fcio'

    lh5_tmp = '{expt}_r{run:0>4d}_{YYYYmmdd}T{hhmmss}Z_{rtp}_{sysn}_{tier}.lh5'

    uni_key = ['run','YYYYmmdd','hhmmss'] # don't need all fields in daq file

    expts = ['LPGTA'] # expt
    tier_dirs = ['raw','dsp','hit'] # tier
    subsystems = ['geds','spms','auxs'] # sysn
    run_types = ['phy','cal'] # rtp

    evt_types = ['evt','tmap'] # special for legend?  keep separate or add as tier?

    # piece of the runDB.  we have to include expt-specific stuff here.
    # could use this to add add'l columns to the DataGroup FileKey DF.
    runDB = {
        "0023":{"dir":"run0023-baseline-test-new-head", "cmap":"pgt_mar.json"},
        "0022":{"dir":"run0022-baseline-test-new-head", "cmap": "pgt_mar.json"}
        }

    walk_daq_dir(daq_dir, daq_tmp)


def group_cage():
    """
    """
    # -- CAGE (ORCA) config --
    daq_dir = '/Volumes/LaCie/Data/CAGE/Data'
    lh5_dir = '/Volumes/LaCie/Data/CAGE/lh5' # raw/dsp/hit | geds...

    # note: using name 'cycle', not 'run', to mark individual files.
    daq_tmp = '{YYYY}-{mm}-{dd}-{prefix}Run{cycle}'

    lh5_tmp = '{expt}_run{run}_cyc{cycle}_{tier}.lh5'

    uni_key = ['YYYY','mm','dd','cycle']

    expts = ['LPGTA'] # expt
    tier_dirs = ['raw','dsp','hit'] # tier
    subsystems = ['oppi','icpc'] # sysn
    run_types = ['phy','cal'] # rtp

    # what to ignore
    ignore = ['.log','.DS_Store']

    # piece of the runDB.  will have to include expt-specific stuff here.
    runDB = {
        "0":{"cycles":[1,10], "note":"init cs+bkg runs 2500 V"},
        "1":{"cycles":[11,14], "note":"init cs+bkg runs, 2800 V"}
        }

    walk_daq_dir(daq_dir, daq_tmp, ignore)


def group_hades():
    """
    here we want to handle multiple detectors/char run types in a sane way.
    maybe each detector gets its own LH5 directory?  or could we stick in
    groups to replace 'geds', like 'IC1234A','IC2345A', ... ?

    - dir: /global/cfs/cdirs/legend/data/hades/I02166B/tier0/ba_HS4_top_dlt
    - example: char_data-I02166B-ba_HS4_top_dlt-run0001-191025T153307.fcio
    - unique key: [run, YYmmdd, hhmmss]
    """
    print('lol tbd')


def group_surf():
    """
    """
    print('tbd')


def walk_daq_dir(daq_dir, daq_tmp, ignore=None):
    """
    build a list of unique file keys by scanning the daq directory,
    and comparing to the template.  this function should be smart enough
    to work for all experiments, pulling information out of the file + path.
    """
    cols = [fn for _,fn,_,_ in Formatter().parse(daq_tmp) if fn is not None]
    cols.append('daq_file')
    print(cols)

    daq_files = []
    for path, folders, files in os.walk(daq_dir):

        for f in files:

            # in some cases, we need information from the path to the file.
            # pull off the daq_dir, we already know it
            if '/' in daq_tmp:
                f_tmp = path.replace(daq_dir,'') + '/' + f
            else:
                f_tmp = f

            # check if we should ignore this file
            if ignore is not None and any(ig in f_tmp for ig in ignore):
                continue

            finfo = parse(daq_tmp, f_tmp)
            if finfo is not None:
                finfo = finfo.named # convert to dict
                finfo['daq_file'] = f_tmp
                pprint(finfo)
                exit()
                daq_files.append(finfo)


if __name__=="__main__":
    main()
