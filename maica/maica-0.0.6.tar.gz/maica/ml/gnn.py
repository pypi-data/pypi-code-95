"""
Graph Neural Networks
---------------------
The ``maica.ml.gnn`` module includes various implementation of graph neural networks from the torch_geometric library.
It provides pre-defined graph neural networks for the structure-based predictions.
"""

import numpy
import torch
import torch_geometric
import torch.nn as nn
import torch.nn.functional as F
import maica.core.sys as sys
import maica.core.env as env
from torch_geometric.nn import LayerNorm
from torch_geometric.nn import GCNConv
from torch_geometric.nn import GATConv
from torch_geometric.nn import GINConv
from torch_geometric.nn import CGConv
from torch_geometric.nn import global_mean_pool
from torch_geometric.nn import global_add_pool
from maica.ml.base import PyTorchModel


class GNN(PyTorchModel):
    """
        Abstract class of the graph neural networks.
        It defines two functions for parameter optimization and prediction.
    """

    def __init__(self,
                 dim_out: int,
                 alg_name: str):
        super(GNN, self).__init__(alg_name)
        self.dim_out = dim_out

    def fit(self,
            data_loader: torch_geometric.data.DataLoader,
            optimizer: torch.optim.Optimizer,
            criterion: object):
        """
        Fit the model parameters for the given dataset in the data loader, optimizer, and loss function.
        It iterates the parameter optimization once for the entire dataset.

        :param data_loader: (torch_geometric.data.DataLoader) A data loader to sample the data from the training dataset.
        :param optimizer: (torch.optim.Optimizer) An optimizer to fit the model parameters.
        :param criterion: (object) A loss function to evaluate the prediction performance of the model.
        :return: Training loss.
        """

        self.train()
        sum_losses = 0

        for batch in data_loader:
            if sys.run_gpu:
                for b in batch:
                    b.x = b.x.cuda()
                    b.y = b.y.cuda()
                    b.edge_index = b.edge_index.cuda()
                    b.batch = b.batch.cuda()
                    b.edge_attr = None if b.edge_attr is None else b.edge_attr.cuda()

            preds = self(batch)
            loss = criterion(batch[0].y, preds)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            sum_losses += loss.detach().item()

        return sum_losses / len(data_loader)

    def predict(self,
                data_loader: torch_geometric.data.DataLoader):
        """
        Predict target values for the given dataset in the data loader.

        :param data_loader: (torch_geometric.data.DataLoader) A data loader to sample the data from the dataset.
        :return: A NumPy array containing the predicted values.
        """

        self.eval()
        list_preds = list()

        with torch.no_grad():
            for batch in data_loader:
                if sys.run_gpu:
                    for b in batch:
                        b.x = b.x.cuda()
                        b.y = b.y.cuda()
                        b.edge_index = b.edge_index.cuda()
                        b.batch = b.batch.cuda()
                        b.edge_attr = None if b.edge_attr is None else b.edge_attr.cuda()

                if sys.run_gpu:
                    list_preds.append(self(batch).cpu().numpy())
                else:
                    list_preds.append(self(batch).numpy())

        return numpy.vstack(list_preds).flatten()


