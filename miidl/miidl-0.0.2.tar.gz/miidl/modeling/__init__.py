import miidl
from .methods import default, none

def buildmodel(X_train=None, y_train=None, X_test=None, y_test=None, method='default', width=None, C=None, epochs=5):
    return getattr(miidl.modeling, method)(X_train, y_train, X_test, y_test, width, C, epochs)

call = {
    'default': default, 
    # 'custom': custom, 
    'none': none
}