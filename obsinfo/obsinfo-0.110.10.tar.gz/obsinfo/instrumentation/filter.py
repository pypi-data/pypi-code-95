"""
Filter class and subclasses

"""
# Standard library modules
import math as m
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
import logging
logger = logging.getLogger("obsinfo")

from ..misc.configuration import ObsinfoConfiguration

from scipy._lib.doccer import extend_notes_in_docstring

# Non-standard modules
# import obspy.core.inventory.response as obspy_response


class Filter(object):
    """
    Filter is superclass of all filter classes
    
       **Attributes :**
      
    
        * type (str): filter type
        * offset (int): offset is samples to skip at the beggining of a signal in digital filters 
                
    """
    
    def __init__(self, type="PolesZeros", offset=0):
        """
        Constructor
            
        :param type: filter type
        :type type: str, one of a list of choices
        :param offset: offset is samples to skip at the beggining of a signal in digital filters 
        :type offset: int
        
        """
        self.type = type
        self.offset = offset
        
    @staticmethod
    def dynamic_class_constructor(attributes_dict, channel_modif={}, 
                                  selected_config={}, stage_id="-1"):
        """
        Creates an appropriate Filter subclass from an attributes_dict
        
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param stage_id: stage_name if it exists
        :type stage_id: str
        :returns: object of the adequate filter subclass
        :raises: TypeError if filter type is not a valid option

        """
        
        if attributes_dict == None:
            msg = "No attributes in filter"
            logger.error(msg)
            raise TypeError(msg)
        
        if "type" not in attributes_dict:
            msg = 'No "type" specified for filter in stage #{stage_id}'
            logger.error(msg)
            raise TypeError(msg)
        else:
            filter_type = attributes_dict.get_configured_element('type', 
                                                           channel_modif, 
                                                           selected_config, 
                                                           None)
            if filter_type == 'PolesZeros':
                obj = PolesZeros.dynamic_class_constructor(filter_type, attributes_dict, 
                                                           channel_modif, selected_config, stage_id)
            elif filter_type == 'FIR':
                obj = FIR.dynamic_class_constructor(filter_type, attributes_dict, 
                                                    channel_modif, selected_config, stage_id)
            elif filter_type == 'Coefficients':
                obj = Coefficients.dynamic_class_constructor(filter_type, attributes_dict, 
                                                             channel_modif, selected_config, stage_id)
            elif filter_type == 'ResponseList':
                obj = ResponseList.dynamic_class_constructor(filter_type, attributes_dict, 
                                                             channel_modif, selected_config, stage_id)
            elif filter_type == 'ADConversion':
                obj = AD_Conversion.dynamic_class_constructor(filter_type, attributes_dict, 
                                                              channel_modif, selected_config, stage_id)
            elif filter_type == 'Analog':
                obj = Analog.dynamic_class_constructor(filter_type, attributes_dict, 
                                                       channel_modif, selected_config, stage_id)
            elif filter_type == 'Digital':
                obj = Digital.dynamic_class_constructor(filter_type, attributes_dict, 
                                                        channel_modif, selected_config, stage_id)
            else:
                msg = f'Unknown Filter type: "{filter_type}" in stage #{stage_id}'
                logger.error(msg)
                raise TypeError(msg)
                
        return obj
    
        
