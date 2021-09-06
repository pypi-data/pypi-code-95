"""
CAPTURA

Este módulo contiene funciones para importar datos de bases externas

"""

import numpy as np
import requests
import pandas as pd
import bs4 as bs


pd.core.common.is_list_like = pd.api.types.is_list_like


#from .manipular import with_missing_columns



def read_OECD(dsname, country, subject, measure=None, frequency='Q', startDate=None, endDate=None):
    """
    La OECD provee una API que permite leer datos a través de un URL. Esta función construye tales URLs a partir de
    la información deseada.

    :param dsname:
    :param country:
    :param subject:
    :param measure:
    :param frequency:
    :param startDate:
    :param endDate:
    :return:
    """
    #TODO: COMPLETAR LA DOCUMENTACIÓN

    OECD_ROOT_URL = "https://stats.oecd.org/SDMX-JSON/data"

    params = dict(startTime=startDate, endTime=endDate)

    if dsname not in ['EO']:
        params['dimensionAtObservation'] = 'AllDimensions'

    if type(country) is str:
        location = country
        country = [country]
    else:
        location = '+'.join(country)

    if dsname in ['QNA', 'PRICES_CPI','STLABOUR','EO']:
        if measure:
            dim_str = '.'.join([location, subject, measure, frequency])
            filter_fields = ['LOCATION', 'SUBJECT', 'MEASURE', 'FREQUENCY', 'TIME_PERIOD']
        else:
            dim_str = '.'.join([location, subject, frequency])
            filter_fields = ['LOCATION', 'SUBJECT', 'FREQUENCY', 'TIME_PERIOD']
    elif dsname == 'MEI_PRICES':
        dim_str = '.'.join([subject, location, measure, frequency])
        filter_fields = ['SUBJECT', 'LOCATION', 'MEASURE', 'FREQUENCY', 'TIME_PERIOD']
    elif dsname == 'MEI_FIN':
        dim_str = '.'.join([subject, location, frequency])
        filter_fields = ['SUBJECT', 'LOCATION', 'FREQUENCY', 'TIME_PERIOD']
    else:
        print(f'Error: Not yet implemented for database {dsname}')

    url = '/'.join([OECD_ROOT_URL, dsname, dim_str, 'all'])
    print(f'Downloading data from {url}')


    response = requests.get(url=url, params=params)

    # Data transformation

    if (response.status_code == 200):

        responseJson = response.json()
        obsList = responseJson.get('dataSets')[0].get('observations')

        def make_list(dimension):
            return [item for item in responseJson.get('structure').get('dimensions').get('observation') if
                    item['id'] == dimension][0]['values']

        if (len(obsList) > 0):
            metadata = {a: make_list(a) for a in filter_fields}
            print('Data downloaded from %s' % response.url)
            print('SERIES: ', metadata['SUBJECT'][0]['name'])
            if measure:
                print('UNITS: ', metadata['MEASURE'][0]['name'], '\n\n')

            obs = pd.DataFrame(obsList).transpose()[[0]]
            obs.rename(columns={0: 'values'}, inplace=True)
            temp = pd.DataFrame([a.split(':') for a in obs.index])
            temp.columns = filter_fields

            for field in filter_fields:
                obs[field] = [metadata[field][int(t)]['id'] for t in temp[field]]

            data = obs.pivot_table(index='TIME_PERIOD', columns=['LOCATION'], values='values')
            #data = with_missing_columns(data, country)
            data.index = pd.period_range(start=data.index[0], periods=data.shape[0], freq=frequency)
            data.columns.name = ''
            return data

        else:

            print('Error: No available records, please change parameters')

    else:

        print('Error: %s' % response.status_code)
        print(response.url)


#==========================================================
# IMF DOTS data

def make_DOTS_series(xmlseries: bs.element.Tag):
    ref_area = xmlseries['ref_area']
    counterpart_area = xmlseries['counterpart_area']
    obs = xmlseries.find_all('obs')

    values = [float(x['obs_value']) for x in obs]
    dates = [x['time_period'] for x in obs]

    date_index = pd.period_range(start=dates[0], end=dates[-1], freq=xmlseries['freq'])
    index = pd.MultiIndex.from_product([[ref_area], [counterpart_area], date_index],
                                       names=['ref_area', 'counterpart_area', 'time_period'])
    if len(date_index) == len(values):
        return pd.Series(values, index=index, name=xmlseries['indicator'])
    else:
        temp = pd.Series(np.zeros_like(date_index, float), index=date_index, name=xmlseries['indicator'])
        for t, v in zip(dates, values):
            temp.loc[t] = v
        temp.index = index
        return temp




