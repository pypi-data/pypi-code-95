import torch.nn as nn
import torch.nn.functional as F
import einops


class ShuffleLayer(nn.Module):
    def __init__(self, hidden_dim, shuffle_dim):
        super().__init__()
        self.q = nn.Linear(hidden_dim, shuffle_dim)
        self.k = nn.Linear(hidden_dim, shuffle_dim)
        self.v = nn.Linear(hidden_dim, shuffle_dim)


    def forward(self, x, gamma, **kwargs):
        q = self.q(x)
        k = self.k(x)
        v = x

        attention = F.softmax(q @ k.transpose(1, 2), dim=-2)
        # ik WIL sharpness, dus niet delen door (dim)**.5

        return gamma * (attention @ v) + (1 - gamma) * x


class BucketAttentionLayer(nn.Module):
    def __init__(self, hidden_dim, heads, n_buckets):
        super().__init__()
        self.q = nn.Linear(hidden_dim, hidden_dim)
        self.k = nn.Linear(hidden_dim, hidden_dim)
        self.v = nn.Linear(hidden_dim, hidden_dim)
        self.heads = heads
        self.n_buckets = n_buckets


    def forward(self, x):
        h = self.heads

        q = self.q(x)
        k = self.k(x)
        v = self.v(x)

        q = einops.rearrange(q, 'b (n_buckets bucket_size) (h h_dim) -> b n_buckets h bucket_size h_dim',
                             n_buckets=self.n_buckets, h=h)
        k = einops.rearrange(k, 'b (n_buckets bucket_size) (h h_dim) -> b n_buckets h bucket_size h_dim',
                             n_buckets=self.n_buckets, h=h)
        v = einops.rearrange(v, 'b (n_buckets bucket_size) (h h_dim) -> b n_buckets h bucket_size h_dim',
                             n_buckets=self.n_buckets, h=h)

        attention = F.softmax(q @ k.transpose(3, 4), dim=-1)
        attended = attention @ v

        attended = einops.rearrange(attended, 'b n_buckets h bucket_size h_dim -> b (n_buckets bucket_size) (h h_dim)')
        return attended + x


class ShuffleFormerLayer(nn.Module):
    def __init__(self, seq_len, hidden_dim, shuffle_dim, heads, n_buckets):
        super().__init__()
        assert seq_len % n_buckets == 0
        self.shuffle = ShuffleLayer(hidden_dim, shuffle_dim)
        self.bucket_attention = BucketAttentionLayer(hidden_dim, heads, n_buckets)


    def forward(self, x, gamma):
        x = self.shuffle(x, gamma)
        x = self.bucket_attention(x)
        return x


class FeedforwardLayer(nn.Module):
    def __init__(self, hidden_dim, ff_dim=None, act=nn.GELU()):
        super().__init__()
        if not ff_dim:
            ff_dim = 4 * hidden_dim
        self.up_scale = nn.Linear(hidden_dim, ff_dim)
        self.act = act
        self.down_scale = nn.Linear(ff_dim, hidden_dim)

    def forward(self, x, **kwargs):
        return x + self.down_scale(self.act(self.up_scale(x)))