class PolesZeros(Filter):
    """
    PolesZeros filter 
    
       **Attributes :**
     
    
        * transfer_function_type (str): one of  'LAPLACE (RADIANS/SECOND)','LAPLACE (HERTZ)','D
        * poles (list of complex numbers)
        * zeros (list of complex numbers)
        * normalization_frequency (float)
        * normalization_factor (float)
           
    """
    
    def __init__(self, filter_type, transfer_function_type='LAPLACE (RADIANS/SECOND)', 
                 poles=[], zeros=[],
                 normalization_frequency=1., 
                 normalization_factor=None,
                 offset=0,
                 stage_id=-1):
        """
        Constructor
        
        :param filter_type 
        :type filter_type: str
        :param transfer_function_type:
        :type transfer_function_type: str, one of 'LAPLACE (RADIANS/SECOND)','LAPLACE (HERTZ)','DIGITAL (Z-TRANSFORM)' 
        :param poles:
        :type poles: list of complex numbers specified as [a, b] 
        :param zeros:
        :type zeros: list of complex numbers specified as [a, b] 
        :param normalization_frequency:
        :type normalization_frequency: float
        :param normalization_factor:
        :type normalization_factor: float
        :param offset:
        :type offset: int
        :param stage_id: id of corresponding stage. Used for reporting only
        :type stage_id:
        
        """
        
        # poles and zeros should be lists of complex numbers
        if transfer_function_type not in ['LAPLACE (RADIANS/SECOND)','LAPLACE (HERTZ)','DIGITAL (Z-TRANSFORM)']:
            msg = f'Illegal transfer_function_type in PolesZeros: "{transfer_function_type}" in stage #{stage_id}'
            logger.error(msg)
            raise TypeError(msg)
            
        self.transfer_function_type = transfer_function_type
        self.poles = poles
        self.zeros = zeros
        
        self.normalization_frequency = normalization_frequency
        if normalization_frequency and normalization_factor:
            self.normalization_factor = normalization_factor
        elif filter_type != 'Analog':     #norm frequency doesn't make sense in analog      
            self.normalization_factor = self.calc_normalization_factor(stage_id)
        else:
            self.normalization_factor = 1.0

        super().__init__(filter_type, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict, channel_modif={}, 
                                  selected_config={}, stage_id=-1):
        """
        Create PolesZeros instance from an attributes_dict
        
        :param filter_type: type of filter, necessarily 'PolesZeros'
        :type filter_type: str
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param stage_id: id of corresponding stage. Used for reporting only
        :type stage_id: int
        :returns: object of :class:`PolesZeros`
        
        """
        obj = cls(filter_type,
                attributes_dict.get_configured_element('transfer_function_type', 
                                                  channel_modif, 
                                                  selected_config, 
                                                  'LAPLACE (RADIANS/SECOND)'),
                [(float(x[0]) + 1j*float(x[1])) for x in attributes_dict.get_configured_element('poles',
                                                         channel_modif, 
                                                         selected_config, 
                                                         [])],
                [(float(x[0]) + 1j*float(x[1])) for x in attributes_dict.get_configured_element('zeros',
                                                         channel_modif, 
                                                         selected_config,
                                                         [])],
                attributes_dict.get_configured_element('normalization_frequency', 
                                                 channel_modif, 
                                                 selected_config, 
                                                 1.),
                attributes_dict.get_configured_element('normalization_factor', 
                                                 channel_modif, 
                                                 selected_config, 
                                                 None),
                attributes_dict.get_configured_element('offset', 
                                                 channel_modif, 
                                                 selected_config,
                                                 0),
                stage_id
              )
        return obj

    def __repr__(self):
    
        s = f'          PolesZeros(Poles={self.poles}, Zeros={self.zeros}, '
        s += f'Normalization Frequency={self.normalization_frequency:g}, '
        s += f'Normalization Factor={self.normalization_factor:g})'
        return s

    def calc_normalization_factor(self, stage_id=-1, debug=False):
        """
        Calculate the normalization factor for a given set of poles-zeros

        he norm factor A0 is calculated such that
        
        :: code-block::

                                  sequence_product_over_n(s - zero_n)

                       A0 * abs(—--------------------------------------) == 1

                                  sequence_product_over_m(s - pole_m)

            for s_f=i*2pi*f if the transfer function is Laplace in radians

                    i*f if the transfer function is Laplace in Hertz

        
        No calculation for digital z-transform
        
        :returns: normalization factor as a float or None if not Laplace 
        
        """
        
        if not self.normalization_frequency:
            msg = f'No normalization frequency for PZ filter in stage #{stage_id}'
            logger.error(msg)
            raise ValueError(msg)

        A0 = 1.0 + (1j * 0.0)
        if self.transfer_function_type == "LAPLACE (HERTZ)":
            s = 1j * self.normalization_frequency
        elif self.transfer_function_type == "LAPLACE (RADIANS/SECOND)":
            s = 1j * 2 * m.pi * self.normalization_frequency
        else:
            msg = "Don't know how to calculate normalization factor \
for z-transform poles and zeros!"
            warnings.warn(msg) 
            logger.warning(msg)
            return None
        
        for p in self.poles:
            A0 *= (s - p)
        for z in self.zeros:
            A0 /= (s - z)

        if debug:
            msg=f"poles={self.poles}, zeros={self.zeros}, s={s}, A0={A0}"
            print(msg)
            logger.debug(msg)

        A0 = abs(A0)
        return A0


