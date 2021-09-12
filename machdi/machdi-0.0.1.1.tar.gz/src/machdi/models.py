import warnings
from matplotlib.pyplot import cla
import numpy as np
from machdi import errors as e
from machdi import preprocessing as prc

warnings.filterwarnings(action='ignore')
#########################################################################################################
def activation_function(z,kind):
    
    if kind == 'relu':
        return np.maximum(0,z)

    elif kind == 'leaky-relu':
        z[z<=0] = .001 * z
        z[z>0] = z
        return z
    
    elif kind =='sigmoid':
        return 1 / (1 + np.exp(-z))
    
    elif kind == 'softMax':
        return np.exp(z) / np.sum(np.exp(z),axis=1,keepdims=True)
    
    elif kind =='tanh':
        return np.tanh(z)
    
    elif kind == 'linear':
        return z
    else:
        raise ValueError(f'{kind} not supported.')

def drivative_activation_function(z,kind):

    if kind == 'relu':
        z[z<=0] = 0
        z[z>0] = 1
        return z

    if kind == 'leaky-relu':
        z[z<=0] = .001
        z[z>0] = 1
        return z
    
    elif kind =='sigmoid':
        s = activation_function(z,'sigmoid')
        return s * (1 - s)
    
    elif kind == 'softMax':
        s = activation_function(z,'softmax').reshape(-1,1)
        return np.diagflat(s) - np.dot(s, s.T)
        #thanks https://aerinykim.medium.com/how-to-implement-the-softmax-derivative-independently-from-any-loss-function-ae6d44363a9d
    
    elif kind =='tanh':
        return 1 - (np.tanh(z) ** 2) 
    
    else:
        return z
#########################################################################################################

class _LinearModels():

    def __init__(self, penalty='L2',alpha=0, include_bias=False,lr=.001,train_type='batch',n_reports=0,maxIter=100,converLim=.001,n_converLim = 1):

        self.penalty = penalty
        self.alpha = alpha
        self.include_bias = include_bias
        self.lr = lr
        self.train_type = train_type
        self.n_reports = n_reports
        self.maxIter = maxIter
        self.converLim = converLim
        self.n_converLim = n_converLim

    @staticmethod
    def _check_weights(w,b,shape):

        if w.ndim != 2:
            raise ValueError('only 2 dimensions arrays allowed')
        if w is None:
            b = np.ones((shape[1],))
            w = np.ones(shape=shape)
        return w,b

    @classmethod
    def score(cls, x, w=None, bias=None, degree = 1):
        #x = prc.polynomial(x, degree=degree,bias = False)
        return  np.dot(x , w) + bias

    @staticmethod
    def regularization(w,kind='L2',alpha=0.,jac=False):
        if kind =='L2':
            # second approach is : return self.alpha * np.sum(np.square(w))
            if not jac:
                return alpha * (w.T @ w)[0,0]
            return alpha * w
        elif kind =='L1':
            return alpha * np.sum(np.abs(w))
        else:
            raise ValueError("regularization must be L1 or L2")

