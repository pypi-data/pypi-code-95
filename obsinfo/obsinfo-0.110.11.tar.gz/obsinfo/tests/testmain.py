import sys
import os
import re
import warnings
from pathlib import Path, PurePath

from obsinfo.tests.test import(TestObsinfo)
from obsinfo.misc.printobs import (PrintObs)
from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)


# We'll first create all the various objects. These strongly follow the
# hierarchy of StationXML files.

class TestArgs(object):
    """
    Class to test how to start executing obsinfo in different modes
    
    """        
          
    def retrieve_arguments(arguments):
        
        options_dict = {
                           "output": "o",
                           "input" : "i",
                           "verbose" : "v",
                           "print_output" : "p",
                           "test" : "t",
                           "validate" : "d",
                         }
        
        input_filename = output_filename = None
        verbose = print_output = test = validate = False
        skip_next_arg = False
        input_found = False
        
        long_option = re.compile("^[\-][\-][a-zA-Z_]+$")
        short_option = re.compile("^[\-][a-zA-Z]$")
        possible_options = re.compile("^[vptdoih]+$")
        
        option = None
        
        for arg in arguments[1:]:

            if skip_next_arg:
                skip_next_arg = False
                continue
            
            if re.match(long_option, arg):  
                option = options_dict.get(arg[2:])
            elif not arg[0] == "-":
                    if not input_found:
                        input_filename = arg
                    else:
                        print(f'Warning: found two input files, one with option "-i" and one without. Retaining the first one and discarding "{arg}"')
                    break
            else:
                option = arg[1:]
            
            if not re.match(possible_options, option):
                s = f'Unrecognized option in command line: -{option}\n'
                s += TestArgs.usage()
                raise ValueError(s)
            
            for opt in option:
        
                if opt == "o":
                    if len(option) == 1:
                        output_filename = arguments[arguments.index("-o" if "-o" in arguments else "--output")+1]
                        skip_next_arg = True
                    else:
                        warnings.warn('-o option should stand alone and be followed by a filename')
                        break
                
                elif opt == "i":
                    if len(option) == 1:
                       input_filename = arguments[arguments.index("-i" if "-i" in arguments else "--input")+1]
                       input_found = True
                       skip_next_arg = True
                    else:
                        warnings.warn('-i option should stand alone and be followed by a filename')
                        break         
                
                elif opt == "v":
                    verbose = True
                elif opt == "p":
                    print_output = True 
                elif opt == "t":
                    test = True
                elif opt == "d":
                    validate = True
                elif opt == "h": 
                    print(TestArgs.usage())
                    sys.exit()
            
        return (verbose, print_output, test, validate, input_filename, output_filename)   
    
    def usage():
        s = f'Usage: {sys.argv[0]} -vptdh  -o <filename> [-i] <filename>\n'
        s += f'Where:\n'
        s += f'      -v or --verbose: prints processing progression\n'
        s += f'      -p or --print_output: prints a human readable version of processed information file\n'
        s += f'      -t or --test: enters test mode, produces no output\n'
        s += f'      -d or --validate: validates the YAML or JSON format of the information file with no further processing\n'
        s += f'      -h or --test: prints this message\n'
        s += f'      -o or --output: names the output file. Default is station.xml\n'
        s += f'      -i or --input: names the input file. The -i may be omitted and the argument will be understood as the input file name\n'
        s += f'      -i or --input: names the input file\n'
        
        return s