class FIR(Filter):
    """
    FIR Filter 
    
       **Attributes :**
     
    
        * symmetry (str): filter symmetry, one of "EVEN", "ODD", "NONE"
        * coefficients (list of floats)
        * coefficient_divisor (float)
        
    """
    
    def __init__(self, filter_type, symmetry, 
                 coefficients, coefficient_divisor, offset=0, stage_id=-1):

        """
        Constructor
        
        :param filter_type: type of filter, necessarily 'FIR'
        :type filter_type: str
        :param symmetry: filter symmetry, one of "EVEN", "ODD", "NONE"
        :type symmetry: str
        :param coefficients:
        :type coefficients: list of floats
        :param coefficient_divisor:
        :type coefficient_divisor: float
        :param offset:
        :type offset: int
        :param stage_id: id of corresponding stage. Used for reporting only
        :type stage_id: int
        
        """        
        self.symmetry = symmetry
        if symmetry not in ['ODD', 'EVEN', 'NONE']:
            msg = f'Illegal FIR symmetry: "{symmetry} in stage #{stage_id}"'
            logger.error(msg)
            raise TypeError()
        
        #Validate coefficients
        sum_coeff = 0
        coeff_cnt = 0
        for coeff in coefficients:
            sum_coeff += coeff
            coeff_cnt += 1
        
        coeff = sum_coeff / coefficient_divisor
        coeff = round(coeff, 2) #check up to two decimal places  
        if coeff != 1 and coeff != 0: #the last conditional means there is at least one coeff
            msg = f'Coefficient sum "{coeff}" not equal to one, num. coefficient: "{coeff_cnt}" in stage #{stage_id}'
            warnings.warn(msg)
            logger.warning(msg) 
            
        self.coefficients = coefficients
        self.coefficient_divisor = coefficient_divisor
        
        super().__init__(filter_type, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict, channel_modif={}, 
                                  selected_config={}, stage_id=-1):
        """
        Create FIR instance from an attributes_dict
        
        :param filter_type: type of filter, necessarily 'FIR'
        :type filter_type: str
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param stage_id: used only for datalogger, it's the delay correction of the whole instrument
        :type stage_id: str
        :returns: object of :class:`FIR`
        
        """
        
        offset = attributes_dict.get_configured_element('offset', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   0)
        if not offset:
            msg = f'No offset in FIR filter'
            logger.error(msg)
            raise TypeError(msg)
        
        obj = cls(filter_type,
                  attributes_dict.get_configured_element('symmetry', 
                                                   channel_modif, 
                                                   selected_config,
                                                   None), #Default will cause an error in init
                  attributes_dict.get_configured_element('coefficients', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   []),
                  attributes_dict.get_configured_element('coefficient_divisor', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   1.),
                  offset)
        
        return obj

    def __repr__(self):
        
        s = f'          FIR("Symmetry={self.symmetry}",'
        s += f' Coefficients={self.coefficients}, Divisor={self.coefficient_divisor})'
        return s


