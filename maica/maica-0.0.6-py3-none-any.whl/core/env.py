"""
Environment Variables
---------------------
This is a core module of MAICA that includes environment variables to define
prediction task, machine learning algorithm, and other algorithmic descriptors.
"""


# Data Formats
DATA_FORMAT_VEC = 'vec'         # Numerical Vector
DATA_FORMAT_IMG = 'img'         # Image Data
DATA_FORMAT_GRAPH = 'graph'     # Mathematical Graph


# Data Types
DATA_TYPE_VEC = 'vec'           # Numerical Vector
DATA_TYPE_FORM = 'form'         # Chemical Formula
DATA_TYPE_SMILES = 'smiles'     # Simplified Molecular-Input Line-Entry System (SMILES)
DATA_TYPE_CIF = 'cif'           # Crystallographic Information File


# Feature Types
FEAT_TYPE_NUM = 'num'           # Numerical Value
FEAT_TYPE_FORM = 'form'         # Chemical Formula
FEAT_TYPE_STRUCT = 'struct'     # Mathematical Graph


# Imputation Methods
IMPUTE_MEAN = 'mean'            # Fill empty value by mean.
IMPUTE_ZERO = 'zero'            # Fill empty value by zero.
IMPUTE_KNN = 'knn'              # Fill empty value by k-nearest neighbor data.


# Abbreviations of the Machine Learning Algorithms
ALG_SKLEARN = 'sklearn'         # Abstract Algorithm of Scikit-learn
ALG_PYTORCH = 'pytorch'         # Abstract Algorithm of PyTorch
ALG_LR = 'lr'                   # Linear Regression
ALG_LASSO = 'lasso'             # Lasso
ALG_DCTR = 'dctr'               # Decision Tree Regression
ALG_SYMR = 'symr'               # Symbolic Regression
ALG_KRR = 'krr'                 # Kernel Ridge Regression
ALG_KNNR = 'knnr'               # K-Nearest Neighbor Regression
ALG_SVR = 'svr'                 # Support Vector Regression
ALG_GPR = 'gpr'                 # Gaussian Process Regression
ALG_GBTR = 'gbtr'               # Gradient Boosting Tree Regression
ALG_FCNN = 'fcnn'               # Fully-Connected Neural Network
ALG_ATE = 'autoencoder'         # Autoencoder
ALG_DOPNET = 'dopnet'           # DopNet
ALG_GCN = 'gcn'                 # Graph Convolutional Network
ALG_GAT = 'gat'                 # Graph Attention Network
ALG_GIN = 'gin'                 # Graph Isomorphism Network
ALG_CGCNN = 'cgcnn'             # Crystal Graph Convolutional Neural Network


# Gradient-Based Optimizers
GD_SGD = 'sgd'                  # Stochastic Gradient Descent method
GD_ADADELTA = 'adadelta'        # AdaDelta Optimizer
GD_RMSPROP = 'rmsprop'          # Root Mean Square Propagation
GD_ADAM = 'adam'                # Adam Optimizer


# Loss Function
LOSS_MAE = 'mae'                # Mean Absolute Error
LOSS_MSE = 'mse'                # Mean Sqaured Error
Loss_SMAE = 'smae'              # Smooth Mean Absolute Error


# Readout Methods for Graph Neural Networks
READOUT_MEAN = 'mean'           # Mean-Based Readout
READOUT_SUM = 'add'             # Sum-Based Readout


# Manifold Learning Methods
EMB_TSNE = 'tsne'               # t-Distributed Stochastic Neighbor Embedding
EMB_SPECT = 'spect'             # Spectral Embedding


# Pipeline Types of the Machine Learning Algorithms
ALGS_SKLEARN = [ALG_SKLEARN, ALG_LR, ALG_LASSO, ALG_DCTR, ALG_SYMR, ALG_KRR, ALG_KNNR, ALG_SVR, ALG_GPR, ALG_GBTR]
ALGS_PYTORCH = [ALG_PYTORCH, ALG_FCNN, ALG_DOPNET, ALG_GCN, ALG_GAT, ALG_GIN, ALG_CGCNN]


# Optimization Types
PROB_MIN = 'min'                # Minimization Problem
PROB_MAX = 'max'                # Maximization Problem


