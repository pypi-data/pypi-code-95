from types import new_class
from bokeh.io.output import output_file
from bokeh.models.annotations import Legend
from bokeh.models.sources import CDSView
from bokeh.plotting import save, figure
from bokeh.io import show
from bokeh.models import ColumnDataSource, filters, Label
from bokeh.tile_providers import CARTODBPOSITRON, get_provider, ESRI_IMAGERY
from pyproj import Proj, transform
from bokeh.palettes import Spectral
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral11
from bokeh.models import ColorBar
from bokeh.transform import linear_cmap
import requests
import pandas as pd
import panel as pn
import sys

######### Global Variables #############
regions = ['Canada','BC','AB','MB','NB','NL','NS','ON','PE','QB','SK']
provinces_full = {
                'BC': "British Columbia",
                'AB': "Alberta",
                'MB': "Manitoba",
                'NB': "New Brunswick",
                'NL': "Newfoundland and Labrador",
                'NS': "Nova Scotia",
                'ON': "Ontario",
                'QB': "Quebec",
                'SK': "Saskatchewan",
                'PE': "Prince Edward Island"
                }
periods = ['2030','2035','2040','2045','2050']
plots = {}

def plot_baseline(year, region):
    wind_solar_extant = pd.read_csv('wind_solar_extant.csv', index_col=0)
    coordinates = pd.read_excel('coordinate.xlsx')

    Colour = "Capacity"
    Tile = "CARTODBPOSITRON_RETINA"
    Size = None
    columns = ['Installed Capacity', 'Generator Type', 'Grid Cell', 'Region']
    point_data = pd.DataFrame([], columns=columns)
    total_installed_capacity = 0
    tile_provider = get_provider(Tile)

    title = f"Solar and Wind Generators in {region} - {year}"
    TOOLTIPS = [("Type","@{Generator Type}"), ("Installed Capacity","@{Installed Capacity}"+" MWH")]
    
    lons,lats = [],[]
    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')
    
    world_lon1, world_lat1 = transform(outProj, inProj, -150, 30)
    world_lon2, world_lat2 = transform(outProj, inProj, -50, 80)
    p = figure(x_range=(world_lon1, world_lon2), y_range=(world_lat1, world_lat2),
                x_axis_type="mercator", y_axis_type="mercator",
                x_axis_label='Longitude', y_axis_label='Latitude',
                title=title, toolbar_location="left", tooltips=TOOLTIPS,
                tools="pan, wheel_zoom, lasso_select, hover, crosshair, reset", active_scroll="wheel_zoom",
                plot_width=700, plot_height=550,)
    p.add_tile(tile_provider)

    if region == 'Canada':
        for index,row in wind_solar_extant.iterrows():
            grid_cell = int(row.name.split('.')[0])
            gen_type = row.name.split('.')[1]
            province, latitude, longitude = None, None, None

            for i, location in coordinates.iterrows():
                if grid_cell == location.get('grid cell'):
                    latitude = location.get('lat')
                    longitude = location.get('lon')
                    province = location.get('PRENAME')
                    break
            
            installed_capacity_at_grid_cell = row.get(year)
            total_installed_capacity = total_installed_capacity + int(installed_capacity_at_grid_cell)
            new_row = pd.DataFrame([[float(installed_capacity_at_grid_cell), gen_type, grid_cell, province]], columns=columns)
            point_data = pd.concat([point_data,new_row], ignore_index=True)
            
            x,y = transform(outProj, inProj, longitude, latitude)
            lons.append(x)
            lats.append(y)
    else:
        for index,row in wind_solar_extant.iterrows():
            grid_cell = int(row.name.split('.')[0])
            gen_type = row.name.split('.')[1]
            latitude, longitude = None, None
            grid_cell_found = False

            for i,location in coordinates.loc[(coordinates['PRENAME'] == provinces_full[region])].iterrows():
                if grid_cell == location.get('grid cell'):
                    latitude = location.get('lat')
                    longitude = location.get('lon')
                    province = location.get('PRENAME')
                    grid_cell_found = True
                    break
            
            if grid_cell_found == False:
                continue

            installed_capacity_at_grid_cell = row.get(year)
            total_installed_capacity = total_installed_capacity + int(installed_capacity_at_grid_cell)
            new_row = pd.DataFrame([[float(installed_capacity_at_grid_cell), gen_type, grid_cell, province]], columns=columns)
            point_data = pd.concat([point_data,new_row], ignore_index=True)
            x,y = transform(outProj, inProj, longitude, latitude)
            
            lons.append(x)
            lats.append(y)

    point_data["MercatorX"] = lons
    point_data["MercatorY"] = lats
    
    colour1 = factor_cmap('Generator Type', palette=Spectral11, factors=sorted(point_data['Generator Type'].unique()))

    colour2 = linear_cmap(field_name='Installed Capacity', palette=Spectral11, low=min(point_data['Installed Capacity']),
                            high=max(point_data['Installed Capacity']))

    if Size == "Capacity":
        point_data['size'] = point_data['Installed Capacity']
        Size = 'size'
    else:
        Size=17

    if Colour == "Capacity":
        colour = colour2
        color_bar = ColorBar(color_mapper=colour2['transform'], label_standoff=12, title='Capacity')
        p.add_layout(color_bar, 'right')
        #legend = None
    else:
        colour=colour1
    source = ColumnDataSource(point_data)

    wind = CDSView(source=source, filters=[filters.GroupFilter(column_name='Generator Type', group='wind')])
    solar = CDSView(source=source, filters=[filters.GroupFilter(column_name='Generator Type', group='solar')])
    p.square(x="MercatorX", y="MercatorY", size=Size, line_color="black", legend_label='Wind',
            fill_color=colour, fill_alpha=0.8, source=source, view=wind)
    p.circle(x="MercatorX", y="MercatorY", size=Size, line_color="black", legend_label='Solar',
            fill_color=colour, fill_alpha=0.8, source=source, view=solar)

    annotation = Label(x=350, y=460, x_units='screen', y_units='screen',
                    text=f'Total Installed Capacity: {int(total_installed_capacity)} MW',
                    render_mode='css', border_line_color='black', background_fill_alpha=1.0,
                    background_fill_color='white', border_line_alpha=1.0, text_font_size='9pt')

    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    p.add_layout(annotation)
    del wind_solar_extant
    del coordinates
    return p, point_data

