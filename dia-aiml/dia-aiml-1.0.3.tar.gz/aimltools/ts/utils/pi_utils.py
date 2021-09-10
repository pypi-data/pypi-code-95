from enum import Enum
import pandas as pd
import pathlib
from pathlib import Path
import aimltools

#launch configuration file
p2 = pathlib.PurePath(Path(globals()['__file__']).parent, 'pi_utils_cfg.py')
try:
    with open(p2) as fd:
        exec(fd.read())
except FileNotFoundError:
    print("Module \'{}\' requires to be initialized with a valid configuration file, but no file was found.".format(Path(globals()['__file__'])))
    print("Please ensure that a configuration file named \'{}\' exists in this folder: \'{}\'.".format("pi_utils_cfg.py", Path(globals()['__file__']).parent))
    print("Please ensure that the file contains valid paths to.NET assemblies used for reading data from OSI PI.")
    print("See file \'{}\' for an example.".format("pi_utils_cfg_sample.py"))
    print("Execution will now stop.")
    quit()


class BoundaryType(Enum):
    INSIDE = 1
    OUTSIDE = 2
    INTERPOLATED = 3


class PITagValues:

    def __init__(self, name, values):
        self.name = name
        self.values = values


class PITagValue:

    def __init__(self, utc_milliseconds, value):
        self.utc_milliseconds = utc_milliseconds
        self.value = value


class OSIPIReader:

    def __init__(self, servername, datetime_format, datetime_format_pi):
        self.piServers = PIServers()
        self.servername = servername
        self.piServer = self.piServers[servername]
        self.datetime_format = datetime_format
        self.datetime_format_pi = datetime_format_pi


    @property
    def datetime_format(self):
        return self.__datetime_format


    @datetime_format.setter
    def datetime_format(self, datetime_format):
        self.__datetime_format = datetime_format


    def read_tags(self, tagname_list, starttime, endtime, boundary_type):
        pi_tag_values=[]
        for tagname in tagname_list:
            pi_tag_values.append(self.__read_tag(tagname, starttime, endtime, boundary_type))

        return pi_tag_values


    def read_tag_interpolated(self, tagname, ts_list):
        pt = PIPoint.FindPIPoint(self.piServer, tagname)
        pt_list = PIPointList()
        pt_list.Add(pt)

        li = List[AFTime]()
        for ts in ts_list:
            ts_epoch = aimltools.ts.utils.generic_utils.DateTimeUtils.string_to_epoch_ciso8601(ts)
            ts_af = AFTime(ts_epoch)
            li.Add(ts_af)

        listResults = pt_list.InterpolatedValuesAtTimes(li, "", False, PIPagingConfiguration(PIPageType.TagCount, 1))

        pi_tag_value_list = list()
        for afVals in listResults:
            for afVal in afVals:
                dto = DateTimeOffset(afVal.Timestamp.LocalTime)
                pi_tag_value = PITagValue(dto.ToUnixTimeMilliseconds(), afVal.Value)
                pi_tag_value_list.append(pi_tag_value)

        pi_tag_values = PITagValues(tagname, pi_tag_value_list)
        return pi_tag_values


    def read_batch_tree(self, modulepath, starttime, endtime):
        start_time_dt = aimltools.ts.utils.generic_utils.DateTimeUtils.string_to_datetime_ciso8601(starttime)
        end_time_dt = aimltools.ts.utils.generic_utils.DateTimeUtils.string_to_datetime_ciso8601(endtime)

        # generate .Net DateTime
        start_time = DateTime(start_time_dt.year, start_time_dt.month, start_time_dt.day, start_time_dt.hour, start_time_dt.minute, start_time_dt.second)
        end_time = DateTime(end_time_dt.year, end_time_dt.month, end_time_dt.day, end_time_dt.hour, end_time_dt.minute, end_time_dt.second)

        #tzoh = str(start_time_dt.tzinfo)[4:6]
        #tzom = str(start_time_dt.tzinfo)[-2:]
        #tspan = TimeSpan(int(tzoh), int(tzom), 0)
        #start_time = DateTimeOffset(start_time_dt.year, start_time_dt.month, start_time_dt.day, start_time_dt.hour, start_time_dt.minute, start_time_dt.second, tspan)
        #end_time = DateTimeOffset(end_time_dt.year, end_time_dt.month, end_time_dt.day, end_time_dt.hour, end_time_dt.minute, end_time_dt.second, tspan)
        
        reader = PISDKReader(self.servername, self.datetime_format_pi, self.datetime_format_pi, '', '', '')
        pidata = reader.ReadBatchTree(start_time, end_time, modulepath)

        return pidata

    def __read_tag(self, tagname, starttime, endtime, boundary_type):
        starttime_utc_secs = aimltools.ts.utils.DateTimeUtils.string_to_epoch_ciso8601(starttime)
        endtime_utc_secs = aimltools.ts.utils.DateTimeUtils.string_to_epoch_ciso8601(endtime)

        pt = PIPoint.FindPIPoint(self.piServer, tagname)

        af_starttime = AFTime(starttime_utc_secs)
        af_endtime = AFTime(endtime_utc_secs)

        time_range = OSIPIReader.__setup_time_range_af(af_starttime, af_endtime)

        af_boundary_type = AFBoundaryType.Inside
        if boundary_type == BoundaryType.OUTSIDE:
            af_boundary_type = AFBoundaryType.Outside
        if boundary_type == BoundaryType.INTERPOLATED:
            af_boundary_type = AFBoundaryType.Interpolated

        af_vals = pt.RecordedValues(time_range, af_boundary_type, "", False)

        pi_tag_value_list = list()
        for afVal in af_vals:
            dto = DateTimeOffset(afVal.Timestamp.LocalTime)

            pi_tag_value = PITagValue(dto.ToUnixTimeMilliseconds(), afVal.Value)
            pi_tag_value_list.append(pi_tag_value)

        pi_tag_values = PITagValues(tagname, pi_tag_value_list)

        return pi_tag_values


    @staticmethod
    def __setup_time_range(starttime_str, endtime_str):
        prv = AFTimeZoneFormatProvider(AFTimeZone())
        af_time_range = AFTimeRange(starttime_str, endtime_str, prv)
        return af_time_range


    @staticmethod
    def __setup_time_range_af(starttime_af, endtime_af):
        af_time_range = AFTimeRange(starttime_af, endtime_af)
        return af_time_range


