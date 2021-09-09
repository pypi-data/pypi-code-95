""" 
obsinfo information file routines, contained in superclass ObsMetadata for generality
"""
# Standard library modules
import json
import pprint
from pathlib import Path, PurePath 
import sys
import re
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
from urllib.parse import urlparse
from urllib.parse import unquote
import logging
logger = logging.getLogger("obsinfo")

# Non-standard modules
import jsonschema
import jsonref
import yaml


# Local modules
from ..misc import yamlref
from ..misc.yamlref import JsonLoader
from ..misc.remoteGitLab import gitLabFile
from ..misc.discoveryfiles import Datapath

root_symbol = "#"
VALID_FORMATS = ["JSON", "YAML"]
VALID_TYPES = [
    "campaign",
    "network",
    "station",
    "instrumentation",
    "datalogger",
    "preamplifier",
    "sensor",
    "response",
    "stage",
    "filter",
]

class ObsMetadata(dict):
    
    def __init__(self, *args, **kwargs):
        """
        Constructor, simply create a dict with positional and keyword arguments
        
        :param args: dictionary of positional arguments
        :param kwars: dictionary of keyword arguments
        """
        
        super().__init__(*args, **kwargs)
        #self.convert_to_obsmetadata()
        
    def convert_to_obsmetadata(self):
        """
        Make all contained dictionaries objects of :class: `ObsMetadata`
        
        """
        
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = self.__class__(value)
                self[key].convert_to_obsmetadata()
            elif isinstance(value, list):
                for x in value:
                   if isinstance(x, dict):
                      x = self.__class__(x)
                      x.convert_to_obsmetadata()    
        
    def list_valid_types():
        """
        Returns a list of valid information file types
        
        :returns: list of valid information file types
        """
        return VALID_TYPES

   
    def validate(self, schema_datapath, filename, remote=False, format=None, type=None, verbose=False,
                 schema_file=None, quiet=False):
        """
        Validates a YAML or JSON file against schema
        
        :param schema_datapath: object to point to schema datapath
        :type schema:datapath datapath: object of :class:`Datapath`
        :param filename: name of file to validate
        :type filename: str or path-like object
        :param remote: whether to search for filename in a remote repository
        :type remote: boolean
        :param format: format of information file. Choices:  "JSON" or "YAML"
        :type format: str
        :param type: type of info file: "network", "station", "instrumentation", "datalogger", "preamplifier", "sensor", "stage", "filter"
        :type type: str
        :param verbose: Print progression of validation steps with filenames
        :type verbose: boolean
        :param schema_file: name of schema file
        :type schema_file: str
        :param quiet: Deprecated. Conserved for compatibility. Cancels verbose.
        :type quiet: boolean
         
        If type and/or format are not provided, tries to figure them out from the
        filename, which should be "*{TYPE}.{FORMAT}*
        """
    
        if quiet:
            verbose = False
    
        if not type and not schema_file:
            type = ObsMetadata.get_information_file_type(filename)
    
        msg = f"instance = {filename}"
        logger.info(msg) 
        if verbose:
            print(msg)
            
        dp = Datapath() #This creates a datapath for information files, not schemas
        
        instance = ObsMetadata.read_json_yaml_ref(filename, dp, format) if not remote \
                  else ObsMetadata.read_json_yaml_ref_datapath(filename, dp, format)
        
        base_file = (type if not schema_file else schema_file) + ".schema.json"  
        schema_file = PurePath(schema_datapath).joinpath(base_file)
        base_uri = unquote(PurePath(schema_file).as_uri())
       
        try:
            with open(schema_file, "r") as f:
                try:
                    schema = yamlref.loads(f.read(), base_uri=base_uri, jsonschema=True, 
                                           datapath=schema_datapath, recursive=True)
                    
                except json.decoder.JSONDecodeError as e:
                    msg = f"JSONDecodeError: Error loading JSON schema file: {schema_file}"
                    logger.error(msg) 
                    print(msg)
                    logger.error(str(e)) 
                    print(str(e))
                    return False
                except:
                    f"Error loading JSON schema file: {schema_file}"
                    print(msg)
                    logger.error(msg)
                    print(sys.exc_info()[1])
                    logger.error(sys.exc_info()[1])
                    return False
        except FileNotFoundError:
            msg = f'File not found: {schema_file}'
            logger.error(msg)
            raise FileNotFoundError(msg)
        except (IOError, OSError):
            msg = f'Input/Output error with file: {schema_file}'
            print(msg)
            logger.error(msg)
            raise
               
        # Lazily report all errors in the instance
        # ASSUMES SCHEMA IS DRAFT-04 (I couldn't get it to work otherwise)
    
        try:
            msg1 = f"schema =   {schema_file.name}"
            msg2 = "\tTesting schema ..."
            logger.info(msg1)
            logger.info(msg2)
            if verbose:
                print(msg1)
                print(msg2, end="")
            
             
            # Check schema first    
            jsonschema.Draft4Validator.check_schema(schema)
            
            msg1 = "OK"
            msg2 = "\tTesting instance ..."
            logger.info(msg1)
            logger.info(msg2)
            if verbose:
                print(msg1)
                print(msg2, end="")
    
            v = jsonschema.Draft4Validator(schema)
    
            if not v.is_valid(instance):
                print("")
                for error in sorted(v.iter_errors(instance), key=str):
                    print("\t\t", end="")
                    for elem in error.path:
                        msg = f"['{elem}']"
                        print(msg, end="")
                        logger.error(msg)
                    msg = f": {error.message}"
                    logger.error(msg)
                    print(msg)
                
                print("\tFAILED")
                logger.info("\tFAILED")
                return False
            else:
                if verbose:
                    print("OK")
                logger.info("OK")
                return True
        except jsonschema.ValidationError as e:
            logger.error(e.message)
            print("\t" + e.message)
            return False
    
    
    def get_information_file_format(filename):
        """
        Determines if the information file is in JSON or YAML format. 
        
         Assumes that the filename is "*.{FORMAT}*
        
        :param filename: filename to determine the type of
        :type filename: str
        :returns: format
        :raises: ValueError
        
        """
        suffix = PurePath(filename).suffix
        format = suffix[1:].upper()
        if format in VALID_FORMATS:
            return format
        msg = f"Unknown format: {format}"
        print(msg)
        logger.error(msg)
        raise ValueError(msg)
        
    def get_information_file_type(filename):
        """
        Determines the type of a file.
        
        Assumes that the filename is "*.{TYPE}.{SOMETHING}*
        
        :param filename: filename to determine the type of
        :type filename: str
        :returns: type
        :raises: ValueError
        """
        
        stem = PurePath(filename).stem
        suffix = PurePath(stem).suffix
        type = suffix[1:]
        if type in VALID_TYPES:
            return type
        msg = f"Unknown type: {type}"
        print(msg)
        logger.error(msg)
        raise ValueError(msg)
    
    
    def read_json_yaml(filename, format=None):
        """ 
        Reads a JSON or YAML file. Does NOT use jsonReference  DEPRECATED.
        
        DEPRECATED. Not being used by any obsinfo method or function. Kept for compatibility
        
        :param filename: filename 
        :type filename: str
        :param format: format type, either "YAML" or "JSON" 
        :type format: str
        :returns: dictionary of JSON or YAML parsed information files
        :raises: JSONDecodeError, any exception open raises
        """
        if not format: #validate format is legal. Otherwise program will exit
            format = ObsMetadata.get_information_file_format(filename)
    
        with open(filename, "r") as f:
            if format == "YAML":
                try:
                    element = yaml.safe_load(f)
                except:
                    msg = f"Error loading YAML file: {filename}"
                    print(msg)
                    logger.error(msg)
                    raise ValueError
            else:
                try:
                    element = json.load(f)
                except JSONDecodeError as e:
                    msg = f"JSONDecodeError: Error loading JSON file: {filename}: {str(e)}"
                    print(msg)
                    logger.error(msg)
                except:
                    msg = f"Error loading JSON file: {filename}"
                    print(msg)
                    logger.error(msg)
                    raise
    
        return element
    
    def read_json_yaml_ref_datapath(filename, datapath, format=None):
        """ 
        Reads a JSON or YAML file using jsonReference using OBSINFO_DATAPATH
        
        :param filename: filename 
        :type filename: str
        :param datapath: object to store list of directories to search info files 
        :type datapath: object of :class:`Datapath`
        :param format: format type, either "YAML" or "JSON" 
        :type format: str
        :returns: dictionary of JSON or YAML parsed information files
        :raises: JSONDecodeError, any exception open raises
        """
        
        if not format:
            format = ObsMetadata.get_information_file_format(filename)
            
        bu = unquote(filename)
         
        if gitLabFile.isRemote(bu):
            base_uri = unquote(urlparse(bu).path)
            loader = JsonLoader()
            jsonstr = loader.get_json_or_yaml(bu, base_uri=base_uri, datapath=datapath)
            return yamlref.loads(jsonstr, base_uri=base_uri, datapath=datapath)
        else:
            base_uri = Path(bu).as_uri()
            try:
                with open(unquote(filename), "r") as f:
                    return yamlref.load(f, base_uri=base_uri, datapath=datapath)
            except FileNotFoundError:
                msg = f'File not found: {filename}'
                logger.error(msg)
                raise FileNotFoundError(msg)
            except (IOError, OSError):
                msg = f'Input/Output error with file: {filename}'
                print(msg)
                logger.error(msg)
                raise
            
    def read_json_yaml_ref(filename, datapath, format=None):
        """ 
        Reads a JSON or YAML file using jsonReference
        
        Like read_json_yaml_ref, but does not look for files in OBSINFO_DATAPATH 
        But $ref within the data files without absolute or relative path will be still looked for
        in OBSINFO_DATAPATH directories
        
        :param filename: filename 
        :type filename: str
        :param datapath: object to store list of directories to search info files. Used as a dummy.
        :type datapath: object of :class:`Datapath`
        :param format: format type, either "YAML" or "JSON" 
        :type format: str
        :returns: dictionary of JSON or YAML parsed information files
        :raises: JSONDecodeError, any exception open raises
    
        
        """
        
        if not format:
            format = ObsMetadata.get_information_file_format(filename)
    
        # print(f'{filename=}, {str(datapath)=}')
        bu = unquote(filename)
        # print(f'{bu=}')
        base_uri = Path(bu).as_uri()
        
        try:       
            with open(filename, "r") as f:
                return yamlref.load(f, base_uri=base_uri, datapath=datapath)
        except FileNotFoundError:
            msg = f'File not found: {filename}'
            logger.error(msg)
            raise FileNotFoundError(msg)
        except (IOError, OSError):
            msg = f'Input/Output error with file: {filename}'
            print(msg)
            logger.error(msg)
            raise
    
    @staticmethod
    def read_info_file(filename, datapath, remote=False, format=None):
        """
        Reads an information file, remote tells 
        
        :param filename: filename 
        :type filename: str
        :param datapath: object to store list of directories to search info files 
        :type datapath: object of :class:`Datapath`
        :param remote: whether to use absolute/relative path locally or OBSINFO_DATAPATH
        :type remote: boolean
        :param format: format type, either "YAML" or "JSON" 
        :type format: str
        :returns: dictionary of JSON or YAML parsed info files, converted to an object of :class:`ObsMetadata`

        """

        dict = ObsMetadata.read_json_yaml_ref(filename, datapath, format) if not remote \
                  else ObsMetadata.read_json_yaml_ref_datapath(filename, datapath, format)
        # Create an ObsMedatada object, which is a dir with some added methods
        return ObsMetadata(dict)
                
    def _validate_script(argv=None):
        """
         Validate an obsinfo information file
    
         Validates a file named *.{TYPE}.json* or *.{TYPE}.yaml* against the 
        obsinfo schema.{TYPE}.json file.
    
         {TYPE} can be campaign, network, instrumentation, instrument_components or
        response
        
        """
        
        from argparse import ArgumentParser
    
        parser = ArgumentParser(prog="obsinfo-validate", description=__doc__)
        parser.add_argument("info_file", help="Information file")
        parser.add_argument(
            "-t", "--type", choices=VALID_TYPES, default=None,
            help="Forces information file type (overrides interpreting from filename)",
        )
        parser.add_argument(
            "-f", "--format", choices=VALID_FORMATS, default=None,
            help="Forces information file format (overrides interpreting from filename)",
        )
        parser.add_argument(
            "-s", "--schema", default=None,
            help="Schema file (overrides interpreting from filename)",
        )
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="increase output verbosity"
        )
        args = parser.parse_args()
    
        validate(args.info_file, format=args.format, type=args.type,
                schema_file=args.schema, verbose=args.verbose)
        
    
    def get_configured_element(self, key, channel_modification={}, selected_configuration={}, default=None): 
        """
        Method to substitute any element of an ObsMetadata dictionary by elements with same keyword
        in other dictionaries: selected_configuration and channel_modification.
        
        This is the heart of *obsinfo* flexibility, which permits changes in configuration or even
        in individual attributes via channel modifications.
        
        First converts any possible dictionary into an ObsMetadata object to be able to use
        this method recursively
        
        Returns the value corresponding to key in the following way:
        
        a) If key present in channel_modification, return the corresponding value
        b) Else if key present in selected_configuration, return the corresponding value
        c) Else if key present in self, return the corresponding value
        d) Else if key not present in either, return default 
        
        Thus, channel_modifications override selected_configuration which overrides self (usually
        the attributes **read** from an information file, which, if not present, are substituted by
        a default.
        
        :param key: key to retrieve the values from the respective dictionaries
        :type key: str
        :param channel_modification: modifications specified at station level
        :type channel_modification: dict or object of :class:`ObsMetadata` 
        :param selected_configuration: configuration specified at component level
        :type selected_configuration: dict or object of :class:`ObsMetadata` 
        :param default: default value if none is found
        :type default: str 
          
        """
        
        value = self.get(key, default) #If no original value, use default step (c)

        # Use selected_configuration if present, else use original_value (which may be default) (a) and (b)
        # if here is for validation only
        if isinstance(selected_configuration, (dict, ObsMetadata)):
            value = selected_configuration.get(key, value)
        # Use channel_modification if present, else use original_value (which may be default) (a) and (b)
        # Channel modifications override selected configurations which override self which overrides default
        # but ONLY at the lowest (leaf) level, so we check whethere the value is a dictionary. If so, it won't be
        # substituted. This does not happen with configurations as they are complete substitutions of things such as
        # response stages or sample rates    
        if isinstance(channel_modification, (dict, ObsMetadata)):
            val = channel_modification.get(key, value)
            # Do not assign value if this is a dictionary, so it's not a leaf in the hierarchy
            if not isinstance(val, (dict, ObsMetadata)):
               value = val 

        if isinstance(value, dict): #Convert to ObsMetadata any dictionaries
            value = ObsMetadata(value)
            
        return value   
    
    def validate_dates(dates):
        """
        Tries to interpret as many date formats as possible, converting them to a standard format
        
        :param dates: list of dates
        :type dates: list of strings
        :returns: list of formatted dates as strings
        """
        
        if dates == None or not isinstance(dates, list):
            return []
        
        return [ObsMetadata.validate_date(dt) for dt in dates]
       
    def validate_date(date):
        """
        Reformats an individual date
        
        Uses regular expressions to match known dates, either in UTC date format, in 
        UTC date and time format or in regular dd-mm-yyyy format. If only two digits of year
        specified, assumes 21st century. The separator can be both "/" or "-"
        
        :param date: a date in a given format
        :type dates: str
        :returns: a reformatted date as string or None if no value
        :raises: ValueError
        """
        
        if date == None or date == int(0): #This is sometimes the default, the epoch date, 1/1/1970
            return None
         
        regexp_date_UTC = re.compile("^[0-9]{4}[\-\/][0-1]{0,1}[0-9][\-\/][0-3]{0,1}[0-9]")
        regexp_date_and_time_UTC = re.compile("^[0-9]{4}[\-\/][0-1]{0,1}[0-9][\-\/][0-3]{0,1}[0-9]T[0-2][0-9]:[0-6][0-9]:{0,1}[0-6]{0,1}[0-9]{0,1}Z{0,1}")
        if re.match(regexp_date_UTC, date) or re.match(regexp_date_and_time_UTC, date): # Year starts string, everything OK
            return date
        else: #Assume it's a regular date
            warnings.warn(f'Date {date} is not UTC format, assuming regular dd/mm/yyyy format')
            regexp_date_normal = re.compile("[\-\/]")
            date_elements = re.split(regexp_date_normal, date)
            if len(date_elements) != 3:
                raise ValueError("Unrecognizable date, must either be UTC or dd/mm/yyyy or dd/mm/yy. Dashes can be used as separators")
            if len(date_elements[2]) == 2:
                date_elements[2] = "20" + date_elements[2] # Assume 21st century
                warnings.warn(f'Date {date} is two digits, assuming 21st century')
    
            return date_elements [2] + "-" + date_elements [1] + "-" + date_elements [0]
            
            