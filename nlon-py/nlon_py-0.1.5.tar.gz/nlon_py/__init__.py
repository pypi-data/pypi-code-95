"""Top-level package for nlon-py."""

__author__ = """Jianwen Xu"""
__email__ = 'xujianwen37@gmail.com'
__version__ = '0.1.5'

from nlon_py.data.build_model import (buildDefaultData, buildDefaultModel,
                                      compareDifModels, loadDefaultData,
                                      plot_cm, plot_model_roc,
                                      plotDistribution, searchParams,
                                      testDefaultModel, validDefaultModel)

# from nlon_py.data.make_data import plotDistribution
# buildDefaultModel(n_classes=5)
# buildDefaultModel(n_classes=5, features='C3', stand=False)
# buildDefaultModel(n_classes=5, features='FE', kbest=False)
# buildDefaultModel(n_classes=5,features='C3_FE', kbest=False)
# buildDefaultModel(n_classes=5,features='C3_FE', kbest=True)
# buildDefaultModel(n_classes=5,features='C3_FE', stand=False)
# testDefaultModel()
# validDefaultModel()
# compareDifModels(n_classes=5)
# buildDefaultData()
# loadDefaultData(n_class=2)
# plotDistribution(n_classes=5)
# searchParams(n_classes=5)
# plot_model_roc(n_classes=5)
# plot_cm()