# Abbreviations of Metaheuristic Algorithms
OPT_EP = 'ep'                   # Evolutionary Programming
OPT_ES = 'es'                   # Evolution Strategies
OPT_MA = 'ma'                   # Memetic Algorithm
OPT_GA = 'ga'                   # Genetic Algorithm
OPT_DE = 'de'                   # Differential Evolution
OPT_FPA = 'fpa'                 # Flower Pollination Algorithm
OPT_CRO = 'cro'                 # Coral Reefs Optimization
OPT_PSO = 'pso'                 # Particle Swarm Optimization
OPT_BFO = 'bfo'                 # Bacterial Foraging Optimization
OPT_BEES = 'bees'               # Bees Algorithm
OPT_CSO = 'cso'                 # Cat Swarm Optimization
OPT_ACO = 'aco'                 # Ant Colony Optimization
OPT_ABC = 'abc'                 # Artificial Bee Colony
OPT_CSA = 'csa'                 # Cuckoo Search Algorithm
OPT_FFA = 'ffa'                 # Firefly Algorithm
OPT_FA = 'fa'                   # Fireworks Algorithm
OPT_BA = 'ba'                   # Bat Algorithm
OPT_FOA = 'foa'                 # Fruit-fly Optimization Algorithm
OPT_SSO = 'sso'                 # Social Spider Optimization
OPT_GWO = 'gwo'                 # Grey Wolf Optimizer
OPT_SSA = 'ssa'                 # Social Spider Algorithm
OPT_ALO = 'alo'                 # Ant Lion Optimizer
OPT_MFO = 'mfo'                 # Moth Flame Optimization
OPT_EHO = 'eho'                 # Elephant Herding Optimization
OPT_JA = 'ja'                   # Jaya Algorithm
OPT_WOA = 'woa'                 # Whale Optimization Algorithm
OPT_DO = 'do'                   # Dragonfly Optimization
OPT_BSA = 'bsa'                 # Bird Swarm Algorithm
OPT_SHO = 'sho'                 # Spotted Hyena Optimizer
OPT_SALP = 'salp'               # Salp Swarm Opimization
OPT_SRSR = 'srsr'               # Swarm Robotics Search And Rescue
OPT_GOA = 'goa'                 # Grasshopper Optimization Algorithm
OPT_MSA = 'msa'                 # Moth Search Algorithm
OPT_SLO = 'slo'                 # Sea Lion Optimization
OPT_NMRA = 'nmra'               # Nake Mole-rat Algorithm
OPT_BES = 'bes'                 # Bald Eagle Search
OPT_PFA = 'pfa'                 # Pathfinder Algorithm
OPT_SFO = 'sfo'                 # Sailfish Optimizer
OPT_HHO = 'hho'                 # Harris Hawks Optimization
OPT_MRFO = 'mrfo'               # Manta Ray Foraging Optimization
OPT_SPA = 'spa'                 # Sparrow Search Algorithm
OPT_HGS = 'hgs'                 # Hunger Games Search
OPT_AO = 'ao'                   # Aquila Optimizer
OPT_SA = 'sa'                   # Simulated Annealing
OPT_WDO = 'wdo'                 # Wind Driven Optimization
OPT_MVO = 'mvo'                 # Multi-Verse Optimizer
OPT_TWO = 'two'                 # Tug of War Optimization
OPT_EFO = 'efo'                 # Electromagnetic Field Optimization
OPT_NRO = 'nro'                 # Nuclear Reaction Optimization
OPT_HGSO = 'hgso'               # Henry Gas Solubility Optimization
OPT_ASO = 'aso'                 # Atom Search Optimization
OPT_EO = 'eo'                   # Equilibrium Optimizer
OPT_ARCH = 'arch'               # Archimedes Optimization Algorithm
OPT_CA = 'ca'                   # Culture Algorithm
OPT_ICA = 'ica'                 # Imperialist Competitive Algorithm
OPT_TLO = 'tlo'                 # Teaching Learning Optimization
OPT_BSO = 'bso'                 # Brain Storm Optimization
OPT_QSA = 'qsa'                 # Queuing Search Algorithm
OPT_SARO = 'saro'               # Search And Rescue Optimization
OPT_LCBO = 'lcbo'               # Life Choice-Based Optimization
OPT_SSDO = 'ssdo'               # Social Ski-Driver Optimization
OPT_GSKA = 'gska'               # Gaining Sharing Knowledge-based Algorithm
OPT_CHIO = 'chio'               # Coronavirus Herd Immunity Optimization
OPT_FBIO = 'fbio'               # Forensic-Based Investigation Optimization
OPT_BRO = 'bro'                 # Battle Royale Optimization
OPT_IWO = 'iwo'                 # Invasive Weed Optimization
OPT_BBO = 'bbo'                 # Biogeography-Based Optimization
OPT_VCS = 'vcs'                 # Virus Colony Search
OPT_SBO = 'sbo'                 # Satin Bowerbird Optimizer
OPT_EOA = 'eoa'                 # Earthworm Optimisation Algorithm
OPT_WHO = 'who'                 # Wildebeest Herd Optimization
OPT_SMA = 'sma'                 # Slime Mould Algorithm
OPT_GCO = 'gco'                 # Germinal Center Optimization
OPT_WCA = 'wca'                 # Water Cycle Algorithm
OPT_AEO = 'aeo'                 # Artificial Ecosystem-based Optimization
OPT_HC = 'hc'                   # Hill Climbing
OPT_SCA = 'sca'                 # Sine Cosine Algorithm
OPT_AOA = 'aoa'                 # Arithmetic Optimization Algorithm
OPT_HS = 'hs'                   # Harmony Search
OPT_CEM = 'cem'                 # Cross-Entropy Method
OPT_PIO = 'pio'                 # Pigeon-Inspired Optimization
OPT_AAA = 'aaa'                 # Artificial Algae Algorithm
OPT_RHO = 'rho'                 # Rhino Herd Optimization
OPT_EPO = 'epo'                 # Emperor Penguin Optimizer
OPT_BOA = 'boa'                 # Butterfly Optimization Algorithm
OPT_BMO = 'bmo'                 # Blue Monkey Optimization
OPT_SOA = 'soa'                 # Sandpiper Optimization Algorithm
OPT_BWO = 'bwo'                 # Black Widow Optimization
