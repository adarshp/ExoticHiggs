#!/usr/bin/env python
import ExoticHiggs
import myProcesses
from tqdm import tqdm

def main():   
    allProcesses = myProcesses.tt_bbll_14_TeV_collection
    for process in tqdm(allProcesses, dynamic_ncols = True, 
            desc = "Creating MG5 process directories, submitting event generation jobs"):
        process.create_directory()
        process.generate_events(nruns = 5, nevents = 50000)

if __name__ == '__main__':
    main()
    
