"""Main module."""
import teradataml as tdml

from .query_execution import execute_query

@execute_query
def getmydata(dimensions=['region', 'profil', 'plage_de_puissance_souscrite'],
              kpis={'sum': ['total_energie_soutiree_wh'], 'avg': [
                  'courbe_moyenne_num1_num2_Wh'], 'min': [], 'max': []},
              period=('2020-12-01', '2020-12-31'),
              period_agg=6,
              period_agg_units='hours',
              schema='ADLSLSEMEA_ENEDIS',
              table_name='Enedis_conso_v'
              ):
    """
    Description de ce que la fonction fait.

    :param dimensions: list of str. default ['region','profil','plage_de_puissance_souscrite']
    :param kpis: list of str. default 
    :param period: tuple of date str (date start, date end)
    :param period_agg: length of the aggregation period
    :param period_agg_units: unit of the aggregation period.
    """
    select = ""
    if period_agg is not None and period_agg_units is not None:
        group_by = f"""
        group by TIME(
        {period_agg_units}({period_agg})
        AND {','.join(dimensions)})
        using timecode(horodate)"""

        select = """
         $TD_TIMECODE_RANGE as TD_TIMECODE_RANGE
        ,CAST(BEGIN($TD_TIMECODE_RANGE) AS VARCHAR(32)) as START_PERIOD
        ,CAST(END($TD_TIMECODE_RANGE) AS VARCHAR(32)) as END_PERIOD
        """
    elif len(dimensions) == 0:
        group_by = ""
    else:
        group_by = f"""
        group by {' AND '.join(dimensions)})
        using timecode(horodate)"""

    query = f"""
    select 
       {select}
    -- dimensions
      ,{','.join(dimensions)}
    -- kpis
      ,{','.join([k+'('+i+') as '+k+'_'+i for k,v in kpis.items() for i in v ])}
      from  {schema}.{table_name}
      {group_by}
      where horodate between DATE '{period[0]}' and DATE '{period[1]}'
    """
    return query