# Thomas N. Kipf and Max Welling
# Semi-Supervised Classification with Graph Convolutional Networks
# International Conference on Learning Representations (ICLR) 2017
class GCN(GNN):
    """
    Graph convolutional network (GCN) form the `"Semi-supervised Classification with Graph Convolutional Networks"
    <https://arxiv.org/abs/1609.02907>`_ paper.
    """

    def __init__(self,
                 n_node_feats: int,
                 dim_out: int,
                 n_graphs: int = 1,
                 readout: str = env.READOUT_MEAN):
        super(GCN, self).__init__(dim_out, env.ALG_GCN)
        self.n_graphs = n_graphs
        self.readout = readout
        self.gc1 = GCNConv(n_node_feats, 256)
        self.gn1 = LayerNorm(256)
        self.gc2 = GCNConv(256, 256)
        self.gn2 = LayerNorm(256)
        self.gc3 = GCNConv(256, 256)
        self.gn3 = LayerNorm(256)
        self.fc1 = nn.Linear(self.n_graphs * 256, 32)
        self.fc2 = nn.Linear(32, dim_out)

    def __emb_nodes(self,
                    g: torch_geometric.data.Batch):
        """
        Generate node embeddings using the graph convolutional layers.

        :param g: (torch_geometric.data.Batch) An input Batch object of the torch_geometric.data.Data objects.
        :return: Node embeddings.
        """

        h = F.relu(self.gn1(self.gc1(g.x, g.edge_index)))
        h = F.relu(self.gn2(self.gc2(h, g.edge_index)))
        h = F.relu(self.gn3(self.gc3(h, g.edge_index)))

        return h

    def forward(self,
                g: torch_geometric.data.Batch):
        """
        Predict target values for the given Batch object.

        :param g: (torch_geometric.data.Batch) An input Batch object of the torch_geometric.data.Data objects.
        :return: Target values.
        """

        if self.readout == env.READOUT_MEAN:
            hg = torch.cat([global_mean_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)
        elif self.readout == env.READOUT_SUM:
            hg = torch.cat([global_add_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)

        hg = F.relu(self.fc1(hg))
        out = self.fc2(hg)

        return out


# Petar Velickovic, Guillem Cucurull, Arantxa Casanova, Adriana Romero, Pietro Lio, and Yoshua Bengio,
# Graph Attention Networks,
# International Conference on Learning Representations (ICLR) 2018
class GAT(GNN):
    """
    Graph attention network (GAT) form the `"Graph Attention Networks"
    <https://arxiv.org/abs/1710.10903>`_ paper.
    """

    def __init__(self,
                 n_node_feats: int,
                 dim_out: int,
                 n_graphs: int = 1,
                 readout: str = env.READOUT_MEAN):
        super(GAT, self).__init__(dim_out, env.ALG_GAT)
        self.n_graphs = n_graphs
        self.readout = readout
        self.gc1 = GATConv(n_node_feats, 256)
        self.gn1 = LayerNorm(256)
        self.gc2 = GATConv(256, 256)
        self.gn2 = LayerNorm(256)
        self.gc3 = GATConv(256, 256)
        self.gn3 = LayerNorm(256)
        self.fc1 = nn.Linear(self.n_graphs * 256, 32)
        self.fc2 = nn.Linear(32, dim_out)

    def __emb_nodes(self,
                    g: torch_geometric.data.Batch):
        """
        Generate node embeddings using the graph convolutional layers.

        :param g: (torch_geometric.data.Batch) An input Batch object of the torch_geometric.data.Data objects.
        :return: Node embeddings.
        """

        h = F.relu(self.gn1(self.gc1(g.x, g.edge_index)))
        h = F.relu(self.gn2(self.gc2(h, g.edge_index)))
        h = F.relu(self.gn3(self.gc3(h, g.edge_index)))

        return h

    def forward(self,
                g: torch_geometric.data.Batch):
        """
        Predict target values for the given Batch object.

        :param g: (torch_geometric.data.Batch) An input Batch object of the torch_geometric.data.Data objects.
        :return: Target values.
        """

        if self.readout == env.READOUT_MEAN:
            hg = torch.cat([global_mean_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)
        elif self.readout == env.READOUT_SUM:
            hg = torch.cat([global_add_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)

        hg = F.relu(self.fc1(hg))
        out = self.fc2(hg)

        return out


# Keyulu Xu, Weihua Hu, Jure Leskovec, and Stefanie Jegelka,
# How Powerful are Graph Neural Networks?,
# International Conference on Learning Representations (ICLR) 2019
class GIN(GNN):
    """
    Graph isomorphism network (GIN) form the `"How Powerful are Graph Neural Networks?"
    <https://arxiv.org/abs/1810.00826>`_ paper.
    """

    def __init__(self,
                 n_node_feats: int,
                 dim_out: int,
                 n_graphs: int = 1,
                 readout: str = env.READOUT_MEAN):
        super(GIN, self).__init__(dim_out, env.ALG_GIN)
        self.n_graphs = n_graphs
        self.readout = readout
        self.gc1 = GINConv(nn.Linear(n_node_feats, 256))
        self.gn1 = LayerNorm(256)
        self.gc2 = GINConv(nn.Linear(256, 256))
        self.gn2 = LayerNorm(256)
        self.gc3 = GINConv(nn.Linear(256, 256))
        self.gn3 = LayerNorm(256)
        self.fc1 = nn.Linear(self.n_graphs * 256, 32)
        self.fc2 = nn.Linear(32, dim_out)

    def __emb_nodes(self,
                    g: torch_geometric.data.Batch):
        """
        Generate node embeddings using the graph convolutional layers.

        :param g: (torch_geometric.data.Batch) An input Batch object of the torch_geometric.data.Data objects.
        :return: Node embeddings.
        """
        h = F.relu(self.gn1(self.gc1(g.x, g.edge_index)))
        h = F.relu(self.gn2(self.gc2(h, g.edge_index)))
        h = F.relu(self.gn3(self.gc3(h, g.edge_index)))

        return h

    def forward(self,
                g: torch_geometric.data.Batch):
        """
        Predict target values for the given Batch object.

        :param g: (torch_geometric.data.Batch) An input Batch object of the torch_geometric.data.Data objects.
        :return: Target values.
        """

        if self.readout == env.READOUT_MEAN:
            hg = torch.cat([global_mean_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)
        elif self.readout == env.READOUT_SUM:
            hg = torch.cat([global_add_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)

        hg = F.relu(self.fc1(hg))
        out = self.fc2(hg)

        return out


# Tian Xie and Jeffrey C. Grossman
# Crystal Graph Convolutional Neural Networks for an Accurate and Interpretable Prediction of Material Properties
# Physical Review Letters, 120, 145301
class CGCNN(GNN):
    """
    Crystal graph convolutional neural network (CGCNN) form the `"Crystal Graph Convolutional Neural Networks for an
    Accurate and Interpretable Prediction of Material Properties"
    <https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.120.145301>`_ paper.
    """

    def __init__(self,
                 n_node_feats: int,
                 n_edge_feats: int,
                 dim_out: int,
                 n_graphs: int = 1,
                 readout: str = env.READOUT_MEAN):
        super(CGCNN, self).__init__(dim_out, env.ALG_CGCNN)
        self.n_graphs = n_graphs
        self.readout = readout
        self.fc1 = nn.Linear(n_node_feats, 256)
        self.gc1 = CGConv(256, n_edge_feats)
        self.gn1 = LayerNorm(256)
        self.gc2 = CGConv(256, n_edge_feats)
        self.gn2 = LayerNorm(256)
        self.gc3 = CGConv(256, n_edge_feats)
        self.gn3 = LayerNorm(256)
        self.fc2 = nn.Linear(self.n_graphs * 256, 32)
        self.fc3 = nn.Linear(32, dim_out)

    def __emb_nodes(self,
                    g: torch_geometric.data.Batch):
        """
        Generate node embeddings using the graph convolutional layers.

        :param g: (torch_geometric.data.Batch) An input Batch object of the torch_geometric.data.Data objects.
        :return: Node embeddings.
        """
        h = F.relu(self.fc1(g.x))
        h = F.relu(self.gn1(self.gc1(h, g.edge_index, g.edge_attr)))
        h = F.relu(self.gn2(self.gc2(h, g.edge_index, g.edge_attr)))
        h = F.relu(self.gn3(self.gc3(h, g.edge_index, g.edge_attr)))

        return h

    def forward(self,
                g: torch_geometric.data.Batch):
        """
        Predict target values for the given Batch object.

        :param g: (torch_geometric.data.Batch) An input Batch object of the torch_geometric.data.Data objects.
        :return: Target values.
        """

        if self.readout == env.READOUT_MEAN:
            hg = torch.cat([global_mean_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)
        elif self.readout == env.READOUT_SUM:
            hg = torch.cat([global_add_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)

        hg = F.relu(self.fc2(hg))
        out = self.fc3(hg)

        return out
