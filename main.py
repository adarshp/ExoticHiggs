#!/usr/bin/env python
import ExoticHiggs
import myProcesses

def main():   
    for process in myProcesses.A_HZ_bbll_14_TeV_collection[0:2]:
        process.create_directory()
        process.generate_events()

if __name__ == '__main__':
    main()
    
