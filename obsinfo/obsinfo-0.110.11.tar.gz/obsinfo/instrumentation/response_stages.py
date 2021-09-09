"""
ResponseStages and Stage classes

"""

# Standard library modules
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
import re
import logging
logger = logging.getLogger("obsinfo")

# Non-standard modules
from obspy.core.inventory.response import (PolesZerosResponseStage,
                                           FIRResponseStage,
                                           CoefficientsTypeResponseStage,
                                           ResponseListResponseStage,
                                           Response)
from obspy.core.inventory.response import Response as obspy_Response

import obspy.core.util.obspy_types as obspy_types

# Local modules
from ..obsMetadata.obsmetadata import (ObsMetadata)
from .filter import (Filter, PolesZeros, FIR, Coefficients, ResponseList,
                     Analog, Digital, AD_Conversion)


class ResponseStages():
    """
    An ordered list of objects of :class:`Stage`, representing a total response.
    
       **Attributes :**
      
    
        * stages (list of objects of :class:`Stage`)
        * obspy_stages (list of objects of different obspy classes according to the type of stage)
     
    """
    def __init__(self, attribute_list, channel_modif={}, selected_config={}, delay_correction=None):
        """
        Constructor
        
        Method can be invoked with attribute_list as a single element of class 
        Stage or as a list of them.
        
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param delay_correction: used only for datalogger, it's the delay correction of the whole instrument
        :type delay_correction: float

        """
        
        if attribute_list == None:
            msg = f'No stages found in information file'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        elif not isinstance(attribute_list, list): #Not a list, single element
            self.stages = Stage(ObsMetadata(attribute_list), 
                                 channel_modif,
                                 selected_config, 
                                 delay_correction, 
                                 0) #last argument is position in list

        else:
            self.stages = [Stage(ObsMetadata(s), 
                                 channel_modif,
                                 selected_config, 
                                 delay_correction, 
                                 i) for s, i in zip(attribute_list, range(0, len(attribute_list)))] #last argument is position in list

        self.obspy_stages = self.to_obspy()

        #delay, delay corrections and sample rates (if not present for digital stages)  will be calculated for the whole instrumentation
           
        
    def to_obspy(self):
        """
        Return list of obspy stage classes
        
        Each class will have a different obspy class
        
        :returns: list of objects of obspy classes
        
        """
        
        if not self.stages:
            return None
        
        obspy_stages = [s.to_obspy() for s in self.stages]
        
        return obspy_stages
                                   
        
    def __repr__(self):

        if self.stages != None:
            return f' Number of response stages: {len(self.stages):d}' 
        else:
            return f'Response_Stages: (empty)'
        

