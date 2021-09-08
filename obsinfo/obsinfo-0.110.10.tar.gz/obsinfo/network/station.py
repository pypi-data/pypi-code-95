"""
Station and Processing classes

"""

# Standard library modules
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
import logging
logger = logging.getLogger("obsinfo")

# Non-standard modules
from obspy.core.inventory.station import Station as obspy_Station

import obspy.core.util.obspy_types as obspy_types
from obspy.core.inventory.util import  (Latitude, Longitude, Site, Comment)
from obspy.core.utcdatetime import UTCDateTime
from obspy.taup.seismic_phase import self_tokenizer
# obsinfo modules
from ..instrumentation.instrumentation import (Instrumentation, Location)
from ..obsMetadata.obsmetadata import (ObsMetadata)

class Station(object):
    """
    Station. Equivalent to obspy/StationXML Station
    
     Methods convert info files to an instance of this class and convert the object to an
     `obspy` object.
    
      **Attributes:**
     
    
        * label
        * site (str)
        * start_date (str with date format): station start date
        * end_date (str with date format): station end date
        * location_code (str)
        * restricted_status (str): status of station
        * locations (list of objects of :class:`Location`)
        * location (object of :class:`Location`) default location code of channels, corresònding to `location_code`
        * instrumentation (object or list of objects of :class:`Instrumentation`) 
        * processing (list of objects of :class:`Processing`) : attributes for clock correction processing
        * comments (list of str)
        * extras (list of str)
        * obspy_station (object of class Station from obspy.core.inventory.station) - Equivalent attributes to above attributes 
    
     
    """
    
    def __init__(self, label, attributes_dict, station_only=False):
        """
        Constructor

        :param attributes_dict: dictionary from station or network info file with YAML or JSON attributes  
        :type attributes_dict: dict or object of :class:`ObsMetadata`
        :param station_only: Creates object with no instrumentation
        :type station_only: boolean
        :raises: TypeError
        
        """
         
        if not attributes_dict:
            msg = 'No station attributes'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        
        self.label = label
        
        self.site = attributes_dict.get("site", None)
        
        start_date = ObsMetadata.validate_date(attributes_dict.get("start_date", None))
        self.start_date = UTCDateTime(start_date) if start_date else None
        end_date = ObsMetadata.validate_date(attributes_dict.get("end_date", None))
        self.end_date = UTCDateTime(end_date) if end_date else None
        
        self.location_code = attributes_dict.get("location_code", None)
        
        self.restricted_status = attributes_dict.get("restricted_status", 'unknown')
        
        self.locations = {c: Location(v) for c, v in \
                          attributes_dict.get('locations', None).items()}
        self.location = Location.get_location_from_code(self.locations, self.location_code, "station", self.label)
      
        instr_list = attributes_dict.get('instrumentations', None)
        if instr_list and isinstance(instr_list, list):
            channel_mods = attributes_dict.get('channel_modifications', {})     
            self.instrumentation = [Instrumentation(inst, self.locations, start_date, end_date, channel_mods) 
                                    for inst in instr_list]
        else:
            instr_dict = attributes_dict.get('instrumentation', None)
            channel_mods = attributes_dict.get('channel_modifications', {})

            if instr_dict:
                self.instrumentation = Instrumentation(instr_dict, self.locations, start_date, end_date, channel_mods) 
            elif station_only:
                self.instrumentation = None # Will create a StationXML file with no instrumentation w/o raising an exception 
            else:
                msg = f'No instrumentation in station {self.site}'
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)
        
        #Locations, start_date and end_date are used to creat obspy Channel
              
        self.comments = attributes_dict.get("commnents", [])
        self.extras = [str(k) + ": " + str(v) for k, v in (attributes_dict.get('extras', {})).items()]
        self.processing = Processing(attributes_dict.get('processing', None))
        
        self.convert_comments_in_obspy() 

        self.obspy_station = self.to_obspy()
        
        
        

    def __repr__(self):
        s = f'\nStation(Label={self.label}, Site={self.site}, Start Date={self.start_date}, End Date={self.end_date}, '
        s += f'Location Code={self.location_code}, '
        s += f'{len(self.locations)} Locations, '
        if self.processing:
            s += f'processing-steps: {self.processing.processing_list}'
        #if not self.restricted_stations == "unknown":
        #    s += f', {self.restricted_status}'
        s += ')'
        return s


    def to_obspy(self):
        """
        Convert station object to obspy object
         
        :returns: object of class Station from *obspy.core.inventory.station* which corresponds to object of :class:`Station`. 
                   in *obsinfo*
        """

        
        latitude, longitude = Location.get_obspy_latitude_and_longitude(self.location) 
        
        start_date = UTCDateTime(self.start_date) if self.start_date else None
        end_date = UTCDateTime(self.end_date) if self.end_date else None
        site = Site(name=self.site, description=None, town=None, county=None, region=None, country=None)
        comments = [Comment(s) for s in self.comments]
        
        if self.instrumentation:
            channels_number = len(self.instrumentation.channels)
            chnl_list = [ch.obspy_channel for ch in self.instrumentation.channels]
            equip_list = [self.instrumentation.equipment]
        else:
            channels_number = 0
            chnl_list = []
            equip_list = []
                   
        obspy_station = obspy_Station( code = self.label, 
                                       latitude = latitude, 
                                       longitude = longitude, 
                                       elevation = self.location.elevation,
                                       channels= chnl_list,
                                       site=site, 
                                       vault=self.location.vault, 
                                       geology=self.location.geology, 
                                       equipments=equip_list, 
                                       operators=None,  #Will be assigned in class Network, where it is specified.
                                       creation_date=start_date, 
                                       termination_date=end_date, 
                                       total_number_of_channels=channels_number, 
                                       selected_number_of_channels=channels_number, 
                                       description=None, 
                                       comments=comments,
                                       start_date=start_date, 
                                       end_date= end_date, 
                                       restricted_status=self.restricted_status, 
                                       alternate_code=None, 
                                       historical_code=None, 
                                       data_availability=None, 
                                       identifiers=None, 
                                       water_level=None, 
                                       source_id=None)
            
        return obspy_station
    
    def convert_comments_in_obspy(self):
        """
        Convert info file notes and extras to XML comments
        """
     
        if self.extras:
            self.comments.append('EXTRA ATTRIBUTES (for documentation only):')
            self.comments = self.comments + self.extras
        if self.processing.processing_list:
            self.comments.append(self.processing.processing_list)
            

