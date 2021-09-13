import torch

class LSTM(torch.nn.Module):
    def __init__(self, input_size=4, hidden_size=10,
                 num_layers=2, output_size=2):
        super(LSTM, self).__init__()
        self.lstm = torch.nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=False,
            bias=False)
        self.fc = torch.nn.Linear(hidden_size, output_size)

    def forward(self, x, state=None):
        x, state = self.lstm(x, state)
        x = self.fc(x)
        return x, state