class Stage(object):
    """
    Stage is a discrete portion of the response of the instrument
    
       **Attributes :**
      
    
        * name (str): name of stage, if any
        * description (str): description of stage
        * input_units (str): validated in schema
        * input_units_description (str)
        * output_units (str): validated in schema
        * output_units_description (str)
        * gain (float): value of gain 
        * gain_frequency (float): frequency at which gain is measured
        * filter (object of :class:`Filter`)
        * stage_sequence_number: sequence number in total response, assigned later
        * input_sample_rate (float): input sample rate in sps
        * delay (float): delay in seconds of stage. If not present, will be calculated from offset
                       from digital stages
        * decimation_factor (float): decimation factor of stage
        * correction (float) : delay correction. Calculated from instrument delay correction
        * polarity (str, either "+" or "-"): whether stage changes polarity
        * calibration_date (str in date format): calibration date of stage
        * instrument_sensitivity (float): Not used, set to None. Sensitivity is calculated for the whole response.
    
    """
    def __init__(self, attributes_dict, channel_modif_list={}, selected_config={}, 
                 delay_correction=None, sequence_number=-1):
        """
        :param attributes_dict: attributes of component
        :type attributes_dict: dict or object of :class:`ObsMetadata`
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param delay_correction: used only for datalogger, it's the delay correction of the whole instrument
        :type delay_correction: float
        :param sequence_number: sequence number. It will first be assigned within component
                                and then for the whole response of the instrument
        :type sequence_number: float

        """
        
        if attributes_dict == None:
            return None
        
        channel_modif = self.get_selected_modifications(channel_modif_list, str(sequence_number))
        
        name = attributes_dict.get_configured_element('name', channel_modif, selected_config, '')
            
        self.name = name if name else sequence_number #stage id is either the name or a sequence number

        self.description = attributes_dict.get_configured_element('description', 
                                                            channel_modif, 
                                                            selected_config,
                                                            '')
        self.input_units = attributes_dict.get_configured_element('input_units', 
                                                            channel_modif, 
                                                            selected_config, None).get('name', None)
        
        self.output_units = attributes_dict.get_configured_element('output_units', 
                                                             channel_modif, 
                                                             selected_config, None).get('name', None)
        
        gain_dict = ObsMetadata(attributes_dict.get('gain', {}))
        if gain_dict:
            modif_gain_dict = channel_modif.get('gain', {})
            self.gain = gain_dict.get_configured_element('value', 
                                                         modif_gain_dict, 
                                                         selected_config,
                                                          1.0)             
            self.gain_frequency = gain_dict.get_configured_element('frequency', 
                                                                   modif_gain_dict, 
                                                                   selected_config, 
                                                                   0.0)
        else:
            msg = f'No gain specified in stage {self.name}'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        
        # filter cannot be changed by configuration, but it can by channel modification
        self.filter = Filter.dynamic_class_constructor(ObsMetadata(attributes_dict.get('filter', None)),
                                                       channel_modif.get('filter', None),
                                                       selected_config, 
                                                       self.name)
        if not self.filter:
            msg = f'No filter in stage {self.name}'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        
        self.stage_sequence_number = -1
        
        input_dict = input_units_description=attributes_dict.get_configured_element('input_units', 
                                                                                    channel_modif, 
                                                                                    selected_config, 
                                                                                    None)
        if input_dict:
            self.input_units_description = input_dict.get('description', None)
        output_dict = output_units_description=attributes_dict.get_configured_element('output_units', 
                                                                                      channel_modif, 
                                                                                      selected_config, 
                                                                                      None)
        if output_dict:  
            self.output_units_description = output_dict.get('description', None)
        self.input_sample_rate = attributes_dict.get_configured_element('input_sample_rate', 
                                                                  channel_modif, 
                                                                  selected_config, 
                                                                  None) 
        
        
        
        self.delay = attributes_dict.get_configured_element('delay', channel_modif, selected_config, None)
        self.decimation_factor = attributes_dict.get_configured_element('decimation_factor', 
                                                                  channel_modif, 
                                                                  selected_config,
                                                                  1)
        self.correction = delay_correction
        
        #default polarity is positive
        self.polarity = attributes_dict.get_configured_element('polarity', channel_modif, selected_config, 1)
                
        #self.calculate_delay(delay_correction)
        
        self.calibration_date = attributes_dict.get_configured_element('calibration_date', selected_config, None)
        
        self.instrument_sensitivity = None #Overall sensitivity will be calculated using obspy and stored in first stage
        
                  
    @property
    def output_sample_rate(self):
        """
        Output sample rate is not specified but calculated from 
        input sample rate and decimation factor
        """
        
        if self.input_sample_rate and self.decimation_factor:
            return self.input_sample_rate / self.decimation_factor
        else:
            return None

    def calculate_delay(self, delay_correct):
        """
        Calculates delay and delay correction
        
        Delay is a function of filter offset for digital filters if not specified in info file
        Otherwise, uses delay as passed in the arguments
        
        Also applies delay_correction in the following way:
            - If delay_correct == None, correction is not applied and self.correction values are made equal to delay values
            - Otherwise, self.correction will be 0 except for the last stage, which will be correct.value
              but is set elsewhere (in datalogger _init_). 
        
        :param delay_correct: used only for datalogger, it's the delay correction of the whole instrument
        :type delay_correct: float     
        """
        
        delay = self.delay
        offset = self.filter.offset
        input_sample_rate = self.input_sample_rate
        
        if delay == None:
            if offset:
                if not input_sample_rate:
                    #Delay is already none, leave it like that
                    msg = f'Stage delay is impossible to calculate \
                        out of filter offset with an Unspecified input sample rate in stage {self.name}. Setting to "None"'
                    logger.warning(msg)
                    warnings.warn(msg)
                else: 
                    self.delay = offset / input_sample_rate
            else:    
                self.delay = None
                       
        else:
            self.delay = delay
               
        self.correction = self.delay if delay_correct == None else 0
    
    def get_selected_modifications(self, modif_dict, key_code):
        """
        Select which channel modifications specified at station level apply to a given stage, 
        with the stage number (WITHIN an instrument component) as key code
        
        :param modif_dict: channel modifications inherited from station
        :type modif_dict: dict or object of :class:`ObsMetadata`
        :param key_code: key to the selected configuration
        :type key_code: str with special regexp format: "*" or, e.g. "[1,2,4]" or "[1-3]"
        
        """
        
        default_dict = range_dict = {}
        modif = modif_dict.get(key_code, {})
        
        overlap = False
        for k, v in modif_dict.items():
            if k[0] == "*":
                default_dict = v
            elif k[0][0] == "[":             
                if re.match(k, key_code):
                    if overlap:
                        msg = "There is an overlap in response stage modifications. Taking the first applicable pattern."
                        warnings.warn(msg)
                        logger.warning(msg)
                        break # Will only use first match to avoid conflicts
                    range_dict = v
                    overlap = True                  
                                    
        # Gather all modifications in a single dict
        # Do this in order: particular mods have priority over range specific which has
        # priority over default
        for k, v in range_dict.items():
            if k not in modif:    
               modif[k] = v  
           
        for k, v in default_dict.items():
            if k not in modif:    
               modif[k] = v
        
        return modif


    def __repr__(self):
        s = f'\n     Stage("{self.name}", "{self.description}", '
        s += f'"{self.input_units}", "{self.output_units}", '
        s += f'{self.gain}, {self.gain_frequency:g}, '
        s += f'{type(self.filter)}'
        if not self.stage_sequence_number == -1:
            s += f', stage_sequence_number="{self.stage_sequence_number}"'
        if self.input_units_description:
            s += f', input_units_description="{self.input_units_description}"'
        if self.output_units_description:
            s += f', output_units_description='
            s += f'"{self.output_units_description}"'
        if self.input_sample_rate:
            s += f', input_sample_rate={self.input_sample_rate}'
        
        s += f', decimation_factor={self.decimation_factor}'
        s += f', delay={self.delay}'
        s += f', correction={self.correction}'
        
        if self.calibration_date:
            s += f', calibration_dates={self.calibration_date}'
        s += ')'
        return s

    def to_obspy(self):
        """
        Return equivalent *obspy.core.inventory.response* classes stages:
        
        Possible stage classes: 
        
           * PolesZerosResponseStage
           * FIRResponseStage
           * CoefficientsTypeResponseStage
           * ResponseListResponseStage
           * Response
           
        :returns: object of one the above classes

        """

        filt = self.filter
        args = (self.stage_sequence_number, self.gain, self.gain_frequency,
                self.input_units, self.output_units) # Invariable position arguments for all
        
        if (isinstance(filt, PolesZeros) 
                or isinstance(filt, Analog)):
            if not filt.normalization_frequency:
                filt.normalization_frequency = self.gain_frequency
                
            if filt.type == "PolesZeros": #Only iterate if zeros and poles exist
                PZ_zeros=[obspy_types.ComplexWithUncertainties(
                    t, lower_uncertainty=0.0, upper_uncertainty=0.0)\
                    for t in filt.zeros]
                PZ_poles=[obspy_types.ComplexWithUncertainties(
                    t, lower_uncertainty=0.0, upper_uncertainty=0.0)\
                    for t in filt.poles]
            else:
                PZ_zeros = filt.zeros
                PZ_poles = filt.poles
                
            obspy_stage = PolesZerosResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=self.input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=filt.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,                #OJO: check if correction and delay should be modified
                resource_id="",
                # PolesZeros-specific
                pz_transfer_function_type=filt.transfer_function_type,
                normalization_frequency=filt.normalization_frequency,
                zeros=PZ_zeros,
                poles=PZ_poles,
                normalization_factor=filt.normalization_factor
                )
            
        elif isinstance(filt, FIR):
            
            obspy_stage = FIRResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=self.input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=filt.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                resource_id="",                
                # FIR-specific
                symmetry=filt.symmetry,
                coefficients=[obspy_types.FloatWithUncertaintiesAndUnit(
                    c / filt.coefficient_divisor) for c in filt.coefficients])
        
        elif (isinstance(filt, Coefficients)
                or isinstance(filt, Digital)
                or isinstance(filt, AD_Conversion)):                
            
            if filt.type == "Coefficients": #Only iterate if zeros and poles exist
                c_numerator=[obspy_types.FloatWithUncertaintiesAndUnit(
                    n, lower_uncertainty=0.0, upper_uncertainty=0.0)\
                    for n in filt.numerator_coefficients]
                c_denominator=[obspy_types.FloatWithUncertaintiesAndUnit(
                    n, lower_uncertainty=0.0, upper_uncertainty=0.0)\
                    for n in filt.denominator_coefficients]
            else:
                c_numerator=filt.numerator_coefficients
                c_denominator=filt.denominator_coefficients
                           
            obspy_stage = CoefficientsTypeResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=self.input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=filt.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                resource_id="",
                # CF-specific
                cf_transfer_function_type=filt.transfer_function_type,
                numerator=c_numerator,
                denominator=c_denominator
                )

        elif isinstance(filt, ResponseList):
            
            obspy_stage = ResponseListResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=self.input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=filt.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                resource_id="",
                # ResponeList-specific
                response_list_elements=filt.response_list)
            
        else:
            msg = f'Unhandled response stage type in stage #{self.stage_sequence_number}: "{filt.type}"'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        
        return obspy_stage
