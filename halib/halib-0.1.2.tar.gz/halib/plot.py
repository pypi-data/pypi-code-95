import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib


def save_fig_latex_pgf(filename, directory='.'):
    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })
    if '.pgf' not in filename:
        filename = f'{directory}/{filename}.pgf'
    plt.savefig(filename)
