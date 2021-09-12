import numpy
import torch
import torch.nn.functional as F
from torch.utils.data import TensorDataset


def train_emb_net(emb_net, data_loader, optimizer, max_epoch):
    if isinstance(data_loader.dataset, TensorDataset):
        for i in range(0, max_epoch):
            train_loss = __train_vec(emb_net, data_loader, optimizer)
            print('Epoch [{}/{}]\tTrain loss: {:.4f}'.format(i + 1, max_epoch, train_loss))
    elif isinstance(data_loader.dataset, list):
        for i in range(0, max_epoch):
            print('graph')
            train_loss = __train_graph(emb_net, data_loader, optimizer)
            print('Epoch [{}/{}]\tTrain loss: {:.4f}'.format(i + 1, max_epoch, train_loss))
    return None


def __train_vec(emb_net, data_loader, optimizer):
    emb_net.train()
    train_loss = 0

    for data, targets in data_loader:
        data = data.cuda()
        targets = targets.cuda()

        rand_idx = torch.randperm(data.shape[0])
        inputs_sample = data[rand_idx, :]
        targets_sample = targets[rand_idx, :]

        emb_data = F.normalize(emb_net(data), p=2, dim=1)
        emb_sample = F.normalize(emb_net(inputs_sample), p=2, dim=1)

        dist_emb = torch.sum((emb_data - emb_sample)**2, dim=1)
        dist_target = torch.sum((targets - targets_sample)**2, dim=1)
        loss = torch.mean((dist_emb - dist_target)**2)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    return train_loss / len(data_loader)


def __train_graph():
    return None


def test(emb_net, data_loader):
    emb_net.eval()
    list_embs = list()

    with torch.no_grad():
        for data, _ in data_loader:
            data = data.cuda()

            embs = F.normalize(emb_net(data), p=2, dim=1)
            list_embs.append(embs.cpu().numpy())

    return numpy.vstack(list_embs)
