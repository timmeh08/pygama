#!/usr/bin/env python3.7
import sys, os, io
import json
import argparse
import numpy as np
import pandas as pd
from pprint import pprint
from pygama import DataSet
import pygama.utils as pu

def main(argv):
    """
    Uses pygama's amazing DataSet class to process runs for different
    data sets, with arbitrary configuration options defined in a JSON file.
    C. Wiseman, 2019/04/09
    Modified for HADES data
    A.Zschocke
    """
    run_db, cal_db = './runDB_example.json', './calDB.json'
    # -- parse args --
    par = argparse.ArgumentParser(description="test data processing suite")
    arg, st, sf = par.add_argument, "store_true", "store_false"
    arg("-ds", nargs='*', action="store", help="load runs for a DS")
    arg("-r", "--run", nargs=1, help="load a single run")
    arg("-t0", "--tier0", action=st, help="run ProcessTier0 on list")
    arg("-t1", "--tier1", action=st, help="run ProcessTier1 on list")
    arg("-t", "--test", action=st, help="test mode, don't run")
    arg("-n", "--nevt", nargs='?', default=np.inf, help="limit max num events")
    arg("-i", "--ioff", nargs='?', default=0, help="start at index [i]")
    arg("-v", "--verbose", action=st, help="set verbose output")
    arg("-o", "--ovr", action=st, help="overwrite existing files")
    arg("-m", "--nomp", action=sf, help="don't use multiprocessing")
    arg("-s", "--sub", nargs=1, help="number of subfiles")
    args = vars(par.parse_args())

    if args["sub"]:
        sub = int(args["sub"][0])

    if args["ds"]:
        ds_lo = int(args["ds"][0])
        try:
          ds_hi = int(args["ds"][1])
        except:
          ds_hi = None
        ds = DataSet(ds_lo, ds_hi, sub=sub, md=run_db, cal=cal_db, v=args["verbose"])

    if args["run"]:
      ds = DataSet(run=int(args["run"][0]), md=run_db, cal=cal_db,
                   v=args["verbose"])

    # -- start processing --
    if args["tier0"] and args["sub"]:
      sub = int(args["sub"][0])
      tier0(ds,sub, args["ovr"], args["nevt"], args["verbose"], args["test"])

    if args["tier1"]:
      tier1(ds, sub,args["ovr"], args["nevt"], args["ioff"], args["nomp"], args["verbose"],
            args["test"])



def tier0(ds,sub,overwrite=False, nevt=np.inf, v=False, test=False):
    """
    Run ProcessTier0 on a set of runs.
    [raw file] ---> [t1_run{}.h5] (tier 1 file: basic info & waveforms)
    """
    from pygama.io.daq_to_raw import daq_to_raw

    for run in ds.runs:
      t0_file = ds.paths[run]["t0_path"]
      t1_file = ds.paths[run]["t1_path"]
      if t1_file is not None and overwrite is False:
        continue
      print("In/Out files:",t0_file,t1_file)

      conf = ds.paths[run]["build_opt"]
      opts = ds.config["build_options"][conf]["tier0_options"]

      if test:
        print("test mode (dry run), processing Tier 0 file:", t0_file)
        continue

      if nevt != np.inf:
        nevt = int(nevt)



    daq_to_raw(
                   t0_file,
                   run,
                   verbose=v,
                   output_dir=ds.tier1_dir,
                   overwrite=overwrite,
                   n_max=nevt,
                   config=ds.config)

def tier1(ds,
          sub,
          overwrite=False,
          nevt=None,
          ioff=None,
          multiproc=None,
          verbose=False,
          test=False):
    """
    Run ProcessTier1 on a set of runs.
    [t1_run{}.h5] ---> [t2_run{}.h5]  (tier 2 file: DSP results, no waveforms)
    Can declare the processor list via:
    - json configuration file (recommended)
    - Intercom(default_list=True)
    - manually add with Intercom::add
    """
    from pygama.dsp.base import Intercom
    from pygama.io.tier1 import ProcessTier1

    for run in ds.runs:

        t1_file = ds.paths[run]["t1_path"]
        t2_file = ds.paths[run]["t2_path"]
        if t2_file is not None and overwrite is False:
            continue

        print("In/Out",t1_file,t2_file)
        if test:
            print("test mode (dry run), processing Tier 1 file:", t1_file)
            continue

        conf = ds.paths[run]["build_opt"]
        proc_list = ds.runDB["build_options"][conf]["tier1_options"]
        proc = Intercom(proc_list)

        ProcessTier1(
            t1_file,
            proc,
            ftype=ds.ftype,
            output_dir=ds.tier2_dir,
            overwrite=overwrite,
            verbose=verbose,
            multiprocess=multiproc,
            nevt=nevt,
            ioff=ioff,
            chunk=ds.runDB["chunksize"])


if __name__ == "__main__":
    main(sys.argv[1:])