def plot_grid_cell(year, region, all_points):
    capacity_solar = pd.read_csv('capacity_solar.csv', header=None)
    capacity_wind = pd.read_csv('capacity_wind.csv', header=None)
    coordinates = pd.read_excel('coordinate.xlsx')
    
    Colour = "Capacity"
    Tile = "CARTODBPOSITRON_RETINA"
    Size = None
    total_installed_capacity = 0
    tile_provider = get_provider(Tile)
    columns = ['Installed Capacity', 'Generator Type', 'Grid Cell', 'Region', 'MercatorX', 'MercatorY']

    title = f"Solar and Wind Generators in {region} - {year}"
    TOOLTIPS = [("Type","@{Generator Type}"), ("Installed Capacity","@{Installed Capacity}"+" MWH")]
    
    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')
    print(type(all_points.at[0, 'Installed Capacity']))
    world_lon1, world_lat1 = transform(outProj, inProj, -150, 30)
    world_lon2, world_lat2 = transform(outProj, inProj, -50, 80)
    p = figure(x_range=(world_lon1, world_lon2), y_range=(world_lat1, world_lat2),
                x_axis_type="mercator", y_axis_type="mercator",
                x_axis_label='Longitude', y_axis_label='Latitude',
                title=title, toolbar_location="left", tooltips=TOOLTIPS,
                tools="pan, wheel_zoom, lasso_select, hover, crosshair, reset", active_scroll="wheel_zoom",
                plot_width=700, plot_height=550,)
    p.add_tile(tile_provider)

    for i,row in capacity_solar.loc[(capacity_solar[0] == f"('{year}'")].iterrows():
        capacity_increase = row.get(2)
        if int(capacity_increase) == 0:
            continue
        grid_cell = row.get(1).split("'")[1]
        gen_exists = False
        for index, row in all_points.iterrows():
            if grid_cell == row['Grid Cell'] and row['Generator Type'] == 'solar':
                all_points.at[index, 'Installed Capacity'] += capacity_increase

                # all_points.loc[(all_points['Grid Cell'] == grid_cell), 'Installed Capacity'] = all_points.loc[(all_points['Grid Cell'] == grid_cell), 'Installed Capacity'] + capacity_increase
                # total_installed_capacity = all_points.loc[(all_points['Grid Cell'] == grid_cell), 'Installed Capacity'] = all_points.loc[(all_points['Grid Cell'] == grid_cell), 'Installed Capacity'] + total_installed_capacity
                gen_exists = True
                break
        
        lon = coordinates.loc[(coordinates['grid cell'] == int(grid_cell))]['lon'].values[0]
        lat = coordinates.loc[(coordinates['grid cell'] == int(grid_cell))]['lat'].values[0]
        province = coordinates.loc[(coordinates['grid cell'] == int(grid_cell))]['PRENAME'].values[0]
        x,y = transform(outProj, inProj, lon, lat)

        if gen_exists == False:
            new_row = pd.DataFrame([[capacity_increase, 'solar', grid_cell, province, x, y]], columns=columns)
            all_points = pd.concat([all_points, new_row], ignore_index=True)

    for i,row in capacity_wind.loc[(capacity_wind[0] == f"('{year}'")].iterrows():
        capacity_increase = row.get(2)
        if int(capacity_increase) == 0:
            continue
        grid_cell = row.get(1).split("'")[1]
        gen_exists = False
        for index, row in all_points.iterrows():
            if grid_cell == row['Grid Cell'] and row['Generator Type'] == 'wind':
                all_points.at[index, 'Installed Capacity'] += capacity_increase
                # all_points.loc[(all_points['Grid Cell'] == grid_cell), 'Installed Capacity'] = all_points.loc[(all_points['Grid Cell'] == grid_cell), 'Installed Capacity'] + capacity_increase
                # total_installed_capacity = all_points.loc[(all_points['Grid Cell'] == grid_cell), 'Installed Capacity'] = all_points.loc[(all_points['Grid Cell'] == grid_cell), 'Installed Capacity'] + total_installed_capacity
                gen_exists = True
                break

        lon = coordinates.loc[(coordinates['grid cell'] == int(grid_cell))]['lon'].values[0]
        lat = coordinates.loc[(coordinates['grid cell'] == int(grid_cell))]['lat'].values[0]
        province = coordinates.loc[(coordinates['grid cell'] == int(grid_cell))]['PRENAME'].values[0]
        x,y = transform(outProj, inProj, lon, lat)

        if gen_exists == False:
            new_row = pd.DataFrame([[capacity_increase, 'wind', grid_cell, province, x, y]], columns=columns)   
            all_points = pd.concat([all_points, new_row], ignore_index=True)
    
    point_data = all_points

    total_installed_capacity = 0
    for index, row in point_data.iterrows():
        total_installed_capacity += row.get('Installed Capacity')

    colour1 = factor_cmap('Generator Type', palette=Spectral11, factors=sorted(point_data['Generator Type'].unique()))
    colour2 = linear_cmap(field_name='Installed Capacity', palette=Spectral11, low=min(point_data['Installed Capacity']),
                        high=max(point_data['Installed Capacity']))

    if Size == "Capacity":
        point_data['size'] = point_data['Installed Capacity']
        Size = 'size'
    else:
        Size=17

    if Colour == "Capacity":
        colour = colour2
        color_bar = ColorBar(color_mapper=colour2['transform'], label_standoff=12, title='Capacity')
        p.add_layout(color_bar, 'right')
        #legend = None
    else:
        colour=colour1
    source = ColumnDataSource(point_data)

    wind = CDSView(source=source, filters=[filters.GroupFilter(column_name='Generator Type', group='wind')])
    solar = CDSView(source=source, filters=[filters.GroupFilter(column_name='Generator Type', group='solar')])
    p.square(x="MercatorX", y="MercatorY", size=Size, line_color="black", legend_label='Wind',
            fill_color=colour, fill_alpha=0.8, source=source, view=wind)
    p.circle(x="MercatorX", y="MercatorY", size=Size, line_color="black", legend_label='Solar',
            fill_color=colour, fill_alpha=0.8, source=source, view=solar)

    annotation = Label(x=350, y=460, x_units='screen', y_units='screen',
                    text=f'Total Installed Capacity: {int(total_installed_capacity)} MW',
                    render_mode='css', border_line_color='black', background_fill_alpha=1.0,
                    background_fill_color='white', border_line_alpha=1.0, text_font_size='9pt')

    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    p.add_layout(annotation)
    return p, all_points