class Processing(object):
    """
    Processing. No equivalente class in obspy/StationXML

    Saves a list of Processing steps as strings
    For now, it just stores the list. It will be converted to comments for StationXML
    
      **Attributes:**
     
    
        * processing_list (dict): list of processing steps with attributes, either linear_drift or leapsecond 
    
    """
    
    def __init__(self, attributes):
        """
        Constructor
        
        :param attributes: list of processing steps with attributes
        :type list: list of either linear_drift or leapsecond dictionaries
        
        """
        
        self.processing_list = []
        
        if not attributes:
            return
                
        # make it a list for standard processing if user forgot the dash
        if not isinstance(attributes, list):
            attributes = [attributes]
        
        for attr in attributes:
            linear_drift_dict = attr.get("clock_correct_linear_drift", None)
            leapsecond_dict = attr.get("clock_correct_leapsecond", None)
            linear_drift = leapsecond = ""
            
            if linear_drift_dict:
                linear_drift = "clock correction linear_drift: ["
                linear_drift += "time_base: " + attr.get("time_base", "None")
                linear_drift += ", reference: " + attr.get("reference", "None")
                linear_drift += ", start_sync_reference: " + attr.get("start_sync_reference", "None")
                linear_drift += ", start_sync_instrument: " + attr.get("start_sync_instrument", "None")
                linear_drift += ", end_sync_reference: " + attr.get("end_sync_reference", "None")
                linear_drift += ", end_sync_instrument: " + attr.get("end_sync_instrument", "None")
                linear_drift += "]"
                self.processing_list.append(linear_drift)
                
            elif leapsecond_dict:  
                leapsecond = "clock correction leap second: ["              
                leapsecond += "time: " + attr.get("time", "None")
                leapsecond += ", type: " + attr.get("type", "None")
                leapsecond += ", description: " + attr.get("description", "None")
                leapsecond += ", corrected_in_end_sync: " + attr.get("corrected_in_end_sync", "None")
                leapsecond += ", corrected_in_data: " + attr.get("corrected_in_data", "None")
                leapsecond += "]"
                self.processing_list.append(leapsecond) 
            

    def __repr__(self):
        s = f'Processing({self.processing_list})'
        return s