class Coefficients(Filter):
    """
    Coefficients Filter :class:
    
       **Attributes :**
     
        
        * transfer_function_type (str): one of  'LAPLACE (RADIANS/SECOND)','LAPLACE (HERTZ)','D
        * numerator_coefficients (list of floats)
        * denominator_coefficients (list of floats)
        
    """
    
    def __init__(self, filter_type, transfer_function_type, numerator_coefficients,
                 denominator_coefficients, offset=0):
        """
        Constructor
        
        :param filter_type: type of filter, necessarily 'Coefficients'
        :type filter_type: str
        :param transfer_function_type:
        :type transfer_function_type: str, one of 'LAPLACE (RADIANS/SECOND)','LAPLACE (HERTZ)','DIGITAL (Z-TRANSFORM)' 
        :param numerator_coefficients:
        :type numerator_coefficients: list of floats
        :param denominator_coefficients:
        :type denominator_coefficients: list of floats
        :param offset:
        :type offset: int
        
        """
        
        if transfer_function_type not in ["ANALOG (RADIANS/SECOND)",
                                          "ANALOG (HERTZ)",
                                          "DIGITAL"]:
            msg = 'Illegal transfer function type: "{transfer_function_type}" in stage #{stage_id}'
            logger.error(msg)
            raise TypeError(msg)

        self.transfer_function_type = transfer_function_type
        self.numerator_coefficients = numerator_coefficients
        self.denominator_coefficients = denominator_coefficients
        
        super().__init__(filter_type, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict, channel_modif={}, 
                                  selected_config={}, stage_id=-1):
        """
        Create Coefficients instance from an attributes_dict
        
        :param filter_type: type of filter, necessarily 'Coefficients'
        :type filter_type: str
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param stage_id: id of corresponding stage. Used for reporting only
        :type stage_id: int
        :returns: object of :class:`Coefficients`
        
        """
        obj = cls(filter_type, 
                  attributes_dict.get_configured_element('transfer_function_type', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   'DIGITAL'),
                  attributes_dict.get_configured_element('numerator_coefficients', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   []),
                  attributes_dict.get_configured_element('denominator_coefficients', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   []),
                  attributes_dict.get_configured_element('offset', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   0)
                  )
        return obj

    def __repr__(self):
        s = f'          Coefficients("Transfer Function Type={self.transfer_function_type}", '
        s += f'Numerator={self.numerator_coefficients}, '
        s += f'Denominator={self.denominator_coefficients})'
        return s


class ResponseList(Filter):
    """
    ResponseList Filter 
    
       **Attributes :**
     
        
        * response_list (list of floats): list of responses instead of function coefficients
    
    """
    
    def __init__(self, filter_type, response_list, offset=0):
        """
        Constructor
        
        :param filter_type: type of filter, necessarily 'ResponseList'
        :type filter_type: str
        :param response_list:
        :type response_list: list of floats
        :param offset:
        :type offset: int
        
        """
        
        self.response_list = response_list
        
        super().__init__(filter_type, offset)
        

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict, channel_modif={}, 
                                  selected_config={}, stage_id=-1):
        """
        Create Response List instance from an attributes_dict
        
        :param filter_type: type of filter, necessarily 'ResponseList'
        :type filter_type: str
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param stage_id: id of corresponding stage. Used for reporting only
        :type stage_id: int
        :returns: object of :class:`ResponseList`
        
        """
        obj = cls(filter_type, 
                  attributes_dict.get_configured_element('elements', channel_modif, selected_config, []), 
                  attributes_dict.get_configured_element('offset', channel_modif, selected_config, 0))
        
        return obj
    

    def __repr__(self):
        return f'          ResponseList("{self.response_list}")'


