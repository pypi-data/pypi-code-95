from collections import deque
from geopy import distance
import gpxpy
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import windrose

# Code from https://gist.github.com/jeromer/2005586
def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def maneuvers(speed_mph, tack_raw, upwind, params):
    cnt = 0
    stopped_segments = []
    moving_segments = []
    crashes = []
    starboard_crashes = []
    port_crashes = []
    window = range(params["window_size"])
    is_moving = np.zeros(len(speed_mph))
    tack = np.zeros(len(speed_mph))
    is_moving[:params["window_size"]] = 1 if (np.mean(speed_mph[window]) >= (params["stopped_threshold_mph"] + params["moving_threshold_mph"])/2) else 0
    tack[:params["window_size"]] = np.median(tack_raw[window])

    crash_data = []

    for i in range(1, len(speed_mph)):
        window = range(min(i, len(speed_mph)-params["window_size"]), min(i+params["window_size"], len(speed_mph)))
        window_speed_mph = np.mean(speed_mph[window])
        if is_moving[i-1]==1:
            is_moving[i]=1
            if (tack[i-1]!=tack_raw[i]) and (len(set(tack_raw[window]))==1): # only update tack if consistent across the window
                # if we're updating tack, scroll back that update earlier in time
                tack[max(i-params["window_size"]+1,0):i] = np.median(tack_raw[window]) 
            tack[i] = tack[i-1]
            if window_speed_mph>params["stopped_threshold_mph"]:
                cnt += 1
            else:
                is_moving[i]=0
                moving_segments.append(cnt)
                crashes.append(i)
                is_moving[max(i-2*params["window_size"],0):i]=0 # Reset time before crash to not moving to clean up data
                
                tack_before_crash = tack[max(i-2*params["window_size"],0)]
                upwind_before_crash = upwind[max(i-2*params["window_size"],0)]
                if tack_before_crash==0:
                    tack_before_crash = np.median([x for x in tack[max(i-2*params["window_size"],0):i] if x!=0])
                if tack_before_crash==1: # port tack
                    port_crashes.append(i)
                else:
                    starboard_crashes.append(i)

                crash_data.append([i,
                                    "Port" if tack_before_crash==1 else "Starboard",
                                    "Upwind" if upwind_before_crash==1 else "Downwind"])
                
                tack[max(i-2*params["window_size"],0):i]=0 # Reset time before crash to not on a tack to clean up data
                cnt=1
        else:
            if window_speed_mph<params["moving_threshold_mph"]:
                cnt += 1
            else:
                is_moving[i] = 1
                stopped_segments.append(cnt)
                cnt=1

    return {
        "is_moving": is_moving,
        "tack": tack,
        "crashes": crashes,
        "crash_data": crash_data,
        "port_crashes": port_crashes,
        "starboard_crashes": starboard_crashes,
        "stopped_segments": stopped_segments, 
        "moving_segments": moving_segments}

# This chooses a wind direction that is in the middle of the range of directions that are almost-never-travelled
def wind_direction(bearing, speed):
    (bearing_density, bins) = np.histogram(bearing, bins=range(360))
    # Normalize so that if I spent an equal time going in each direction, each bin would have a density of 1.0
    bearing_density = list(bearing_density/np.sum(bearing_density)*360)

    # Pull out maximum and start it at 0 degrees for simplicity - this way I don't have to worry about the wind direction crossing 0
    offset = np.where(bearing_density == np.max(bearing_density))[0][0]
    bearing_density_offset = bearing_density[offset:]+bearing_density[:offset]

    # state 0 - a direction regularly travelled
    # state 1 - a direction not regularly travelled (and thus a candidate for the wind direction)
    state = 0
    cnt = 0
    start_loc = 0

    segments = []

    for i in range(len(bearing_density_offset)):
        if state==0:
            # 0.5 - arbitrary parameter between "direction regularly traveled" and "direction irregularly travelled"
            if bearing_density_offset[i]<0.5:
                state=1
                cnt=1
                start_loc=i
        else:
            if bearing_density_offset[i]<0.5:
                cnt+=1
            else:
                state=0
                segments.append((start_loc, cnt))

    segments = sorted(segments, key=lambda x: x[1], reverse=True)
    candidate = (segments[0][0] + offset + int(segments[0][1]/2)) % 360
    
    if 0.5*segments[0][1]<segments[1][1]:
        candidate_2 = (segments[1][0] + offset + int(segments[1][1]/2) + 180) % 360
        candidate = int((candidate+candidate_2)/2)

    # top N% downwind vmg should be greater than top N% upwind vmg
    # if that's not true, then I probably have my wind direction reversed
    vmg = np.cos((bearing-candidate)*np.pi/180)*speed
    top2percent_loc = int(len(bearing)/100)
    partition = np.partition(vmg, [top2percent_loc, -top2percent_loc])
    top_vmg_upwind = partition[-top2percent_loc]
    top_vmg_downwind = partition[top2percent_loc]
    if np.abs(top_vmg_downwind)<np.abs(top_vmg_upwind):
        candidate = (candidate + 180) % 360
    
    return candidate

