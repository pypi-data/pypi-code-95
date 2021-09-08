# Import(s)
from importlib import reload
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

# Project import(s)
#from .theme import style

# Decorators


def defer(func):
    def wrapper(self, *args, **kwargs):
        plt.figure(self._base.number)
        method = getattr(plt, func.__name__)
        self._try_style()
        return method(*args, **kwargs)
    return wrapper


def cd(func):
    def wrapper(self, *args, **kwargs):
        plt.figure(self._base.number)
        return func(self, *args, **kwargs)
    return wrapper


# Class definition
class figure:

    # Constructor
    def __init__(self, dark=False, despine=0):

        # Member variables
        self._dark = dark
        self._despine = despine  # @TODO: axis label padding not workign properly with despine
        reload(style.theme)
        if self._dark:
            self._make_dark()
            pass
        reload(plt)
        self._base = plt.figure(facecolor=style.base if self._dark else None)

        # State
        self._styled = False

        return

    # Custom, public methods
    def ax(self):
        try:
            return self._base.axes[0]
        except IndexError:
            # Axes have not been defined yet
            pass
        return None

    def logo(self, alpha=1.):
        if not self.ax():
            print("[WARNING] logo: Axes not defined yet.")
            return
        box = self.ax().get_position()
        inset = self._base.add_axes([box.x0, box.y0 + box.height + 0.022, box.width,
                                    box.height * 0.09], anchor='NE', frameon=False, xticks=[], yticks=[])
        inset.imshow(
            style.images['normal' if self._dark else 'inverted'], interpolation='none', alpha=alpha)
        return

    # Specialised, deferred methods

    @cd
    def title(self, *args, **kwargs):
        # Set defaults
        defaults = {
            'ha': 'left',
            'va': 'bottom',
            'x': 0.00,
            'y': 1.02,
            'fontdict': {'family': 'serif', 'weight': 'bold', 'size': 14, "color": 'white' if self._dark else style.base}
        }
        kwargs = dict(defaults, **kwargs)

        # Call base method
        return plt.title(*args, **kwargs)

    @cd
    def xlabel(self, *labels, linesep=0.07, offset=-0.15):
        # Check(s)
        labels = self._check_labels(labels)

        # Resize the figure to make room for the labels
        self._add_padding(bottom=(len(labels) - 1) * linesep)

        # Manually draw x-axis label(s) as text
        ax = self.ax()
        despine_offset = self._despine / float(self._base.bbox.ymax)
        for ix, line in enumerate(labels):
            ax.text(1, offset - ix * linesep - despine_offset, line, color='gray' if ix else (
                'white' if self._dark else '.15'), transform=ax.transAxes, ha='right', weight=None if ix else 'semibold')
            pass
        return

    @cd
    def ylabel(self, *labels, linesep=0.0425, offset=-0.09):
        # Check(s)
        labels = self._check_labels(labels)

        # Resize the figure to make room for the labels
        self._add_padding(left=(len(labels) - 1) * linesep)

        # Manually draw y-axis label(s) as text
        ax = self.ax()
        despine_offset = self._despine / float(self._base.bbox.ymax)
        for ix, line in enumerate(labels):
            ax.text(offset - (len(labels) - ix - 1) * linesep - despine_offset, 1, line, color='gray' if ix else ('white' if self._dark else '.15'),
                    transform=ax.transAxes, ha='right', weight=None if ix else 'semibold', rotation=90., rotation_mode='anchor')
            pass
        return

    @cd
    def legend(self, *args, ax=None, **kwargs):
        # Set defaults
        defaults = {
            'loc': 'center left',
            'bbox_to_anchor': (1, 0.5),
            'prop': {'weight': 'semibold'}
        }
        kwargs = dict(defaults, **kwargs)

        ax = ax or self.ax()
        assert ax

        if ax.get_legend_handles_labels()[0]:

            # Resize the figure to make room for legend outsize
            self._add_padding(ax=ax, right=0.2)

            # Put a legend to the right of the current axis
            return ax.legend(**kwargs)
        else:
            print("[WARNING] legend: No legend entries found.")
            pass
        return

    # Deferred methods

    @defer
    def plot(self, *args, **kwargs): return

    @defer
    def errorbar(self, *args, **kwargs): return

    @defer
    def hist(self, *args, **kwargs): return

    @defer
    def bar(self, *args, **kwargs): return

    @defer
    def fill_between(self, *args, **kwargs): return

    @defer
    def scatter(self, *args, **kwargs): return

    @defer
    def text(self, *args, **kwargs): return

    @defer
    def axhline(self, *args, **kwargs): return

    @defer
    def axvline(self, *args, **kwargs): return

    @defer
    def xlim(self, *args, **kwargs): return

    @defer
    def ylim(self, *args, **kwargs): return

    @defer
    def xticks(self, *args, **kwargs): return

    @defer
    def yticks(self, *args, **kwargs): return

    @defer
    def show(self, *args, **kwargs): return

    @defer
    def gcf(self, *args, **kwargs): return

    @defer
    def savefig(self, *args, **kwargs): return

    # Internal methods

    def _make_dark(self):
        mpl.rcParams['axes.labelcolor'] = 'white'
        mpl.rcParams['axes.edgecolor'] = 'white'
        mpl.rcParams['xtick.color'] = 'white'
        mpl.rcParams['ytick.color'] = 'white'
        mpl.rcParams['text.color'] = 'white'
        mpl.rcParams['axes.prop_cycle'] = mpl.cycler(
            color=['white'] + style.colours[1:])
        return

    def _add_padding(self, top=0, bottom=0, left=0, right=0, ax=None):
        ax = ax or self.ax()

        horizontal = left + right
        vertical = top + bottom

        # Resize the figure to make room for legend outsize
        w, h = self._base.get_size_inches()
        self._base.set_size_inches(w / (1. - horizontal), h / (1. - vertical))

        # Shrink current axis by `reduction`
        box = ax.get_position()
        ax.set_position([box.x0 + box.width * left,
                         box.y0 + box.height * bottom,
                         box.width * (1 - horizontal),
                         box.height * (1. - vertical)])
        return

    def _check_labels(self, labels):
        assert isinstance(labels, (list, tuple))
        if len(labels) == 1:
            label = labels[0]
            if isinstance(label, (list, tuple)):
                labels = label
            else:
                assert isinstance(label, str)
                labels = [f.strip() for f in label.split('\n')]
                pass
            pass
        return labels

    def _try_style(self):
        if self._styled:
            return
        if not self.ax():
            return
        self._style()
        self._styled = True
        return

    def _style(self):
        ax = self.ax()
        assert ax
        ax.xaxis.get_major_locator().set_params(nbins=5, steps=[1, 2, 5, 10])
        ax.yaxis.get_major_locator().set_params(nbins=5, steps=[1, 2, 5, 10])
        if self._dark:
            ax.set_facecolor(style.base)
            pass
        sns.despine(offset=self._despine)
        return
    pass