class Analog(PolesZeros):
    """
    Analog Filter (Flat PolesZeros filter)
    
       **Attributes :**
     
      
        *None*    
    
    """
    
    def __init__(self, filter_type, offset=0): 
        
        """
        Constructor
        
        :param filter_type: type of filter, necessarily 'Analog'
        :type filter_type: str
        :param offset:
        :type offset: int
        
        """
        
        self.poles = []
        self.zeros = []
        self.normalization_frequency = 1.
        self.normalization_factor = None
        
        super().__init__(filter_type, "LAPLACE (RADIANS/SECOND)", 
                         self.poles, self.zeros, self.normalization_frequency, self.normalization_factor, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict, channel_modif={}, 
                                  selected_config={}, stage_id=-1):
        
        """
        Create Analog instance from an attributes_dict
        
        :param filter_type: type of filter, necessarily 'Analog'
        :type filter_type: str
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param stage_id: id of corresponding stage. Used for reporting only
        :type stage_id: int
        :returns: object of :class:`Analog`
        
        """
        
        obj = cls(filter_type, attributes_dict.get_configured_element('offset', 
                                                                channel_modif, 
                                                                selected_config, 
                                                                0))
        return obj
    

    def __repr__(self):
        return '          Analog()'


class Digital(Coefficients):
    """
    Digital Filter (Flat Coefficients filter)
    
       **Attributes :**
     
      
        *None*    
    
    """
    
    def __init__(self, filter_type, offset=0):
        """
        Constructor
        
        :param filter_type: type of filter, necessarily 'Digital'
        :type filter_type: str
        :param offset:
        :type offset: int
        """
        
        self.transfer_function_type = 'DIGITAL'
        self.numerator_coefficients = [1.0]
        self.denominator_coefficients = []

        super().__init__(filter_type, "DIGITAL", self.numerator_coefficients, self.denominator_coefficients, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict, channel_modif={}, 
                                  selected_config={}, stage_id=-1):
        
        """
        Create Digital instance from an attributes_dict
        
        :param filter_type: type of filter, necessarily 'Digital'
        :type filter_type: str
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param stage_id: id of corresponding stage. Used for reporting only
        :type stage_id: int
        :returns: object of :class:`Digital`  
        """
        
        obj = cls(filter_type, attributes_dict.get_configured_element('offset', 
                                                                channel_modif, 
                                                                selected_config, 
                                                                0))
        return obj

    def __repr__(self):
        return '          Digital()'


class AD_Conversion(Coefficients):
    """
    AD_Conversion Filter (Flat Coefficients filter)
    
     **Attributes :**
     
      
        * input_full_scale (float)
        * output_full_scale (float)    
    
    """
    
    def __init__(self, filter_type, input_full_scale, output_full_scale, offset=0):
        """
        Constructor
        
        :param filter_type: type of filter, necessarily 'ADConversion'
        :type filter_type: str
        :param input_full_scale:
        :type input_full_scale: float
        :param output_full_scale:
        :type output_full_scale: float
        :param offset:
        :type offset: int    
        """
        
        self.transfer_function_type = 'DIGITAL'
        self.numerator_coefficients = [1.0]
        self.denominator_coefficients = []
        self.input_full_scale = input_full_scale
        self.output_full_scale = output_full_scale
        
        super().__init__(filter_type, "DIGITAL", 
                         self.numerator_coefficients, self.denominator_coefficients, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict, channel_modif={}, 
                                  selected_config={}, stage_id=-1):
        """
        Create AD_Conversion instance from an attributes_dict
        
        :param filter_type: type of filter, necessarily 'ADConversion'
        :type filter_type: str
        :param attribute_list: list of information file dictionaries for stages
        :type attribute_list: list of dicts or single dict
        :param channel_modif: channel modifications inherited from station
        :type channel_modif: dict or object of :class:`ObsMetadata`
        :param selected_config: the configuration description that will override or complement default values
        :type selected_config: dict or object of :class:`ObsMetadata`
        :param stage_id: id of corresponding stage. Used for reporting only
        :type stage_id: int
        :returns: object of :class:`ADConversion`      
        """
        obj = cls(filter_type, 
                  attributes_dict.get_configured_element('input_full_scale', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   None),
                  attributes_dict.get_configured_element('output_full_scale', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   None), 
                  attributes_dict.get_configured_element('offset', 
                                                   channel_modif, 
                                                   selected_config, 
                                                   0))
        return obj
    

    def __repr__(self):
        s = f'          ADConversion(Input Full Scale={self.input_full_scale:g}, '
        s += f'Output Full Scale={self.output_full_scale})'
        return s
