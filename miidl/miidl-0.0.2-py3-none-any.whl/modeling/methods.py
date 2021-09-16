import sys
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

global W, C

class myDataset(Dataset):
    def __init__(self, dataset, labels):
        self.dataset = torch.tensor(dataset).type(torch.float32)
        self.labels = torch.tensor(labels)
    def __len__(self):
        return len(self.labels)
    def __getitem__(self, idx):
        data = self.dataset[idx]
        label = self.labels[idx]
        return data, label

class CNN(nn.Module):
    def __init__(self):
        super(CNN,self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=2, stride=1, padding=1
            ),                               #维度变换(1,28,28) --> (16,28,28)
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)      #维度变换(16,28,28) --> (16,14,14)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=2, stride=1, padding=1
            ),                               #维度变换(16,14,14) --> (32,14,14)
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)      #维度变换(32,14,14) --> (32,7,7)
        )
        W, C = self.get_params()
        self.fc1 = nn.Linear(int(32*W), int(8*W))
        self.fc2 = nn.Linear(int(8*W), int(C))

    def forward(self, x):
        out = self.conv1(x)                  #维度变换(Batch,1,28,28) --> (Batch,16,14,14)
        out = self.conv2(out)                #维度变换(Batch,16,14,14) --> (Batch,32,7,7)
        out = out.view(out.size(0),-1)       #维度变换(Batch,32,14,14) --> (Batch,32*14*14)||将其展平
        out = self.fc1(out)
        out = self.fc2(out)
        return out
    def get_params(self):
        global W, C
        return W, C

def default_model(width, c):
    global W, C
    W = (width/4)**2
    C = c
    model = CNN()
    print(model)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Using {} device".format(device))
    return model, loss_fn, optimizer, device

def train(dataloader, model, loss_fn, optimizer, device):
    size = len(dataloader.dataset)
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        
        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)
        
        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

def test(dataloader, model, loss_fn, device):
    size = len(dataloader.dataset)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= size
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

def default(X_train, y_train, X_test, y_test, width, C, epochs=5):
    train_dataloader = DataLoader(myDataset(X_train, y_train), batch_size=8, shuffle=True)
    test_dataloader = DataLoader(myDataset(X_test, y_test), batch_size=8, shuffle=True)
    model, loss_fn, optimizer, device = default_model(width, C)
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        train(train_dataloader, model, loss_fn, optimizer, device)
        test(test_dataloader, model, loss_fn, device)
    print("Done!")
    return model

# def custom(X_train, y_train, X_test, y_test):
#     print("[Modeling] Custom: Not available yet!")
#     model = None
#     return model 

def none(X_train=None, y_train=None, X_test=None, y_test=None, width=None, C=None, epochs=None):
    print("Exit!")
    sys.exit(0)