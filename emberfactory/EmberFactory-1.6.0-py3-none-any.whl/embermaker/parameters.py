from embermaker import helpers as hlp
from reportlab.lib.units import cm, mm
import re

"""
        gp[key] => 'main' part of the value
        gp.lst(key) => 'list' part of the value
"""


class ParamDict(dict):
    """
    ParamDict is meant to store Graphic Parameters. It is a substantially modified type of dictionnary, because
    - there is a mechanism to handle deprecated parameters, by copying them to new names and possibly issuing a message
    - parameters values are made of 3 parts: value = [main, list, type]
    The main part is a single value; the list part is a list containing additional information;
        the type is a single character: S for string type, F for float, L for length on the canvas (a float),
        B for boolean.
    paramdict[key] will return the 'main' value;
    paramdict.list[key] will return the additional list, if any.
    NB: this could be done with a parameter class having all 3 'parts' has attributes instead of a list.
    It would be slightly slower, but that would most likely not be significant.
    That would probably make the code more readable (e.g. value[Ø] would become parameter.main); but is it useful?
    """

    def __init__(self, *args, **kw):
        super(ParamDict, self).__init__(*args, **kw)
        self._deprecated = {}

    def __setitem__(self, key, data):
        """ Updates the in paramdict[key] by setting its
                'list part'=data if data is a list, otherwise its
                'main part'=data,
            handling deprecated parameters and rejecting unknown parameters
        """
        key = key.strip()
        isdeprec = self._handle_deprecated(key, data)
        if not isdeprec:
            if key not in self:
                hlp.addlogwarn('Unknown parameter: ' + key)
            else:
                value = self.getvalue(key)
                if isinstance(data, list):
                    # The input was a list => set it as list part of the parameter (value[1])
                    value[1] = data
                elif value[2] in ('F', 'L', 'B'):
                    data = data.strip() if isinstance(data, str) else data
                    # The input was not a list, and the parameter is not defined as a string
                    if data in ['', '-']:
                        # The input was empty
                        value[0] = None
                    elif value[2] == 'B':  # The parameter is defined as boolean
                        if isinstance(data, str) and data.lower() == 'false' or data == 0:
                            value[0] = False
                        elif isinstance(data, str) and data.lower() == 'true' or data == 1:
                            value[0] = True
                        else:
                            hlp.addlogwarn('Ignored parameter {} because its value ({}) could not be'
                                           'converted to a logical value (boolean)'. format(key, data))
                    else:  # A number is expected
                        try:
                            if data is not None:
                                value[0] = float(data)
                        except(ValueError, TypeError):
                            hlp.addlogwarn('Ignored parameter {} because its value ({}) '
                                           'could not be converted to a number'. format(str(key), str(data)))
                else:
                    # The parameter type is string and the input is not a list => string
                    value[0] = str(data)
                super(ParamDict, self).__setitem__(key, value)

    def setnew(self, key, value):
        """ Sets a new parameter key/value[main,list,type], handling deprecated parameters"""
        key = key.strip(' \t')  # Get rid trailing white spaces and/or tabs
        isdeprec = self._handle_deprecated(key, value)
        if not isdeprec:
            super(ParamDict, self).__setitem__(key, value)

    def getvalue(self, key):
        try:
            val = super(ParamDict, self).__getitem__(key)
        except KeyError:
            hlp.addlogwarn('Internal error - requested parameter is not defined: {}'.format(key))
            # For consistency with __setitem__, return None as the main value (= no value)
            val = [None, None, '']
        if not isinstance(val, list):
            hlp.addlogwarn('Malformed parameter: {}:{}'.format(key, val))
            val = [None, None, '']
        return val

    def __getitem__(self, key):
        return self.getvalue(key)[0]

    def __repr__(self, *args, **kwargs):
        """Provides a printed string from self"""
        out = ''
        for key in list(self):
            val = super(ParamDict, self).__getitem__(key)
            if len(val) > 1:
                out += "; {" if out != '' else '{'
                out += key + ": " + str(val[0])
                if val[1]:
                    out += " " + str(val[1])
                out += "}"
        return out

    def lst(self, key):
        return self.getvalue(key)[1]

    def get(self, key, default=None):
        """
        Mimics the traditional dict get, but provides the 'main' part of the parameter value only.
        This is meant to be used to in rare cases where a missing value needs to be substituted on the fly,
        it should not replace the 'static' default values provided in the file defining parameters.
        :param key:
        :param default:
        :return: the main part of the parameter if not None, else the default provided value.
        """
        main = self.getvalue(key)[0]
        if main is not None:
            return main
        else:
            return default

    def update(self, adict=None, **kwargs):
        """ Updates self with adict, handling deprecated parameters (nothing done for other cases)
            use of ParamDict.update(dict) is not recommended but was tested on a simple case."""
        if type(adict) is dict:
            for key in adict.keys():
                isdeprec = self._handle_deprecated(key.strip(), adict[key])
                if isdeprec:
                    del adict[key]
            if len(adict) > 0:
                super(ParamDict, self).update(adict, **kwargs)
        else:
            super(ParamDict, self).update(adict, **kwargs)

    def _handle_deprecated(self, key, value):
        """
        Does what self._deprecated says it should do to the passed key,value

        :param key:
        :param value:
        :return: isdeprecated: True if key is in the list of deprecated parameters
        """
        if key in list(self._deprecated):
            # the new parameter and the msg to use for this deprecated parameter [key]:
            newpars, msg = self._deprecated[key]
            if newpars is not None:
                for npa in newpars:
                    self[npa] = value
            if msg is not None:
                hlp.addlogwarn("Deprecated parameter: {}. {}".format(key, msg))
            return True
        return False

    def setdeprecated(self, deprecated):
        """
        Sets a dict of deprecated parameters including information on how to handle them.

        :param deprecated: a dict of deprecated parameters:
               {name_of_old_parameter: ((new_param_1, new_param_2 if any, ...), str warning_message or None)}
               new_params can be in a list or tuple, but if tuple, remember that ('newpar1')
               would not make a tuple, only ('newpar1',) would make one.
        :return:
        """
        self._deprecated = deprecated

    def readmdfile(self, filepath):
        """
        Generates a dictionnary of parameters (ParamDict) from a standard file providing parameter names, defaults, etc.
        :param filepath:
        :return:
        """
        with open(filepath) as fi:
            waittable = True
            for iline, line in enumerate(fi):
                line = line.rstrip('\n').strip(' \t|')  # cleanup: start after any |, get rid of end-of-line
                # Lines which are not in a table are not read and imply a status of 'waiting for table data':
                if line == '':
                    waittable = True
                    continue
                if waittable:
                    if "-------" in line:
                        waittable = False
                    continue
                # We reach this point when the line is in a table
                # lines containing certain html tags are only for the documentation, => pass
                if re.search('<.+?>', line) \
                        and any(tagf in line for tagf in ['<h2', '<h3>', '<h4>', '<section', '</section']):
                    continue
                cells = [cl.strip() for cl in line.split('|')]
                if "<del>" in cells[0]:  # Deprecated parameter - pass
                    continue
                if len(cells) != 3:
                    hlp.addlogwarn("Internal problem in the list of parameters (no description?): |{}|".format(line))
                    continue
                key, c1, c2 = cells
                # Get additional data, if any
                if '[' in c1 and ']' in c1:  # There is additional data
                    stdat = c1.find('[')
                    lst = c1[stdat+1: c1.find(']')]
                    lst = None if lst == '' else lst.split(';')
                    main = c1[:stdat].rstrip()
                else:
                    main = c1
                    lst = None
                main = main.replace('-', '')  # '-' or '' are equivalent and mean 'No value'
                # Get type of data and process value when needed:
                if "(number)" in c2:
                    dtype = 'F'
                    main = None if main == '' else float(main)
                elif "(length)" in c2:
                    dtype = 'L'
                    # Process units of length, if any (todo: consider moving to a more 'generic' place?)
                    if dtype == 'L':
                        if ' cm' in main:
                            main = float(main.replace(' cm', '')) * cm
                        elif ' mm' in main:
                            main = float(main.replace(' mm', '')) * mm
                        else:
                            main = None if main == '' else float(main)
                elif "(logical)" in c2:
                    dtype = 'B'  # Boolean
                    main = None if main == '' else main.lower() != 'false'
                else:  # Default type is string
                    dtype = 'S'
                self.setnew(key, [main, lst, dtype])
        return
