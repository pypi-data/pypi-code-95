"""
Network :class:

"""
# Standard library modules
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
import logging
logger = logging.getLogger("obsinfo")

# Non-standard modules
from obspy.core.inventory.network import Network as obspy_Network
import obspy.core.util.obspy_types as obspy_types
from obspy.core.inventory.util import (Person, Comment, PhoneNumber)
from obspy.core.inventory.util import Operator as obspy_Operator
from obspy.core.utcdatetime import UTCDateTime
# obsinfo modules
from ..obsMetadata.obsmetadata import (ObsMetadata)
from ..network.station import (Station, Location)
from ..instrumentation.instrumentation import (Operator)


class Network(object):
    """
    Network obsinfo: Equivalent to obspy/StationXML Network
    
    Methods convert info files to an instance of this class and convert the object to an
    `obspy` object.
    
      **Attributes:**
     
        * campaign_ref (str)
        * fdsn_code (str)
        * fdsn_name (str)
        * start_date (str with date format)
        * end_date (str with date format)
        * description  (str)
        * restricted_status (str)
        * operator (object of :class:`Operator`) 
        * stations (list of objects of :class:`Station`) 
        * comments (list of str)
        * extras (list of str)
        * obspy_network (object of class Network from obspy.core.inventory.network) - Equivalent attributes to above attributes 
    
    """
    
    def __init__(self, attributes_dict=None, station_only=False):
        """
        Constructor
        
        :param attributes_dict: dictionary from network info file with YAML or JSON attributes
        :type attributes_dict: dict or object of :class:`ObsMetadata`
        :param station_only: Instructs class Station to create object with no instrumentation
        :type station_only: boolean
        :raises: TypeError
        """
        
        if not attributes_dict:
            msg = 'No network attributes'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        
        self.campaign_ref = attributes_dict.get("campaing_ref_name", None)
        network_info = attributes_dict.get("network_info", None)
        
        if network_info:
            self.fdsn_code = network_info.get("code", None)
            self.fdsn_name = network_info.get("name", None)        
            self.start_date = network_info.get("start_date", 0)
            self.end_date = network_info.get("end_date", 0)
            self.description = network_info.get("description", None)
        
        self.restricted_status = attributes_dict.get("restricted_status", None)
        
        self.operator = Operator(attributes_dict.get("operator", None))  
        
        stations = attributes_dict.get("stations", None)              
        self.stations = [Station(k, v, station_only) for k, v in stations.items()]
        
        self.comments = attributes_dict.get("comments", [])
        self.extras = [str(k) + ": " + str(v) for k, v in (attributes_dict.get('extras', {})).items()]
        self.convert_notes_and_extras_to_obspy() 
        
        self.obspy_network = self.to_obspy()     
          

    def __repr__(self):
        s = f'Network(Campaign: {self.campaign_ref}, FDSN Code: {self.fdsn_code}, FDSN Name: {self.fdsn_code}, '
        s += f'Start date: {self.start_date}, End date: {self.end_date}, Description: {self.description}, '
        s += f'{len(self.stations)} stations)'

        return s
    
    
    def to_obspy(self):
        """
         Convert network object to obspy object
         
         :returns: object of ;class: Network from *obspy.core.inventory.network* which correspondes to object of class Network. 
                   in *obsinfo*
        """
          
        if self.operator:
            
            mails = [self.operator.email] if self.operator.email else []
            phones = [PhoneNumber(self.operator.area_code, 
                                  self.operator.phone_number,
                                  self.operator.country_code)] if self.operator.phone_number else []
            names = [self.operator.contact] if self.operator.contact else []
            agencies=[self.operator.reference_name] if self.operator.reference_name else []
            person = Person(names=names, 
                            agencies=agencies, 
                            emails=mails, 
                            phones=phones)
                   
            operator = obspy_Operator(
                agency=self.operator.full_name,  
                contacts=[person], 
                website=self.operator.website)
        else:
            operator = None
                      
        stations_number = len(self.stations)
        start_date = UTCDateTime(self.start_date) if self.start_date else None
        end_date = UTCDateTime(self.end_date) if self.end_date else None
        comments = [Comment(s) for s in self.comments]
         
        self.obspy_network = obspy_Network(code=self.fdsn_code, 
                                     stations=  [st.obspy_station for st in self.stations], 
                                     total_number_of_stations=stations_number, 
                                     selected_number_of_stations=stations_number, 
                                     description=self.fdsn_name + " - " + self.description, 
                                     comments=comments,
                                     start_date=start_date, 
                                     end_date=end_date, 
                                     restricted_status=self.restricted_status, 
                                     alternate_code=None, 
                                     historical_code=None, 
                                     data_availability=None, 
                                     identifiers=None, 
                                     operators=[operator], 
                                     source_id=None)
        
        for st in self.stations:  #complete stations
            st.operators = [operator]
            
        return self.obspy_network
    
    
    def convert_notes_and_extras_to_obspy(self):
        """
        Convert info file notes and extras to XML comments
        """
        
        if self.extras:
            self.comments += ['EXTRA ATTRIBUTES (for documentation only): '] + self.extras
    
    
    
