from collections import defaultdict
import torch
from torch.nn.utils.rnn import pad_sequence
import torch.nn.functional as F

class ByteEncoder(object):
    
    def __init__(self):
        
        vocab = None
                
    def encode_token(self, token):
        """Encode token

        Args:
            token (str): a string

        Returns:
            torch.LongTensor: encoded token
        """
        return torch.LongTensor(list(token.encode("utf-8"))) + 1 # 0 for padding
    
    def encode_sequence(self, sequence):
        """encode a tokenized sequence

        Args:
            sequence (list[str]): tokenized sequence

        Returns:
            list: contains all encoded tokens
        """
        return [self.encode_token(token) for token in sequence]
    
    def encode_batch(self, batch):
        """encode a batch of tokenized sequence

        Args:
            batch (list[list[str]]): batch of tokenized sequence

        Returns:
            torch.LongTensor: contains the encoded (padded) batches [B, num_words, num_chars]
        """
        
        lengths = []
        batch_tokens = []
        
        for seq in batch:
            batch_tokens.extend(self.encode_sequence(seq))
            lengths.append(len(seq))
            
        batch_tokens = pad_sequence(batch_tokens, batch_first=True)
            
        list_seq = torch.split(batch_tokens, lengths)
            
        return pad_sequence(list_seq, batch_first=True)
    
    def encode_batch_with_length(self, batch, length=15):
        """encode a batch of tokenized sequence given a max char length

        Args:
            batch (list[list[str]]): batch of tokenized sequence
            length (int, optional): Max char length. Defaults to 15.

        Returns:
            torch.LongTensor: contains the encoded (padded) batches [B, num_words, length]
        """
        
        lengths = []
        batch_tokens = []
        
        for seq in batch:
            batch_tokens.extend(self.encode_sequence(seq))
            lengths.append(len(seq))
        
        batch_tokens = torch.stack([self.pad_middle(i, length) for i in batch_tokens], dim=0)
        
        list_seq = torch.split(batch_tokens, lengths)
        
        return pad_sequence(list_seq, batch_first=True)
    
    def pad_middle(self, b, max_len):
        
        b = b[:max_len]
        
        len_b = len(b)
        
        pad_left = (max_len - len_b)//2
        
        if (len_b + max_len) % 2 == 0:
            return F.pad(b, (pad_left, pad_left))
        else:
            return F.pad(b, (pad_left + 1, pad_left))


class WordEncoder(object):
    
    def __init__(self, tokenizer, special_tokens=["[PAD]", "[UNK]"]):
        """Word encoder

        Args:
            tokenizer (callable): tokenization function
            special_tokens (list, optional): Special tokens. Defaults to ["[PAD]", "[UNK]"].
        """
        
        self.tokenizer = tokenizer
        
        self.special_tokens = special_tokens
        
        self.vocabulary = []
        
        self.token_to_id = {}
        
        self.id_to_token = {}
        
    def fit(self, documents):
        """Fit a document

        Args:
            documents (List[str]): list of strings
        """
        
        counter = defaultdict(int)
        
        for x in documents:
            x = self.check_type(x)
            for token in x:
                counter[token] += 1
                        
        self.vocabulary = self.special_tokens + [t for t in counter.keys()]
        
        for k, v in enumerate(self.vocabulary):
            self.token_to_id[v] = k
            self.id_to_token[k] = v
        
    def tokenize(self, x):
        """tokenize a sequence

        Args:
            x (str): input sequence

        Returns:
            list[str]: tokenized sequence
        """
        return self.tokenizer(x)
    
    def batch_tokenize(self, doc):
        """Tokenize a batch of sequence

        Args:
            doc (list[str]): [description]

        Returns:
            list[list[str]]: batch tokenized
        """
        return [self.tokenizer(x) for x in doc]
    
    def encode(self, x):
        """Encode sentence to list of ids

        Args:
            x ([type]): [description]

        Returns:
            [type]: [description]
        """
        x = self.check_type(x)
        y = []
        for t in x:
            try:
                idx = self.token_to_id[t]
            except KeyError:
                idx = 1
            y.append(idx)
        return y
    
    def encode_batch(self, doc, paddind_idx=0):
        """batch encode a list of sequence

        Args:
            doc ([type]): [description]
            paddind_idx (int, optional): [description]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        
        batch = []
        for b in doc:
            b = torch.LongTensor(self.encode(b))
            batch.append(b)
            
        return pad_sequence(batch, batch_first=True, padding_value=paddind_idx)
    
    def check_type(self, x):
        if isinstance(x, str):
            return self.tokenizer(x)
        elif isinstance(x, list):
            return x
        else:
            raise ValueError
            
    def __repr__(self):
        return f"tokenizer containing {len(self.vocabulary)} tokens"