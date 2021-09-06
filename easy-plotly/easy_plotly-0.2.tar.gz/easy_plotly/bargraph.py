from easy_plotly.graph import Graph
import plotly.graph_objects as go


class BarGraph(Graph):
    """
    Bar Graph class
    """

    def __init__(self):
        Graph.__init__(self)

    def add_trace(self, X, Y, color, name):
        """
        Adds trace to the plot

        Attributes:
            X: (pandas.Series) with X-axis values
            Y: (pandas.Series) with Y-axis values
            color: (string)
            name: (string)
            width: (int)
        """

        self.X = X
        self.Y = Y
        self.color = color
        self.name = name
        self.fig.add_trace(go.Bar(x=self.X, y=self.Y, name=self.name, marker_color=self.color))

    def update_layout(self, title, x_title="", y_title="", x_suffix="", y_suffix="",
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      barmode="group"):
        """
        Updates layout

        Attributes:
            title (string): Title of the chart
            x_title (string): X-axis label
            y_title (string): Y-axis label
            x_suffix (string): X-axis suffix, e.g. %
            y_suffix (string): Y-axis suffix, e.g. %
            paper_bgcolor (string): Sets the color of paper where the graph is drawn, e.g. "white"
            plot_bgcolor (string): Sets the background color of plotly area, e.g. "white"
            barmode: Type of bar chart e.g. "group"
        """

        # Initiate attributes from parent class
        Graph.update_layout(self, title, x_title, y_title, x_suffix, y_suffix, paper_bgcolor,
                            plot_bgcolor)

        # set the barmode of the graph
        self.barmode = barmode

        # Update using bargrouph
        self.fig.update_layout(barmode=self.barmode)