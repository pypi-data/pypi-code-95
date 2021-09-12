#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from datetime import datetime, timezone

from emhass.retrieve_hass import retrieve_hass
from emhass.optimization import optimization
from emhass.forecast import forecast
from emhass.utils import get_root, get_root_2pardir, get_yaml_parse, get_days_list, get_logger

# create logger
logger, ch = get_logger(__name__, file=False)

def setUp():
    
    try:
        root = get_root()
        retrieve_hass_conf, optim_conf, plant_conf = get_yaml_parse(root)
    except:
        root = get_root_2pardir()
        retrieve_hass_conf, optim_conf, plant_conf = get_yaml_parse(root)
    
    days_list = get_days_list(retrieve_hass_conf['days_to_retrieve'])
    var_list = [retrieve_hass_conf['var_load'], retrieve_hass_conf['var_PV']]
    
    rh = retrieve_hass(retrieve_hass_conf['hass_url'], retrieve_hass_conf['long_lived_token'], 
                       retrieve_hass_conf['freq'], retrieve_hass_conf['time_zone'])
    rh.get_data(days_list, var_list,
                     minimal_response=False, significant_changes_only=False)
    rh.prepare_data(retrieve_hass_conf['var_load'], load_negative = retrieve_hass_conf['load_negative'],
                         set_zero_min = retrieve_hass_conf['set_zero_min'], 
                         var_replace_zero = retrieve_hass_conf['var_replace_zero'], 
                         var_interp = retrieve_hass_conf['var_interp'])
    df_input_data = rh.df_final.copy()
    
    fcst = forecast(retrieve_hass_conf, optim_conf, plant_conf)
    df_weather = fcst.get_weather_forecast(method='scrapper')
    P_PV_forecast = fcst.get_power_from_weather(df_weather)
    P_load_forecast = fcst.get_load_forecast()
    df_input_data_dayahead = pd.concat([P_PV_forecast, P_load_forecast], axis=1)
    df_input_data_dayahead.columns = ['P_PV_forecast', 'P_load_forecast']
    
    opt = optimization(retrieve_hass_conf, optim_conf, plant_conf, days_list)

    input_data_dict = {
        'root': root,
        'retrieve_hass_conf': retrieve_hass_conf,
        'df_input_data': df_input_data,
        'df_input_data_dayahead': df_input_data_dayahead,
        'opt': opt,
        'rh': rh,
        'fcst': fcst,
        'P_PV_forecast': P_PV_forecast,
        'P_load_forecast': P_load_forecast
    }
    return input_data_dict
    
def perfect_forecast_optim():
    input_data_dict = setUp()
    df_input_data = input_data_dict['opt'].get_load_unit_cost(input_data_dict['df_input_data'])
    opt_res = input_data_dict['opt'].perform_perfect_forecast_optim(df_input_data)
    return opt_res
    
def dayahead_forecast_optim():
    input_data_dict = setUp()
    df_input_data_dayahead = input_data_dict['opt'].get_load_unit_cost(input_data_dict['df_input_data_dayahead'])
    opt_res_dayahead = input_data_dict['opt'].perform_dayahead_forecast_optim(
        df_input_data_dayahead, input_data_dict['P_PV_forecast'], input_data_dict['P_load_forecast'])
    # Save CSV file for publish_data
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    filename = 'opt_res_dayahead_'+today.strftime("%Y_%m_%d")
    opt_res_dayahead.to_csv(input_data_dict['root'] + '/data/' + filename + '.csv', index_label=False)
    return opt_res_dayahead
    
def publish_data():
    # Check if a day ahead optimization has been performed (read CSV file)
    input_data_dict = setUp()
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    filename = 'opt_res_dayahead_'+today.strftime("%Y_%m_%d")
    if not os.path.isfile(input_data_dict['root'] + '/data/' + filename + '.csv'):
        logger.error("File not found error, run the dayahead_forecast_optim first.")
    else:
        opt_res_dayahead = pd.read_csv(input_data_dict['root'] + '/data/' + filename + '.csv')
        opt_res_dayahead.index = pd.to_datetime(opt_res_dayahead.index)
    # Estimate the current index
    today_precise = datetime.now(input_data_dict['retrieve_hass_conf']['time_zone']).replace(second=0, microsecond=0)
    idx_closest = opt_res_dayahead.index.get_loc(today_precise,method='nearest')
    # Publish PV forecast
    input_data_dict['rh'].post_data(opt_res_dayahead['P_PV'], idx_closest, 
                                    'sensor.p_pv_forecast', "W", "PV Power Forecast")
    # Publish Load forecast
    input_data_dict['rh'].post_data(opt_res_dayahead['P_Load'], idx_closest, 
                                    'sensor.p_load_forecast', "W", "Load Power Forecast")
    # Publish deferrable loads
    for k in range(input_data_dict['opt'].optim_conf['num_def_loads']):
        input_data_dict['rh'].post_data(opt_res_dayahead["P_deferrable{}".format(k)], idx_closest, 
                                        'sensor.p_deferrable{}'.format(k), "W", "Deferrable Load {}".format(k))
    # Publish battery power
    if input_data_dict['opt'].optim_conf['set_use_battery']:
        input_data_dict['rh'].post_data(opt_res_dayahead['P_batt'], idx_closest,
                                        'sensor.p_batt_forecast', "W", "Battery Power Forecast")
        

if __name__ == '__main__':
    # opt_res = perfect_forecast_optim()
    # opt_res_dayahead = dayahead_forecast_optim()
    publish_data()