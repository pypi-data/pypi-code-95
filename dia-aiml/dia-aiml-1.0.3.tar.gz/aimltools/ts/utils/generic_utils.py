import logging
import pandas as pd
import ciso8601
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class GenericUtils:
    @staticmethod
    def read_timestamp(FILENAME):             
        try:
            with open(FILENAME) as file:
                data = file.readlines()
            latest_timestamp = data[-1]
            file.close()
            return latest_timestamp
        except (Exception,IOError) as error:
            logger.info("Unable to read file: {}".format(error))
        finally:
            file.close()
    
    
    @staticmethod
    def write_timestamp(ts, FILENAME, mode = 'w'):
        try:
            with open(FILENAME, mode) as file:
                file.write(ts + '\n')
                file.close()
            return
        except (Exception,IOError) as error:
            logger.info("Unable to write file: {}".format(error))
        finally:
            file.close()
            
    @staticmethod
    def cls_to_df(df_train_ft, cls_scores_list, cls_reslts_list, eqm_id, model_id, output_cols):
        #eqpm_id     integer NOT NULL,
        #modl_id     varchar(50) NOT NULL,
        #evnt_time   timestamp(6) with time zone NOT NULL,
        #score       real NOT NULL,
        #is_anomaly boolean NOT NULL,
        #feat_count 
        
        result_list = []
        i = 0
        for index, row in df_train_ft.iterrows():
            is_anomalous = False
            if cls_reslts_list[i] == 1:
                is_anomalous = True
            
            lst = df_train_ft.columns[row.notnull()]
            feature_count = len(lst)
            #rc_features = "|".join(lst)
            tmp = [eqm_id, model_id, index, cls_scores_list[i], is_anomalous, feature_count] 
            result_list.append(tmp)
            i = i + 1
    
        df_result = pd.DataFrame(result_list, columns = output_cols)
        return df_result


    @staticmethod
    def cls_res_to_df(df_train_ft, cls_res_list, model_id, score_thr, output_cols):
        result_list = []
        i = 0
        for index, row in df_train_ft.iterrows():
            res_str = "NORMAL"
            if cls_res_list[i] > score_thr:
                res_str = "ANOMALOUS"
            
            lst = df_train_ft.columns[row.notnull()]
            feature_count = len(lst)
            rc_features = "|".join(lst)
            tmp = [model_id, index, cls_res_list[i], res_str, rc_features, score_thr, feature_count] 
            result_list.append(tmp)
            i = i + 1
    
        df_result = pd.DataFrame(result_list, columns = output_cols)
        return df_result


class DateTimeUtils:
    @staticmethod
    def string_to_datetime_ciso8601(time_str):
        return ciso8601.parse_datetime(time_str)


    @staticmethod
    def datetime_to_epoch(dt):
        return dt.timestamp()


    @staticmethod
    def string_to_epoch_ciso8601(time_str):
        return DateTimeUtils.datetime_to_epoch(DateTimeUtils.string_to_datetime_ciso8601(time_str))


    @staticmethod
    def epoch_to_string(epoch_dt, time_str_format):
        return time.strftime(time_str_format, time.localtime(epoch_dt))


    @staticmethod
    def epoch_to_string_tz(epoch_dt, time_str_format, tzone):
        return datetime.fromtimestamp(epoch_dt, tzone).strftime(time_str_format)


    @staticmethod
    def datetime_to_string(dt, time_str_format):
        return dt.strftime(time_str_format)

