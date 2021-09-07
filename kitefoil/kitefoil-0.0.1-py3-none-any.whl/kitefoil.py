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

def angle_difference(a, b):
    theta = abs(a-b)%360
    return theta if theta<=180 else 360-theta

def angle_difference_180(a, b):
    theta = abs(a-b)%180
    return theta if theta<=90 else 180-theta

# This chooses a wind direction that is in the middle of the range of directions that are almost-never-travelled
def calculate_wind_direction(bearing):
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

    # prefer westerly directions over easterly for bay area
    if candidate < 180:
        candidate+=180
    
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
        if params is None:
            params = {}
        
        for param in self.default_params:
            if param not in params:
                params[param] = self.default_params[param]
        
        data = gpx.tracks[0].segments[0].points
        df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
        
        for point in data:
            df = df.append({'lon': point.longitude, 'lat' : point.latitude, 'alt' : point.elevation, 'time' : point.time.astimezone(tz=pytz.timezone("US/Pacific"))}, ignore_index=True)
        
        time_dif = [1]
        distance_cumulative = [0]
        distance_step = [0]
        bearing = [0]

        for index in range(len(data)):
            if index == 0:
                pass
            else:
                start = data[index-1]        
                stop = data[index]

                this_step_distance = distance.distance((start.latitude, start.longitude), (stop.latitude, stop.longitude)).m
                distance_step.append(this_step_distance)

                distance_cumulative.append(distance_cumulative[-1] + this_step_distance)

                time_delta = (stop.time - start.time).total_seconds()
                time_dif.append(time_delta)

                bearing.append(calculate_initial_compass_bearing((start.latitude, start.longitude), (stop.latitude, stop.longitude)))

        df['distance_cumulative'] = distance_cumulative
        df['distance_step'] = distance_step
        df['time_diff'] = time_dif
        df['speed_mph'] = df['distance_step']/df['time_diff']*3600/1609
        df['bearing'] = bearing
        df["speed_mph_capped"] = df["speed_mph"]
        df.loc[df["speed_mph"]>40,"speed_mph_capped"]=40

        df["wind"]=df["bearing"]+90
        df.loc[df["bearing"]>180, "wind"]=df["bearing"][df["bearing"]>180]-90
        df['time_elapsed_sec'] = np.cumsum(df['time_diff'])-1
        
        # ideally this would be based on when is_moving=1, but doing this way because I don't have is_moving in the DF yet
        wind_dir = calculate_wind_direction(df[df["speed_mph"]>params["moving_threshold_mph"]]["bearing"].values)
        
        self.calculated_wind_dir = wind_dir
        if "wind_dir" in params:
            wind_dir=params["wind_dir"]
        self.wind_dir=wind_dir
               
        df["upwind"] = [1 if angle_difference(wind_dir, bearing)<90 else -1 for bearing in df["bearing"]]
        df["tack_raw"] = [1 if ((bearing-wind_dir) % 360)<180 else -1 for bearing in df["bearing"]]
        
        cnt = 0
        stopped_segments = []
        moving_segments = []
        crashes = []
        starboard_tack_crashes = []
        port_tack_crashes = []
        window_queue = deque(range(params["window_size"]))
        window = list(window_queue)
        is_moving = np.mean(df["speed_mph"][window]) >= (params["stopped_threshold_mph"] + params["moving_threshold_mph"])/2
        tack = np.median(df["tack_raw"][window])
        df["is_moving"] = 0
        df["tack"] = 0

        for i in range(len(df)):
            window_queue.popleft()
            window_queue.append(i)
            window = list(window_queue)
            window_speed_mph = np.mean(df["speed_mph"][window])
            if is_moving==True:
                df.at[i,"is_moving"]=1
                if len(set(df["tack_raw"][window]))==1: # only update tack if consistent across the window
                    tack = np.median(df["tack_raw"][window])
                    df.loc[max(i-params["window_size"]+1,0):i,"tack"]=tack # if we're updating tack, scroll back that update earlier in time
                df.at[i,"tack"]=tack
                if window_speed_mph>params["stopped_threshold_mph"]:
                    cnt += 1
                else:
                    is_moving=False
                    moving_segments.append(cnt)
                    crashes.append(i)
                    df.loc[max(i-2*params["window_size"],0):i,"is_moving"]=0 # Reset time before crash to not moving to clean up data
                    
                    tack_before_crash = df.loc[max(i-2*params["window_size"],0),"tack"]
                    if tack_before_crash==0:
                        tack_before_crash = np.median([x for x in df.loc[max(i-2*params["window_size"],0):i,"tack"] if x!=0])
                    if tack_before_crash==1: # port tack
                        port_tack_crashes.append(i)
                    else:
                        starboard_tack_crashes.append(i)
                    
                    df.loc[max(i-2*params["window_size"],0):i,"tack"]=0 # Reset time before crash to not on a tack to clean up data
                    cnt=1
            if is_moving==False:
                if window_speed_mph<params["moving_threshold_mph"]:
                    cnt += 1
                else:
                    is_moving=True
                    stopped_segments.append(cnt)
                    cnt=1

        df["segment"] = 1
        this_segment = 1
        for i in range(1, len(df)):
            if df.loc[i-1, "tack"]!=df.loc[i,"tack"]:
                this_segment+=1
            df.loc[i, "segment"] = this_segment
        
        df["upwind"] = [0 if df["is_moving"][i]==0 else df["upwind"][i] for i in df.index]
                    
        transitions_port      = []
        transitions_starboard = []

        tack = df["tack"][0]
        
        tacks = []
        jibes = []

        for i in range(len(df)):
            if tack != df["tack"][i]:
                if tack==1 and df["tack"][i]==-1:
                    transitions_port.append(i)
                    if df["upwind"][i]==1:
                        tacks.append(i)
                    elif df["upwind"][i]==-1:
                        jibes.append(i)
                if tack==-1 and df["tack"][i]==1:
                    transitions_starboard.append(i)
                    if df["upwind"][i]==1:
                        tacks.append(i)
                    elif df["upwind"][i]==-1:
                        jibes.append(i)
                tack=df["tack"][i]
        
        self.df = df
        self.transitions_port = transitions_port
        self.transitions_starboard = transitions_starboard
        self.stopped_segments = stopped_segments
        self.moving_segments = moving_segments
        self.crashes = crashes
        self.port_tack_crashes = port_tack_crashes
        self.starboard_tack_crashes = starboard_tack_crashes
        self.tacks = tacks
        self.jibes = jibes
        
        stats = {}
        stats["start_time"] = df["time"].min()
        stats["stop_time"]  = df["time"].max()
        stats["duration"] = df["time"].max()-df["time"].min()
        num_crashes = len(stopped_segments)
        stats["num_crashes"] = num_crashes
        stats["num_starboard_tack_crashes"] = len(starboard_tack_crashes)
        stats["num_port_tack_crashes"] = len(port_tack_crashes)
        time_elapsed_minutes = (max(df["time"])-min(df["time"])).seconds/60.0
        stats["time_elapsed_minutes"] = time_elapsed_minutes
        stats["minutes_per_crash"] = time_elapsed_minutes / num_crashes
        successful_transitions = len(self.transitions_port)+len(self.transitions_starboard)
        stats["transition_success_percent"] = 100.0*successful_transitions/(successful_transitions+num_crashes)
        stats["starboard_transition_success_percent"] = 100.0*len(self.transitions_starboard)/(len(self.starboard_tack_crashes)+len(transitions_starboard))
        stats["port_transition_success_percent"] = 100.0*len(self.transitions_port)/(len(self.port_tack_crashes)+len(self.transitions_port))
        stats["num_starboard_to_port_transitions"] = len(transitions_starboard)
        stats["num_port_to_starboard_transitions"] = len(transitions_port)
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
                      text="Tack"))
        fig.add_trace(go.Scattermapbox(lat=self.df["lat"][self.jibes], lon=self.df["lon"][self.jibes], 
                mode='markers',
                marker=go.scattermapbox.Marker(size=10),
                text="Jibe"))
        fig.show()