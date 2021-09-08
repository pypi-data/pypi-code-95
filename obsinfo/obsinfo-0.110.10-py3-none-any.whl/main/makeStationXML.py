"""
 Main functions for obsinfo-makeStationXML
 
 Creates obsinfo objects starting with a network object in a hierarchy which 
 strongly follows the hierarchy of StationXML files.
 Then converts the objects to a StationXML file using obspy.

"""

# General library imports
import sys
import os
import re
import warnings

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
from pathlib import Path, PurePath
from json.decoder import JSONDecodeError
import logging
from logging.handlers import RotatingFileHandler

from argparse import ArgumentParser

#Third party imports
import obspy
from obspy.core.inventory import Inventory,  Station, Channel, Site
from obspy.core.inventory import Network as obspy_Network
from obspy.clients.nrl import NRL
#obsinfo imports
from ..network import (Network)
from ..obsMetadata.obsmetadata import (ObsMetadata)
from ..misc.discoveryfiles import (Datapath)
from ..print_version import main as print_version 
import obsinfo
from ..misc.const import *
from ..misc.configuration import ObsinfoConfiguration

def main():
    """
    Entry point for obsinfo-makeStationXML. 
     
     1) Setups status variables from command line arguments.
     2) Read yaml or jason file invoking read_info_file, which returns a dictionary. Optionally validates dictionary schema.
     3) Creates obsinfo objects starting from network object from the dictionary 
     4) Converts these to StationXML using obpsy libraries. 
     
    Manages all uncaught exceptions.
    """
    
    # create list of directories to search for files    
    dp = Datapath()
    args = retrieve_arguments(dp)
    logger = init_logging()
    
    if args.verbose:
        print(f'Using OBSINFO_DATAPATH: {dp.datapath_list}')
    
    logger.info(f'Using OBSINFO_DATAPATH: {dp.datapath_list}') 
   
        
    try:               
                         
        file = Path(args.input_filename).name    
       
        if args.validate:
            if args.verbose:
                print(f'Validating network file: {file}')
            logger.info(f'Validating network file: {file}')    
                
            ret = ObsMetadata().validate(args.schemapath,  str(args.input_filename), 
                                         remote=args.remote, 
                                         format="yaml", 
                                         type="network", 
                                         verbose=args.verbose, 
                                         schema_file="network", 
                                         quiet=False)
                    
        info_dict = ObsMetadata.read_info_file(args.input_filename, dp, args.remote)
        
        net_dict = info_dict.get('network', None)
        if not net_dict:
            return 
                
        if args.verbose:
            print(f'Processing network file: {file}')
        logger.info(f'Processing network file: {file}')
        
        obj = Network(ObsMetadata(net_dict), args.station)
                  
        if args.verbose:
           print(f'Network file parsed successfully for: {file}')
        logger.info(f'Network file parsed successfully for: {file}')
           
        networks=[obj.obspy_network]
        if not isinstance(obj.obspy_network, obspy_Network):
            print("Not a network object")
            logger.error("Not a network object")
            
        if not args.quiet:
           print(obj.obspy_network)
        
        logger.info(obj.obspy_network)
            
        version = os.environ.get('OBSINFO_VERSION')
        
        author = get_first_author(info_dict)
    
        inv = Inventory(
                networks,
                module=version,
                module_uri="https://gitlab.com/resif/obsinfo",
                sender=author,
                source="ObsPy")
    
        if not args.test: # Generate Stationxml file
            if not args.output:
                stem_name = Path(file).stem      # remove .yaml
                stem_name = Path(stem_name).stem #Remove .network
            
                output_filename = stem_name + ".station.xml"
            else:
                output_filename = args.output
            
            stationxml=inv.write(output_filename, format="stationxml", validate=False)
         
        if not args.quiet and not args.test:
           print(f'StationXML file created successfully: {output_filename}') 
        logger.info(f'StationXML file created successfully: {output_filename}')          
               
    except TypeError:
        print("Illegal format: fields may be missing or with wrong format in input file, or there is a programming error")
        logger.error("TypeError: Illegal format: fields may be missing or with wrong format in input file, or there is a programming error")
        if args.debug:
            raise
        
        sys.exit(EXIT_DATAERR)
    except (KeyError, IndexError):
        print("Illegal value in dictionary key or list index")
        logger.error("KeyError, IndexError: Illegal value in dictionary key or list index")
        if args.debug:
            raise
        sys.exit(EXIT_SOFTWARE)
    except ValueError:
        print("An illegal value was detected")
        logger.error("ValueError: An illegal value was detected")
        if args.debug:
            raise
        sys.exit(EXIT_DATAERR)
    except FileNotFoundError:
        if args.debug:
            raise
        print("File could not be found")
        logger.error("FileNotFoundError: File could not be found")
        sys.exit(EXIT_NOINPUT)
    except JSONDecodeError:
        print("File and/or subfiles have an illegal format. Probably indentation or missing quotes/parentheses/brackets")
        logger.error("JSONDecodeError: File and/or subfiles have an illegal format. Probably indentation or missing quotes/parentheses/brackets")
        if args.debug:
            raise 
        sys.exit(EXIT_DATAERR)
    except (IOError, OSError, LookupError):
        print("File could not be opened or read")
        logger.error("IOError, OSError, LookupError: File could not be opened or read")
        if args.debug:
            raise
        sys.exit(EXIT_UNAVAILABLE)
    except AttributeError:
        print("Programming error: an object in code had a wrong attribute")
        logger.debug("AttributeError: Programming error: an object in code had a wrong attribute")
        if args.debug:
            raise
        sys.exit(EXIT_SOFTWARE)
    except:
        print("General exception")
        logger.debug("General exception")
        if args.debug:
            raise
        sys.exit(EXIT_FAILURE)
        
    sys.exit(EXIT_SUCCESS)
    
  
