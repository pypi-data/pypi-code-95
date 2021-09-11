import re
import string
import torch
from tqdm import tqdm
from .model import CharEmbedder


def load_index(path):
    return torch.load(path)


class SearchIndex(object):
    
    def __init__(self, text_list, device='cpu', word_tokenizer=None, d_model=64, max_length=20, kernels=[3, 5], bigram=False, **args):
        """Compute embeddings given a list of sequences

        Args:
            text_list (list[str]): list of sequences
            device (str, optional): 'cpu' or 'cuda'. Defaults to 'cpu'.
            word_tokenizer (callable, optional): tokenizer function. Defaults to None.
            d_model (int, optional): embedding dimension. Defaults to 64.
            length (int, optional): Max char length. Defaults to 15.
            kernels (list, optional): [description]. Defaults to [3, 5].
        """
        
        self.text_list = text_list
        
        if word_tokenizer is None:
            word_tokenizer = self.simple_tokenizer
            
        self.word_tokenizer = word_tokenizer
        
        self.model = CharEmbedder(d_model, kernels=kernels, max_length=max_length, bigram=bigram)
        
        tokenized = []
        for t in tqdm(text_list, desc='tokenization'):
            tokenized.append(self.word_tokenizer(t))
            
        self.embeddings = self.model.compute_embeddings(tokenized, device=device, **args)
        
    def simple_tokenizer(self, txt):
        """simple tokenization function

        Args:
            txt (str): string sequence

        Returns:
            list[str]: list of tokens
        """
        t = txt.strip().lower()
        t = re.sub(r'([%s])' % re.escape(string.punctuation), r' \1 ', t) 
        t = re.sub(r'\\.', r' ', t) 
        t = re.sub(r'\s+', r' ', t)
        return t.split()
        
    def search(self, query):
        """Return most relevant idx

        Args:
            query (str): query

        Returns:
            list[int]: sort result ids
        """
        query = [self.word_tokenizer(query)]
        query_embedding = self.model.compute_embeddings(query, pbar=False, batch_size=1, device='cpu')
        score = self.embeddings @ query_embedding.transpose(1, 2)
        # max sum
        maxsum = score.max(-2).values.sum(-1)
        
        return torch.argsort(maxsum, dim=0, descending=True).numpy()
    
    def show_topk(self, query, k=10):
        """Show top k results

        Args:
            query (str): query
            k (int, optional): top k result to show. Defaults to 10.
        """
        
        res = self.search(query)[:k]
        for r in res:
            print(self.text_list[r])
    
    def save(self, path):
        """Save index

        Args:
            path (str): path to save
        """
        torch.save(self, path)