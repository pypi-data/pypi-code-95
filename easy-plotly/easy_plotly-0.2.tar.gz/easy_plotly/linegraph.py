from easy_plotly.graph import Graph
import plotly.graph_objects as go

class LineGraph(Graph):
    """
    Line Graph class
    """

    def __init__(self):
        Graph.__init__(self)

    def add_trace(self, X, Y, color, name, width):
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
        self.width = width
        self.fig.add_trace(go.Scatter(x=self.X, y=self.Y,
                                      mode="lines", line=dict(color=self.color,
                                                              width=self.width), name=self.name))




