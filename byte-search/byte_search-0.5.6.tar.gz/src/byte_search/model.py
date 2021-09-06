import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader
import torch.nn.functional as F
from tqdm import tqdm
from .cnn import CharCNN
from .tokenizer import ByteCharEncoder
from functools import partial

class BiAvg(nn.AvgPool1d):
    
    def __init__(self):
        super().__init__(self, kernel_size=2, stride=1, padding=1)

    def forward(self, x):
        
        x = x.transpose(1, 2)
        
        x = super().forward(x)
        
        return x.transpose(1, 2)


class CharEmbedder(nn.Module):
    
    def __init__(self, hidden_size, max_length=20, kernels=[2, 3, 4], bigram=False):
        """Embedding model

        Args:
            hidden_size (int): embedding hidden size
            max_length (int, optional): character max length. Defaults to 20.
            kernels (list, optional): kernel sizes for convolution. Defaults to [2, 3, 4].
        """
        
        super().__init__()
        
        self.hidden_size = hidden_size
        self.char_transformer = ByteCharEncoder()
        self.embedding = nn.Embedding(256 + 1, hidden_size, padding_idx=0)
        self.cnn = CharCNN(hidden_size, kernels=kernels)

        self.bigram = bigram

        if bigram:
            self.b_pool = BiAvg()
                
        self.max_length = max_length
        
    def forward(self, indexes):
        """forward pass

        Args:
            indexes (torch.LongTensor): input ids of dim [B, num_words, num_chars]

        Returns:
            torch.Tensor: embeddings [B, num_words, hidden_size]
        """
        x = self.embedding(indexes) # [B, W, C, H]
        B, W, C, H = x.size()
        x = x.view(B * W, C, H) # [B * W, C, H]
        x = self.cnn(x) # [B * W, H]
        x = x.view(B, W, H)

        if self.bigram:
            x_pool = self.b_pool(x)
            x = torch.cat([x, x_pool], dim=1)
                
        return F.normalize(x, dim=2)
        
    def direct_forward(self, list_tokens):
        """Embed a list of tokenized sequences [['this', 'is'], ['I', 'am]]

        Args:
            list_tokens (list[list[str]]): list of tokenized sequences

        Returns:
            [torch.Tensor]: embeddings [B, num_words, hidden_size]
        """
        indexes = self.char_transformer.encode_batch_with_length(list_tokens, length=self.max_length) # [B, W, C]
        return self.forward(indexes)
    
    def create_dataloader(self, list_tokens, **kwargs):
        """Create a dataloader

        Args:
            list_tokens (list[list[str]]): list of tokenized sequences

        Returns:
            [torch.data.DataLoader]: returns a dataloader
        """
        return DataLoader(list_tokens, collate_fn=partial(self.char_transformer.encode_batch_with_length, length=self.max_length), **kwargs)
    
    @torch.no_grad()
    def compute_embeddings(self, list_tokens, pbar=True, device='cpu', **kwargs):
        """Compute embeddings given a list of tokenized sequences

        Args:
            list_tokens (list[list[str]]): list of tokenized sequences
            pbar (bool, optional): use progress bar. Defaults to True.
            device (str, optional): 'cpu' or 'cuda'. Defaults to 'cpu'.

        Returns:
            torch.Tensor: embeddings [B, num_words, hidden_size]
        """
        
        self.to(device)
        
        loader = self.create_dataloader(list_tokens, **kwargs)
        
        embeddings = []
        
        if pbar:
            loader = tqdm(loader, desc='compute embeddings')
        
        for x in loader:
            
            x = x.to(device)
            e = self.forward(x)
            embeddings.append(e.cpu())
            
        return pad_sequence([i for k in embeddings for i in k], batch_first=True)