def make_DOTS_dataframe(xmldataset: bs.element.Tag):
    allseries = [make_DOTS_series(x) for x in xmldataset.find_all('series') if x.find('obs')]

    indicators = set([series.name for series in allseries])

    data_by_indicator = {indicator: list() for indicator in indicators}

    for series in allseries:
        data_by_indicator[series.name].append(series)

    for indicator in indicators:
        data_by_indicator[indicator] = pd.concat(data_by_indicator[indicator], axis=0)

    return pd.concat([data_by_indicator[indicator] for indicator in indicators], sort=True, axis=1)


def as_url_list(param):
    if type(param) is str:
        param = [param]
    return '+'.join(param)


def read_DOTS(indicator, ref_area, counterpart_area='W00', frequency='M', startPeriod=None, endPeriod=None):
    DOTS_ROOT_URL = 'http://dataservices.imf.org/REST/SDMX_XML.svc/CompactData/DOT/'
    params = dict(startPeriod=startPeriod, endPeriod=endPeriod)

    # Convert parameters to url lists
    indicator = as_url_list(indicator)
    ref_area = as_url_list(ref_area)
    counterpart_area = as_url_list(counterpart_area)

    url = DOTS_ROOT_URL + '.'.join([frequency, ref_area, indicator, counterpart_area])
    print(f'Downloading data from {url}')

    response = requests.get(url=url, params=params)

    # Data transformation

    if response.status_code == 200:
        soup = bs.BeautifulSoup(response.content, features='lxml')
        if soup.find('series'):  # True if at least 1 series in dataset
            return make_DOTS_dataframe(soup.find('dataset'))
        else:
            print('Error: No available records, please change parameters')
    else:
        print('Error: %s' % response.status_code)
        print(response.url)




#==========================================================
# IMF IFS data

def make_IFS_series(xmlseries: bs.element.Tag):
    ref_area = xmlseries['ref_area']
    date0 = xmlseries.find('obs')['time_period']
    values = [float(x['obs_value']) for x in xmlseries.find_all('obs')]
    nobs = len(values)
    dates = pd.period_range(start=date0, freq=xmlseries['freq'], periods=nobs)
    index = pd.MultiIndex.from_product([[ref_area], dates], names=['ref_area', 'time_period'])
    return pd.Series(values, index=index, name=xmlseries['indicator'])


def make_IFS_dataframe(xmldataset: bs.element.Tag):
    allseries = [make_IFS_series(x) for x in xmldataset.find_all('series')]

    indicators = set([series.name for series in allseries])

    data_by_indicator = {indicator: list() for indicator in indicators}

    for series in allseries:
        data_by_indicator[series.name].append(series)

    for indicator in indicators:
        data_by_indicator[indicator] = pd.concat(data_by_indicator[indicator], axis=0)

    return pd.concat([data_by_indicator[indicator] for indicator in indicators], sort=True, axis=1)


def read_IFS(indicator, ref_area, frequency='M', startPeriod=None, endPeriod=None):
    IFS_ROOT_URL = 'http://dataservices.imf.org/REST/SDMX_XML.svc/CompactData/IFS/'
    params = dict(startPeriod=startPeriod, endPeriod=endPeriod)

    # Convert parameters to url lists
    indicator = as_url_list(indicator)
    ref_area = as_url_list(ref_area)


    url = IFS_ROOT_URL + '.'.join([frequency, ref_area, indicator])
    print(f'Downloading data from {url}')

    response = requests.get(url=url, params=params)

    # Data transformation

    if response.status_code == 200:
        soup = bs.BeautifulSoup(response.content, features='lxml')
        if soup.find('series'):  # True if at least 1 series in dataset
            return make_IFS_dataframe(soup.find('dataset'))
        else:
            print('Error: No available records, please change parameters')
            #print(soup.prettify())
    else:
        print('Error: %s' % response.status_code)
        print(response.url)

