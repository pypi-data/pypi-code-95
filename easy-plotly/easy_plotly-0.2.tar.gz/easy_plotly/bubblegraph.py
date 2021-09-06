from easy_plotly.graph import Graph
import plotly.graph_objects as go


class BubbleGraph(Graph):
    """
    Bubble Chart
    """

    def __init__(self):
        Graph.__init__(self)

    def add_trace(self, X, Y, color, name, size=30):
        self.X = X
        self.Y = Y
        self.color = color
        self.name = name
        self.size = size
        self.fig.add_trace(go.Scatter(x=self.X, y=self.Y, mode="markers", marker_size=self.size))