class Optimization:

    def GD(self,x,y,plot_j):
        '''
        Gradient descent algorithm .
        Returns
        -------
        ndarray, int
        optimum weights matrix, loss of new weights.
        '''
        # variables
        costs = []
        iterNum = 1
        self.bias = 0
        self.weight = np.ones((x.shape[1],y.shape[1]))
        if self.include_bias:
            self.bias = np.ones((x.shape[1],)).reshape(-1,1)
        
        # conditions
        if self.train_type != 'batch':
            if self.train_type == 'stochastic':
                idx = np.random.randint(len(x), size=1)
            elif self.train_type == 'mini-batch':
                idx = np.random.randint(len(x), size=int(.3 * len(x)))
            else:
                raise ValueError('''invalid value for parameter : "Type"''')

        # other conditions:
        if self.lr < 0:
            raise ValueError('Learning rate must be greater than 0')
        if self.n_reports > self.maxIter:
            raise ValueError('verbose must be smaller than maxIter')
        # functions
        def weight_grad(x,y,p): return 1/len(x) * np.dot(x.T, (p-y))
        def bias_grad(y,p) : return np.average(p - y) 
        def choose_random(x, y, idx): return (x[idx], y[idx])

        # starting the algorithm
        while iterNum != self.maxIter+1:

            X,Y = x,y
            if self.train_type != 'batch':
                X, Y = choose_random(x= x, y=y, idx=idx)
            
            p = self.predict(X)
            self.bias -= self.lr * bias_grad(Y,p)
            self.weight -= self.lr * weight_grad(X,Y,p)
            costs.append(self.loss(p,Y,self.weight))
        
            if self.n_reports>0:
                print('\nEpoch{0} | loss : {1:.4f}\n'.format(
                    iterNum, (costs[-1])))
                self.n_reports -=1
            ##########################################################
            iterNum += 1
            counter=0
            try:
                for i in range(self.n_converLim):
                    if abs(costs[-1] - costs[-2]) < self.converLim:
                        counter +=1
                if counter == self.n_converLim:
                    print('End of the algorithm at iteration number {}.\nThe differences in costs is less than {}'.format(
                        iterNum, self.converLim))
                    break
            except IndexError:
                pass
        if plot_j:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10,10))
            plt.scatter(range(1,iterNum),costs, color='red')
            plt.xlabel('iteration number')
            plt.ylabel('cost')
            plt.show()
        return self.bias,self.weight
    
        
class LinearRegressor(_LinearModels,Optimization):
    '''
    "LinearRegression"
    
    parameters
    ----------
    alpha : float , optional
        regularization hyper parameter.
    penalty : str , optional
        order : {'L1','L2'}
        regularization technique.
    included_bias : boolean , optional
        if True, then bias is attached to weight matrix. if not, bias will set to 0.
    '''

    def __init__(self, penalty='L2' ,alpha=0, include_bias=False,train_type=None,lr=.001,n_reports=0,maxIter=100, converLim=.001,n_converLim=1):
        super().__init__(penalty=penalty, alpha=alpha, include_bias=include_bias,train_type=train_type,lr=lr,n_reports=n_reports,maxIter=maxIter,converLim=converLim,n_converLim=n_converLim)
        self.activ = 'linear'

    def loss(self,p, y,w=None,vectorized = True):
        
        dls = np.average((np.square(p - y)))
        if vectorized :
            dloss =  1/len(y) * ((p - y).T @ (p - y))[0, 0]
        if self.penalty is not None:
            rls = super().regularization(w,kind=self.penalty)
        return dls
    
    def predict(self,x):
        return activation_function(super().score(x=x, w=self.weight, bias=self.bias),kind=self.activ)

    def train(self,x,y,plot_j=False):
        return self.GD(x=x,y=y,plot_j = plot_j) 

    def plot_loss(self):

        self.plot_j()





class LogisticRegression(_LinearModels,Optimization):

    def __init__(self, penalty='L2' ,alpha=0, include_bias=False,train_type=None,lr=.001,n_reports=0,maxIter=100, converLim=.001,n_converLim=1,activation='sigmoid'):
        super().__init__(penalty=penalty, alpha=alpha, include_bias=include_bias,train_type=train_type,lr=lr,n_reports=n_reports,maxIter=maxIter,converLim=converLim,n_converLim=n_converLim)
        self.activ = activation
        if self.activ not in ['sigmoid','softmax']:
            raise ValueError('invalid activation function.')

    def loss(self,p, y, vectorized = True):
        if len(list(np.unique(y))) == 2:
            return np.average( (-y *np.log(p))-(( 1-y )*np.log(1 - p)))
        else:
            return np.average( -y * np.log(p))

    def predict(self,x,return_classLabel=True):
        p =  activation_function(super().score(x=x, w=self.weight, bias=self.bias),kind=self.activ)
        if not return_classLabel:
            return p
        return np.argmax(p,axis = 1)

    def train(self,x,y):
        self.GD(x=x,y=y)

    def plot_loss(self):
        self.plot_j()