from easy_plotly.linegraph import LineGraph
from easy_plotly.bargraph import BarGraph
from easy_plotly.bubblegraph import BubbleGraph
import pandas as pd

if __name__ == "__main__":

    # Import sample data
    df1 = pd.read_csv("sample_data.csv")

    # Line graph
    chart = LineGraph()
    chart.add_trace(df1['Date'], df1['Index1'], 'blue', 'Index1', 3)
    chart.add_trace(df1['Date'], df1['Index2'], 'red', 'Index2', 3)
    chart.add_trace(df1['Date'], df1['Index3'], 'green', 'Index3', 3)
    chart.update_layout(title="Line Chart", y_suffix="%")
    chart.show_chart()

    # Bar Chart
    df2 = df1.iloc[1:20]
    bar = BarGraph()
    bar.add_trace(X=df2['Date'], Y=df2['Index1'], name='Index1', color="blue")
    bar.add_trace(X=df2['Date'], Y=df2['Index2'], name='Index2', color="red")
    bar.add_trace(X=df2['Date'], Y=df2['Index3'], name='Index3', color="green")
    bar.update_layout(title="Bar Chart", y_suffix="%", barmode="stack")
    bar.show_chart()

    # Bubble Chart
    x = [1, 2, 3, 4]
    y = [10, 11, 12, 13]
    chart = BubbleGraph()
    chart.add_trace(x, y, "red", "bubbles")
    chart.update_layout(title="Bubble Chart", y_suffix="%", y_title="Return")
    chart.show_chart()
