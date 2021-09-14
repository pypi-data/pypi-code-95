import multiprocessing as mp
from aimltools.ts.distances import *
import itertools
import tslearn.barycenters


class GoldenCycle():
    
    def __init__(self):
        pass
    
    def get_closest_real_cycle(self, gc, df_tag, distance_metric):
        cycle_list = df_tag.cycle.unique()
        d_min = float('inf')
        grc_min = []
        cycle_min = -1
        logger.info("candidate cycles: {}".format(len(cycle_list)))
        for cycle_n in cycle_list:
            ts = df_tag[df_tag.cycle == cycle_n].value.values
            d = distance_metric.compute_distance_(gc, ts)
            if d < d_min:
                d_min = d
                grc_min = ts
                cycle_min = cycle_n

        logger.info("closest real cycle: {}".format(cycle_min))
        return grc_min

    def get_barycenter(self, df_tag, barycenter_type):

        def create_ts_list(dfn):
            cycle_list = dfn.cycle.unique()
            ts_list = []
            for cycle_n in cycle_list:
                ts = dfn[dfn.cycle == cycle_n].value
                ts_list.append(ts)
            return ts_list

        if barycenter_type == 'euc':
            br = list(itertools.chain.from_iterable(tslearn.barycenters.euclidean_barycenter(create_ts_list(df_tag))))
        elif barycenter_type == 'dtw_avg':
            br = list(itertools.chain.from_iterable(tslearn.barycenters.dtw_barycenter_averaging(create_ts_list(df_tag),max_iter=50, tol=1e-3)))
        elif barycenter_type == 'dtw_avg_gradient':
            br = list(itertools.chain.from_iterable(tslearn.barycenters.dtw_barycenter_averaging_subgradient(create_ts_list(df_tag),max_iter=10,random_state=0)))
        elif barycenter_type == 'sdtw':
            br = list(itertools.chain.from_iterable(tslearn.barycenters.softdtw_barycenter(create_ts_list(df_tag), max_iter=5)))
        return br

    def calculate_single_golden_mp(self, df_tag, distance_metric, return_dict, real, barycenter_type):
        tagn = df_tag.tag.unique()[0]
        cycle_cnt = len(df_tag.cycle.unique())
        logger.info("calculating barycenter for tag {} ({} cycles)".format(tagn, cycle_cnt))
        br = self.get_barycenter(df_tag,barycenter_type)
        if real:
            logger.info("evaluating closest real cycle")
            br = self.get_closest_real_cycle(br, df_tag, distance_metric)
            br = br.reshape(-1).tolist()
        return_dict[tagn] = br

    def compute_golden(self,df, real, distance_metric, barycenter_type):
        jobs = []
        manager = mp.Manager()
        return_dict = manager.dict()
        for tagname in df.tag.unique():
            df_tag = df[df.tag == tagname]
            p = mp.Process(target=self.calculate_single_golden_mp, args=(df_tag, distance_metric, return_dict, real, barycenter_type))
            jobs.append(p)
            p.start()   
        for p in jobs:
            p.join()
        return return_dict
   

def real_golden_cycle(df, distance_metric = [], barycenter_type = 'dtw_avg'):

    golden_class = GoldenCycle()
    golden_cycle = golden_class.compute_golden(df, distance_metric = distance_metric, barycenter_type = barycenter_type, real = True)
    return golden_cycle.copy()


def nonreal_golden_cycle(df, barycenter_type = 'dtw_avg'):
    
    distance_metric = None
    golden_class = GoldenCycle()
    golden_cycle = golden_class.compute_golden(df, distance_metric = distance_metric, barycenter_type = barycenter_type, real = False)
    return golden_cycle.copy()