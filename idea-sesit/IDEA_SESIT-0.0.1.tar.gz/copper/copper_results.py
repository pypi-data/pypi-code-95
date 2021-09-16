from bokeh.models.annotations import ColorBar
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import output, show, output_file, save
from bokeh.palettes import Bokeh5, Spectral10
from jinja2.nodes import Output
import pandas as pd

def plot_line(national, provincial):
    plot = figure(title='National Emmisions', x_axis_label='Year', y_axis_label='Emmision (Mt C02)')
    plot.line(x=national.index, y=national['Emission MT'], legend_label='Canada', line_width=3, color='red')
    
    for row, colour in zip(provincial.iloc, Spectral10):
        plot.line(x=row.index, y=row, legend_label=row.name, line_width=3, color=colour)
    
    plot.legend.location = "top_right"
    plot.legend.click_policy="hide"
    
    return plot

def main():
    national_emissions = pd.read_excel('Results_summary1.xlsx', 'carbon_national', index_col=0)
    provincial_emissions = pd.read_excel('Results_summary1.xlsx', 'carbon_AP', index_col=0)
    plot = plot_line(national_emissions, provincial_emissions)
    output_file('plots/copper_emissions.html')
    save(plot)

if __name__ == '__main__':
    main()