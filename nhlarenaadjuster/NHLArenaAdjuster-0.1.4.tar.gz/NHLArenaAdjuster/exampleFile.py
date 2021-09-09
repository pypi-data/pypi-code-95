import pandas as pd
from NHLArenaAdjuster.CoordinateAdjuster import CoordinateAdjuster

season = "20202021"

pbp_url = f"https://hockey-data.harryshomer.com/pbp/nhl_pbp{season}.csv.gz"

pbp = pd.read_csv(pbp_url, compression='gzip')

fenwick = pbp.copy()
fenwick['abs_xC'] = fenwick.xC.abs()
fenwick = fenwick.loc[fenwick.Event.isin(["GOAL",'SHOT','MISS'])
                        &(fenwick.Ev_Zone == "Off")
                        &(fenwick.abs_xC > 24)]

fenwick['abs_yC'] = fenwick.yC.abs()
fenwick['isAway'] = (fenwick.Ev_Team == fenwick.Away_Team).astype(int)

columns = ['abs_xC','abs_yC','Home_Team','Away_Team','isAway']

fenwick.dropna(subset = columns, inplace=True)

ca = CoordinateAdjuster()

adj = ca.fit_transform(fenwick[columns])


print(adj)

