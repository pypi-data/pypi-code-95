from transformer_layers import *
import torch.nn as nn


class ShuffleFormer(nn.Module):
    def __init__(self, n_vocab, depth, hidden_dim, seq_len, shuffle_dim, heads, n_buckets):
        super().__init__()
        self.embedding = nn.Embedding(n_vocab, hidden_dim)
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers += [ShuffleFormerLayer(seq_len, hidden_dim, shuffle_dim, heads, n_buckets)]
            self.layers += [FeedforwardLayer(hidden_dim)]

    def forward(self, x):
        x = self.embedding(x)
        for layer in self.layers:
            x = layer(x)

        return x