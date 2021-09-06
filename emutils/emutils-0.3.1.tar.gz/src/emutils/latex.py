import matplotlib.pyplot as plt


# %%
def activate_latex(size=13):
    plt.rcParams.update(
        {
            "text.usetex": True,
            "text.latex.preamble": r"\usepackage{amsmath}\usepackage{bm}\usepackage{amssymb}",
            "font.sans-serif": ["Helvetica", "Avant Garde", "Computer Modern Sans Serif"],
            "font.serif": ["Bookman", "Computer Modern Roman", "Times"],
            "font.family": "serif",
            'font.size': size,
            "legend.labelspacing": .1,
        }
    )


def bold(s, latex):
    if latex:
        return '\\textbf{' + s + '}'
    else:
        return s


def percentage_sign(latex):
    if latex:
        return '\%'
    else:
        return '%'


def serif(s, latex):
    if latex:
        return '\\emph{' + s + '}'
    else:
        return s


def equation(s, latex):
    if latex:
        return '$' + s + '$'
    else:
        return s


# %%
