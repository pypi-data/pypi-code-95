"""Data config file"""


# Configure visualizations when 1 set (x,y) per XML document
# Need to gather all XML documents for 1 plot

# In the path, '.' starts a dict
# In the path, '/' starts a list of dicts

# List of dicts
# Each dict defined will be a plot
# X and Y parameters have to be defined, has to be a 'parameterName' from config_parameters
# 'idsNames' is optional, default value will be intersection of 'idsNames' from both parameters

# Time has to be under UTC format and has to be named "Time (UTC)" for the time range selection to work properly

config_charts = [
    {
        'xName': 'Time (UTC)',
        'yName': 'Elevation',
    },
    {
        'xName': 'Time (UTC)',
        'yName': 'Azimuth',
    },
    {
        'xName': 'Time (UTC)',
        'yName': 'CNO',
    },
    {
        'xName': 'Time (UTC)',
        'yName': 'Residual',
    },
    {
        'xName': 'Elevation',
        'yName': 'Azimuth',
        'idsName': ['Satellite'],
    },
    {
        'xName': 'Elevation',
        'yName': 'CNO',
    },
    {
         'xName': 'Time (UTC)',
         'yName': 'Time Offset',
    },
]


# Each plotable parameter
# They can be part of different schemas from the DB
# 'parameterName' will appear on the plot to define the parameter
# 'idsNames' is None or a List, each element of the list has to be an 'idName' from config_ids
# 'idsNames' are used to group elements (will appear in different colors / shapes on charts)
# If a same parameter is present on two or more schema, 'parameterPath' has to be a list of all those paths
# 'unitPath' is optional
# 'variablePath' is optional but can define the variable parameter of an experiment
config_parameters = [
    {
        'parameterName': 'Time (UTC)',
        'idsNames': [],
        # Same variable on two different schemas
        'parameterPath': ['data.receiver.time/utc.value', 'timeintervalcounterdata.timeintervalcounter/startdate'],
        'unitPath': None,
        'variablePath': None
    },
    {
        'parameterName': 'Clock Accuracy',
        'idsNames': ['Data Origin'],
        'parameterPath': 'data.receiver.time/clkacc.value',
        'unitPath': 'data.receiver.time/clkacc.unit',
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'Clock Bias',
        'idsNames': ['Data Origin'],
        'parameterPath': 'data.receiver.time/clkbias.value',
        'unitPath': 'data.receiver.time/clkbias.unit',
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'Clock Drift',
        'idsNames': ['Data Origin'],
        'parameterPath': 'data.receiver.time/clkdrift.value',
        'unitPath': 'data.receiver.time/clkdrift.unit',
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'PDOP',
        'idsNames': ['Data Origin'],
        'parameterPath': 'data.receiver.time/pdop.value',
        'unitPath': None,
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'TM0 Rising',
        'idsNames': ['Data Origin'],
        'parameterPath': 'data.receiver.time/tm0rising.tm0value',
        'unitPath': None,
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'TPQerr',
        'idsNames': ['Data Origin'],
        'parameterPath': 'data.receiver.time/tpqerr.value',
        'unitPath': 'data.receiver.time/tpqerr.unit',
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'Elevation',
        'idsNames': ['Satellite', 'Data Origin'],
        'parameterPath': 'data.receiver.satellites.satellite/elevation.value',
        'unitPath': 'data.receiver.satellites.satellite/elevation.unit',
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'Azimuth',
        'idsNames': ['Satellite', 'Data Origin'],
        'parameterPath': 'data.receiver.satellites.satellite/azimuth.value',
        'unitPath': 'data.receiver.satellites.satellite/azimuth.unit',
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'CNO',
        'idsNames': ['Satellite', 'Data Origin'],
        'parameterPath': 'data.receiver.satellites.satellite/cno.value',
        'unitPath': 'data.receiver.satellites.satellite/cno.unit',
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'Residual',
        'idsNames': ['Satellite', 'Data Origin'],
        'parameterPath': 'data.receiver.satellites.satellite/residual.value',
        'unitPath': 'data.receiver.satellites.satellite/residual.unit',
        'variablePath': 'data.receiver.time/utc.value',
    },
    {
        'parameterName': 'Counter',
        'idsNames': [],
        'parameterPath': 'timeintervalcounterdata.timeintervalcounter/counter.countervalue',
        'unitPath': 'timeintervalcounterdata.timeintervalcounter/counter.unit',
        'variablePath': 'timeintervalcounterdata.timeintervalcounter/startdate',
    },
    {
        'parameterName': 'Time Offset',
        'idsNames': [],
        'parameterPath': 'timeintervalcounterdata.timeintervalcounter/timeoffset.timeoffsetvalue',
        'unitPath': 'timeintervalcounterdata.timeintervalcounter/timeoffset.unit',
        'variablePath': 'timeintervalcounterdata.timeintervalcounter/startdate',
    }]


# 'idName' will appear on the plot to define a group
config_ids = [
    {
        'idName': 'Satellite',
        'idPath': 'data.receiver.satellites.satellite/satelliteID',
    },
    {
        'idName': 'Data Origin',
        'idPath': 'data.receiver.receiverinfo.id',
    }]