class KiteFoilSession():
    default_params = {
        "stopped_threshold_mph": 8,
        "moving_threshold_mph":  10,
        "window_size":           5
    }
    
    def __init__(self, gpx_file, params=None):        
        with open(gpx_file, "r") as f:
            gpx = gpxpy.parse(f)
        
        self.process_gpx_file(gpx, params)
    
    def process_gpx_file(self, gpx, params):
        import time
        t = time.time()
        if params is None:
            params = {}
        
        for param in self.default_params:
            if param not in params:
                params[param] = self.default_params[param]
        
        data = gpx.tracks[0].segments[0].points
        point_list = [[point.longitude,
                       point.latitude,
                       point.elevation,
                       point.time.astimezone(tz=pytz.timezone("US/Pacific"))] for point in data]

        df = pd.DataFrame(data=point_list, columns=['lon', 'lat', 'alt', 'time'])
        
        df["distance_step"] = [0] + [distance.distance((data[i-1].latitude, data[i-1].longitude),
                                                       (data[i].latitude, data[i].longitude)).m
                                     for i in range(1, len(data))]
        df["distance_cumulative"] = np.cumsum(df["distance_step"])
        df["time_diff"] = [1] + [(data[i].time - data[i-1].time).total_seconds() for i in range(1, len(data))]
        df["bearing"] = [0] + [calculate_initial_compass_bearing((data[i-1].latitude, data[i-1].longitude),
                                                                 (data[i].latitude, data[i].longitude))
                               for i in range(1, len(data))]

        df['speed_mph'] = df['distance_step']/df['time_diff']*3600/1609
        df["speed_mph_capped"] = df["speed_mph"]
        df.loc[df["speed_mph"]>40,"speed_mph_capped"]=40
        df['time_elapsed_sec'] = np.cumsum(df['time_diff'])-1
        
        moving_locs = df["speed_mph"]>params["moving_threshold_mph"]
        wind_dir = wind_direction(df[moving_locs]["bearing"].values, df[moving_locs]["speed_mph"].values)
        
        self.calculated_wind_dir = wind_dir
        if "wind_dir" in params:
            wind_dir=params["wind_dir"]
        self.wind_dir=wind_dir
        df["vmg_mph"] = np.cos((df["bearing"]-wind_dir)*np.pi/180)*df["speed_mph"]
        df["speed_kts"] = df["speed_mph"]/1.1507794480235
        df["vmg_kts"] = df["vmg_mph"]/1.1507794480235
               
        df["upwind"] = np.sign(df["vmg_mph"])
        df["tack_raw"] = [1 if ((bearing-wind_dir) % 360)<180 else -1 for bearing in df["bearing"]]
        
        m = maneuvers(df["speed_mph"].values, df["tack_raw"].values, df["upwind"].values, params)
        df["is_moving"] = m["is_moving"]
        df["tack"] = m["tack"]
        crashes = m["crashes"]
        crash_data = m["crash_data"]
        port_crashes = m["port_crashes"]
        starboard_crashes = m["starboard_crashes"]
        stopped_segments = m["stopped_segments"]
        moving_segments = m["moving_segments"]

        crashes_df = pd.DataFrame(data=crash_data, columns=["Loc", "Tack", "Upwind"])
        self.crashes_df = crashes_df

        segment = np.ones(len(df))
        this_segment = 1
        for i in range(1, len(df)):
            if df.loc[i-1, "tack"]!=df.loc[i,"tack"]:
                this_segment+=1
            segment[i] = this_segment
        df["segment"] = segment

        df["upwind"] = df["is_moving"]*df["upwind"]
            
        transitions_port      = []
        transitions_starboard = []
        transitions = []

        tack = df["tack"][0]
        
        tacks = []
        jibes = []

        for i in range(len(df)):
            if tack != df["tack"][i]:
                if tack==1 and df["tack"][i]==-1:
                    transitions_port.append(i)
                    if df["upwind"][i]==1:
                        tacks.append(i)
                        transitions.append([i, "Port", "Tack"])
                    elif df["upwind"][i]==-1:
                        jibes.append(i)
                        transitions.append([i, "Port", "Jibe"])
                if tack==-1 and df["tack"][i]==1:
                    transitions_starboard.append(i)
                    if df["upwind"][i]==1:
                        tacks.append(i)
                        transitions.append([i, "Starboard", "Tack"])
                    elif df["upwind"][i]==-1:
                        jibes.append(i)
                        transitions.append([i, "Starboard", "Jibe"])
                tack=df["tack"][i]
        
        transitions_df = pd.DataFrame(data=transitions, columns=["Loc", "Tack", "Maneuver"])

        self.df = df
        self.transitions_port = transitions_port
        self.transitions_starboard = transitions_starboard
        self.transitions_df = transitions_df
        self.stopped_segments = stopped_segments
        self.moving_segments = moving_segments
        self.crashes = crashes
        self.port_crashes = port_crashes
        self.starboard_crashes = starboard_crashes
        self.tacks = tacks
        self.jibes = jibes
        
        stats = {}
        with np.errstate(invalid="ignore"):
            stats["start_time"] = df["time"].min()
            stats["stop_time"]  = df["time"].max()
            stats["duration"] = df["time"].max()-df["time"].min()
            num_crashes = len(stopped_segments)
            stats["num_crashes"] = num_crashes
            stats["num_starboard_tack_crashes"] = len(starboard_crashes)
            stats["num_port_tack_crashes"] = len(port_crashes)
            time_elapsed_minutes = (max(df["time"])-min(df["time"])).seconds/60.0
            stats["time_elapsed_minutes"] = time_elapsed_minutes
            stats["minutes_per_crash"] = time_elapsed_minutes / num_crashes
            successful_transitions = len(self.transitions_port)+len(self.transitions_starboard)
            stats["transition_success_percent"] = np.float64(100)*successful_transitions/(successful_transitions+num_crashes)
            stats["starboard_transition_success_percent"] = np.float64(100)*len(self.transitions_starboard)/(len(self.starboard_crashes)+len(transitions_starboard))
            stats["port_transition_success_percent"] = np.float64(100)*len(self.transitions_port)/(len(self.port_crashes)+len(self.transitions_port))
            stats["num_starboard_to_port_transitions"] = len(transitions_starboard)
            stats["num_port_to_starboard_transitions"] = len(transitions_port)
            stats["port_tack_success_percent"] = np.float64(100)*len(transitions_df[(transitions_df["Maneuver"]=="Tack") & (transitions_df["Tack"]=="Port")]) / (
                len(transitions_df[(transitions_df["Maneuver"]=="Tack") & (transitions_df["Tack"]=="Port")]) +
                len(crashes_df[(crashes_df["Upwind"]=="Upwind") & (crashes_df["Tack"]=="Port")]))
            stats["starboard_tack_success_percent"] = np.float64(100)*len(transitions_df[(transitions_df["Maneuver"]=="Tack") & (transitions_df["Tack"]=="Starboard")]) / (
                len(transitions_df[(transitions_df["Maneuver"]=="Tack") & (transitions_df["Tack"]=="Starboard")]) +
                len(crashes_df[(crashes_df["Upwind"]=="Upwind") & (crashes_df["Tack"]=="Starboard")]))
            stats["port_jibe_success_percent"] = np.float64(100)*len(transitions_df[(transitions_df["Maneuver"]=="Jibe") & (transitions_df["Tack"]=="Port")]) / (
                len(transitions_df[(transitions_df["Maneuver"]=="Jibe") & (transitions_df["Tack"]=="Port")]) +
                len(crashes_df[(crashes_df["Upwind"]=="Downwind") & (crashes_df["Tack"]=="Port")]))
            stats["starboard_jibe_success_percent"] = np.float64(100)*len(transitions_df[(transitions_df["Maneuver"]=="Jibe") & (transitions_df["Tack"]=="Starboard")]) / (
                len(transitions_df[(transitions_df["Maneuver"]=="Jibe") & (transitions_df["Tack"]=="Starboard")]) +
                len(crashes_df[(crashes_df["Upwind"]=="Downwind") & (crashes_df["Tack"]=="Starboard")]))
        self.stats=stats

    def windrose(self):
        n = int(len(self.df))
        wind = list(range(self.wind_dir-2, self.wind_dir+3))
        ax = windrose.plot_windrose(self.df[self.df["is_moving"]==1], var_name="speed_mph", direction_name="bearing", kind="contourf",bins=[x for x in range(10,30, 2)], nsector=180)
        ax.legend(title="Speed (MPH)")
        ax.contourf(wind*n, [30]*n*len(wind), nsector=360)
        text_offset = -5 if self.wind_dir>=270 or self.wind_dir<=90 else 5
        ax.text((90-self.wind_dir+text_offset)/180*np.pi, ax.get_ylim()[1]*0.75, "Wind Direction", fontsize=10)
        
    def map(self):
        fig = px.line_mapbox(self.df, lon="lon", lat="lat", color="tack", line_group="segment", mapbox_style="open-street-map", hover_data=["speed_mph", "bearing", "tack_raw", "distance_cumulative", "upwind"], zoom=14, height=1000)
        fig.add_trace(go.Scattermapbox(lat=self.df["lat"][self.tacks], lon=self.df["lon"][self.tacks], 
                      mode='markers',
                      marker=go.scattermapbox.Marker(size=10),
                      name="Tack"))
        fig.add_trace(go.Scattermapbox(lat=self.df["lat"][self.jibes], lon=self.df["lon"][self.jibes], 
                      mode='markers',
                      marker=go.scattermapbox.Marker(size=10),
                      name="Jibe"))
        fig.add_trace(go.Scattermapbox(lat=self.df["lat"][self.crashes], lon=self.df["lon"][self.crashes], 
                      mode='markers',
                      marker=go.scattermapbox.Marker(size=10),
                      name="Crash"))
        fig.show()