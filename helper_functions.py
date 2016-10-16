#!usr/bin/env python
import os
import numpy as np
import itertools as it
import contextlib
import untangle

""" Some helper functions. """

def common_path(process, energy):
    return '/'.join([process.name, process.decay_channel, str(energy)])
    
def mg5_process_dir(process, energy, index):
    return '/'.join(['mg5_processes', process.process_type+'s', common_path(process, energy), str(index)])

def convert_SAF_to_XML(filename):
    """ Converts a SAF file to XML """

    def convert_to_XML_line(line):
        """ Converts a SAF  line to XML """
        line = line.replace(' < ', ' &lt; ')
        line = line.replace(' > ', ' &gt; ')
        if line.startswith('#'):
            line = '<!-- '+line.rstrip()+' -->\n'
        return line

    with open(filename, 'r') as f:
        result = [convert_to_XML_line(line) for line in f]
    
    xml_filename = filename.split('.')[0]+'.xml'

    with open(xml_filename, 'w') as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<root>\n')
        for line in result:
            f.write(line)
        f.write('</root>\n')

def get_SAF_objects(filename):
    """ Get SAF objects from a file. """
    convert_SAF_to_XML(filename+'.saf')
    xml_filepath = filename+'.xml'
    return (untangle.parse(xml_filepath)).root

def modify_file(filepath, line_modification_function):
    """ Modify a file in place.

    Parameters
    ----------

    filepath: str
        Path to the file to be modified.
    line_modification_function: func
        The line modification function. Takes one parameter, the line, and
        returns either the original line or a modified version of it.
    """

    with open(filepath, 'r') as f:
        lines = [line_modification_function(line) for line in f.readlines()]
    with open(filepath, 'w') as f: [f.write(line) for line in lines]

def change_directory(destination_directory):
    """ A context manager to handle temporary directory changes """
    cwd = os.getcwd()
    os.chdir(destination_directory)
    try: yield
    except: pass
    finally: os.chdir(cwd)

cd = contextlib.contextmanager(change_directory)