def plot_grid_cell_prov(year, region, all_points):

    Colour = "Capacity"
    Tile = "CARTODBPOSITRON_RETINA"
    Size = None
    total_installed_capacity = 0
    tile_provider = get_provider(Tile)

    title = f"Solar and Wind Generators in {region} - {year}"
    TOOLTIPS = [("Type","@{Generator Type}"), ("Installed Capacity","@{Installed Capacity}"+" MWH")]
    
    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')
    
    world_lon1, world_lat1 = transform(outProj, inProj, -150, 30)
    world_lon2, world_lat2 = transform(outProj, inProj, -50, 80)
    p = figure(x_range=(world_lon1, world_lon2), y_range=(world_lat1, world_lat2),
                x_axis_type="mercator", y_axis_type="mercator",
                x_axis_label='Longitude', y_axis_label='Latitude',
                title=title, toolbar_location="left", tooltips=TOOLTIPS,
                tools="pan, wheel_zoom, lasso_select, hover, crosshair, reset", active_scroll="wheel_zoom",
                plot_width=700, plot_height=550,)
    p.add_tile(tile_provider)

    point_data = all_points.loc[all_points['Region'] == provinces_full[region]]
    # if year == '2030' and region == 'BC':
    #     point_data.to_csv('help_me.csv')
    total_installed_capacity = 0
    for index, row in point_data.iterrows():
        total_installed_capacity += row.get('Installed Capacity')

    colour1 = factor_cmap('Generator Type', palette=Spectral11, factors=sorted(point_data['Generator Type'].unique()))
    colour2 = linear_cmap(field_name='Installed Capacity', palette=Spectral11, low=min(point_data['Installed Capacity']),
                        high=max(point_data['Installed Capacity']))

    if Size == "Capacity":
        point_data['size'] = point_data['Installed Capacity']
        Size = 'size'
    else:
        Size=17

    if Colour == "Capacity":
        colour = colour2
        color_bar = ColorBar(color_mapper=colour2['transform'], label_standoff=12, title='Capacity')
        p.add_layout(color_bar, 'right')
        #legend = None
    else:
        colour=colour1
    source = ColumnDataSource(point_data)

    wind = CDSView(source=source, filters=[filters.GroupFilter(column_name='Generator Type', group='wind')])
    solar = CDSView(source=source, filters=[filters.GroupFilter(column_name='Generator Type', group='solar')])
    p.square(x="MercatorX", y="MercatorY", size=Size, line_color="black", legend_label='Wind',
            fill_color=colour, fill_alpha=0.8, source=source, view=wind)
    p.circle(x="MercatorX", y="MercatorY", size=Size, line_color="black", legend_label='Solar',
            fill_color=colour, fill_alpha=0.8, source=source, view=solar)

    annotation = Label(x=350, y=460, x_units='screen', y_units='screen',
                    text=f'Total Installed Capacity: {int(total_installed_capacity)} MW',
                    render_mode='css', border_line_color='black', background_fill_alpha=1.0,
                    background_fill_color='white', border_line_alpha=1.0, text_font_size='9pt')

    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    p.add_layout(annotation)
    return p

def get_plot(Regions, Periods):
    return plots[f"{Regions}-{Periods}"]

def main():
    all_points = None
    for region in regions:
        plot, point_data = plot_baseline('2025', region)
        plots[f"{region}-2025"] = plot
        if region == 'Canada':
            all_points = point_data

    period_dict = {}
    for year in periods:
        plot, period_dict[year] = plot_grid_cell(year, 'Canada', all_points)
        all_points = period_dict[year]
        plots[f"Canada-{year}"] = plot

    for region in regions[1:]:
        for year in periods:
            plot = plot_grid_cell_prov(year, region, period_dict[year])
            plots[f"{region}-{year}"] = plot
    
    periods.insert(0, '2025')
    scenarios = dict(Regions=regions, Periods=periods)
    
    i = pn.interact(get_plot, **scenarios)
    p = pn.Row(i[1],i[0])
    p.save('plots/installed_capacity.html', embed=True)
    p.show()
    
if __name__ == '__main__':
    main()