def retrieve_arguments(datapath):
    
    """
    Retrieve arguments from command line. Setup several status variables and get information file name
      
    :param datapath: Object that contains the datapath to find repository files, read from .obsinforc
    :type datapath: Datapath.
    :returns: Tuple with all status variables and information file name.
    """
            
    # Parse the arguments
    parser_args = ArgumentParser(prog="obsinfo-makeStationXML")
    
    #flags
    parser_args.add_argument("-r", "--remote", action='store_true', default=False,
                             help="Assumes input filename is discovered through OBSINFO_DATAPATH environment variable. Does not affect treatment of $ref in info files",
                            )
    
    parser_args.add_argument("-l", "--validate", action='store_true', default=None,
                             help="Performs complete validation, equivalent to obsinfo-validate, before processing"
                             )
    
    parser_args.add_argument("-v", "--verbose", action='store_true', default=False,
                             help="Prints processing progression"
                            )
    
    parser_args.add_argument("-q", "--quiet", action='store_true', default=False,                    
                             help="Silences a human-readable summary of processed information file"
                            )
    
    parser_args.add_argument("-d", "--debug",  action='store_true', default=False,
                             help="Turns on exception traceback"
                            ) 
       
    parser_args.add_argument("-t", "--test",  action='store_true', default=False,
                             help="Produces no output"
                            ) 
    
    parser_args.add_argument("-V", "--version",  action="store_true", default=False,
                             help="Print the version and exit"
                            ) 
    
    parser_args.add_argument("-S", "--station",  action="store_true", default=False,
                             help="Create a StationXML file with no instrumentation"
                            ) 
    
    # optional arguments
    parser_args.add_argument("-o", "--output", default=None,
                             help="Names the output file. Default is <input stem>.station.xml"
                            )
     
    # positional arguments
    parser_args.add_argument("input_filename", type=str,  nargs=1, 
                             help="is required and must be a single value"
                            ) 
    
    args = parser_args.parse_args() 
    
    if args.version:
        print_version() 
        sys.exit(EXIT_SUCCESS) 

    # schemas must always be installed under obsinfo/data/schemas   
    args.schemapath = Path(obsinfo.__file__).parent.joinpath('data', 'schemas')
    
    if not args.input_filename:
        print("No input filename specified")
        sys.exit(EXIT_USAGE) 
        
    input_filename = args.input_filename[0]
    
    args.input_filename = str(datapath.build_datapath(input_filename) if args.remote \
                         else Path(os.getcwd()).joinpath(input_filename))
    
    return args

def init_logging():
    """
    Create or open a rotating logging file and add it to ObsinfoConfiguration
    
    :returns: object of Logger class 
    """
    
    logfile = Path.home().joinpath('.obsinfo', 'obsinfolog-makeStationXML')
    
    
    logger = logging.getLogger("obsinfo")
    
    logger.setLevel(logging.DEBUG)
    # add a rotating handler with 200K (approx) files and just two files
    handler = RotatingFileHandler(logfile, maxBytes=200000,
                                  backupCount=2)
    frmt = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(frmt)
    logger.addHandler(handler)  
    
    return logger 
        

def get_first_author(info_dict):
    """
    Get info file first author info and return it in a string.

    Used to fill the author attribute in the Inventory object of obspy.
    
    :param info_dict: The name to use.
    :type name: str.
    :param state: Current state to be in.
    :type state: bool.
    :returns:  str -- first author first name and last name and contact information
    """
    
    # Ojo, might change to parse arguments
    
    rev = info_dict.get('revision', None)
    if not rev:
        return ""
   
    authors = rev.get('authors', None)

    if authors:
        author = authors[0].get('first_name', "") + " " + authors[0].get('last_name', "") \
           + ", " + authors[0].get('institution', "") +  " Email: " + authors[0].get('email', "") + "  Phones: "
        for phn in authors[0].get('phones', ""):
            author += phn + " "
    
    return author 

    
if __name__ == '__main__':
    main()