class PIDataUBSerializer:
    COL_UB_UID = 'uid'
    COL_UB_BATCHID = 'batch_id'
    COL_UB_PRODUCT = 'product'
    COL_UB_STARTTIME = 'start_time'
    COL_UB_ENDTIME = 'end_time'
    COL_UB_UTCSTART = 'utc_start'
    COL_UB_UTCEND = 'utc_end'
    COL_UB_PROCEDURE = 'procedure'
    COL_UB_MODULEUID = 'moduleuid'
    COL_UB_BATCHUID = 'batchuid'

    COLS_UB_DATAFRAME = [COL_UB_UID, COL_UB_BATCHID, COL_UB_PRODUCT, COL_UB_STARTTIME, COL_UB_ENDTIME, COL_UB_PROCEDURE, COL_UB_MODULEUID, COL_UB_BATCHUID]

    COL_SB_UID = 'uid'
    COL_SB_UBATCHUID = 'unitbatchuid'
    COL_SB_PATH = 'path'
    COL_SB_NAME = 'name'
    COL_SB_LEVEL = 'level'
    COL_SB_CHLDCNT = 'childcount'
    COL_SB_STARTTIME = 'starttime'
    COL_SB_ENDTIME = 'endtime'
    COL_SB_UTCSTART = 'utcstart'
    COL_SB_UTCEND = 'utcend'
    COL_SB_HEADINGUID = 'headinguid'
    COL_SB_PARENTUID = 'parentuid'

    COLS_SB_DATAFRAME = [COL_SB_UID, COL_SB_UBATCHUID, COL_SB_PATH, COL_SB_NAME, COL_SB_LEVEL, COL_SB_CHLDCNT, COL_SB_STARTTIME, COL_SB_ENDTIME, COL_SB_HEADINGUID, COL_SB_PARENTUID]

    def __init__(self):
        self.__ub_dict = dict.fromkeys(PIDataUBSerializer.COLS_UB_DATAFRAME)
        for key in self.__ub_dict.keys():
            self.__ub_dict[key] = []

        self.__sb_dict = dict.fromkeys(PIDataUBSerializer.COLS_SB_DATAFRAME)
        for key in self.__sb_dict.keys():
            self.__sb_dict[key] = []


    @staticmethod
    def batch_tree_to_ub_sb_df(pidata):
        pidataser = PIDataUBSerializer()
        [df_ub, df_sb] = pidataser.process_batches(pidata)
        return [df_ub, df_sb]


    def process_batches(self, pidata):
        for batch in pidata.get_batches():
            for unit_batch in batch.get_unitBatches():
                self.__process_unit_batch(unit_batch)

        df_ub = pd.DataFrame.from_dict(self.__ub_dict)
        df_ub[PIDataUBSerializer.COL_UB_UTCSTART] = [aimltools.ts.utils.generic_utils.DateTimeUtils.datetime_to_epoch(val) for val in self.__ub_dict[PIDataUBSerializer.COL_UB_STARTTIME]]
        df_ub[PIDataUBSerializer.COL_UB_UTCEND] = [aimltools.ts.utils.generic_utils.DateTimeUtils.datetime_to_epoch(val) for val in self.__ub_dict[PIDataUBSerializer.COL_UB_ENDTIME]]

        df_sb = pd.DataFrame.from_dict(self.__sb_dict)
        df_sb[PIDataUBSerializer.COL_SB_UTCSTART] = [aimltools.ts.utils.generic_utils.DateTimeUtils.datetime_to_epoch(val) for val in self.__sb_dict[PIDataUBSerializer.COL_SB_STARTTIME]]
        df_sb[PIDataUBSerializer.COL_SB_UTCEND] = [aimltools.ts.utils.generic_utils.DateTimeUtils.datetime_to_epoch(val) for val in self.__sb_dict[PIDataUBSerializer.COL_SB_ENDTIME]]

        return [df_ub, df_sb]

    def __process_unit_batch(self, unit_batch):
        self.__ub_dict[PIDataUBSerializer.COL_UB_UID].append(unit_batch.uid)
        self.__ub_dict[PIDataUBSerializer.COL_UB_BATCHID].append(unit_batch.batchid)
        self.__ub_dict[PIDataUBSerializer.COL_UB_PRODUCT].append(unit_batch.product)
        self.__ub_dict[PIDataUBSerializer.COL_UB_STARTTIME].append(pd.Timestamp(unit_batch.starttime, tz='utc'))
        self.__ub_dict[PIDataUBSerializer.COL_UB_ENDTIME].append(pd.Timestamp(unit_batch.endtime, tz='utc'))
        self.__ub_dict[PIDataUBSerializer.COL_UB_PROCEDURE].append(unit_batch.procedure)
        self.__ub_dict[PIDataUBSerializer.COL_UB_MODULEUID].append(unit_batch.moduleuid)
        self.__ub_dict[PIDataUBSerializer.COL_UB_BATCHUID].append(unit_batch.batchuid)
        if len(unit_batch.subBatches) > 0:
            level = 0
            path = "\\"
            self.__process_subbatches("", unit_batch.subBatches, unit_batch, path, level)

    def __process_subbatches(self, parent_uid, sub_batches, reference_unit_batch, path, level):
        for sub_batch in sub_batches:
            self.__process_subbatch(parent_uid, sub_batch, reference_unit_batch, path, level)

    def __process_subbatch(self, parent_uid, sub_batch, reference_unit_batch, path, level):
        self.__sb_dict[PIDataUBSerializer.COL_SB_UID].append(sub_batch.uid)
        self.__sb_dict[PIDataUBSerializer.COL_SB_UBATCHUID].append(reference_unit_batch.uid)
        self.__sb_dict[PIDataUBSerializer.COL_SB_PATH].append(path)
        self.__sb_dict[PIDataUBSerializer.COL_SB_NAME].append(sub_batch.name)
        self.__sb_dict[PIDataUBSerializer.COL_SB_LEVEL].append(level)
        self.__sb_dict[PIDataUBSerializer.COL_SB_CHLDCNT].append(len(sub_batch.subBatches))
        self.__sb_dict[PIDataUBSerializer.COL_SB_STARTTIME].append(pd.Timestamp(sub_batch.starttime, tz='utc'))
        self.__sb_dict[PIDataUBSerializer.COL_SB_ENDTIME].append(pd.Timestamp(sub_batch.endtime, tz='utc'))
        self.__sb_dict[PIDataUBSerializer.COL_SB_HEADINGUID].append(sub_batch.headinguid)
        self.__sb_dict[PIDataUBSerializer.COL_SB_PARENTUID].append(parent_uid)
        self.__iterate_subbatch(sub_batch.uid, sub_batch, reference_unit_batch, path, level)

    def __iterate_subbatch(self, parent_uid, sub_batch, reference_unit_batch, path, level):
        if len(sub_batch.subBatches) == 0:
            return
        path = path + sub_batch.name + "\\"
        level = level + 1
        self.__process_subbatches(parent_uid, sub_batch.subBatches, reference_unit_batch, path, level)


class S3OSIPIReader:
    @staticmethod
    def read_machine_status(full_path_to_file):
        data_location = 's3://{}'.format(full_path_to_file)
        df = pd.read_csv(data_location, parse_dates=['time'], infer_datetime_format=True)
        df.columns = ['Tag', 'Time', 'Status', 'Svalue', 'Pistatus', 'Flags']
        df.drop('Svalue', axis=1, inplace=True)
        df.drop('Pistatus', axis=1, inplace=True)
        df.drop('Flags', axis=1, inplace=True)
        return df


class FileOSIPIReader:

    @staticmethod
    def read_machine_status(full_path_to_file):
        df = pd.read_csv(full_path_to_file, parse_dates=['time'], infer_datetime_format=True)
        df.columns = ['Tag', 'Time', 'Status', 'Svalue', 'Pistatus', 'Flags']
        df.drop('Svalue', axis=1, inplace=True)
        df.drop('Pistatus', axis=1, inplace=True)
        df.drop('Flags', axis=1, inplace=True)
        return df