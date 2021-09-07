from collections import Counter
import logging

import torch
from gensim.models import Word2Vec
from gensim.models.word2vec import PathLineSentences, LineSentence
from gensim.models.callbacks import CallbackAny2Vec

logger = logging.getLogger(__file__)


def build_vocab_from_text_file(
    file_path, keep_tokens=("<pad>", "<unk>", "<sos>", "<eos>"), 
    freq_threshold=3, stop_words=(" ",), tokenizer=lambda x: list(x),
):
    """Build vocab from a text file.

    Args:
        file_path (str): text file path
        keep_tokens (tuple, optional): preset tokens. 
            Defaults to ("<pad>", "<unk>", "<sos>", "<eos>").
        freq_threshold (int, optional): word frequency limition. Defaults to 3.
        stop_words (iterable[str], optional): stop words that we don't want
            keep in vocab. Defaults to (" ",).
        tokenizer (callable): tokenizer.

    Returns:
        tuple: (str_to_idx: dict, idx_to_str: dict)
    """
    word_counter = Counter()
    
    with open(file_path, 'r') as frd:
        for line in frd.readlines():
            word_counter.update(Counter(tokenizer(line.strip())))

    # remove stop words
    if stop_words:
        for word in stop_words:
            if word in word_counter:
                word_counter.pop(word)
    
    str_to_idx = {}
    idx_to_str = {}
    cnt = 0
    
    for token in keep_tokens:
        str_to_idx[token] = cnt
        idx_to_str[cnt] = token
        cnt += 1
        
    for word, freq in word_counter.items():
        # filter words with frequency less than threshold
        if freq < freq_threshold:
            continue
        str_to_idx[word] = cnt
        idx_to_str[cnt] = word
        cnt += 1

    return str_to_idx, idx_to_str


def load_wv_model(
    w2v_model_path, binary, keep_tokens=("<pad>", "<unk>", "<sos>", "<eos>"),
):
    """Load w2v model and build vocab with pretrained embeddings.

    Args:
        w2v_model_path (str): w2v model path
        binary (bool): indicates if the w2v a binary model
        keep_tokens (tuple, optional): preset tokens. 
            Defaults to ("<pad>", "<unk>", "<sos>", "<eos>").

    Raises:
        Exception: raises when w2v model fails to load

    Returns:
        tuple: (str_to_idx: dict, idx_to_str: dict, embedding: torch.tensor)
    """
    try:
        if binary:
            w2v = Word2Vec.load(w2v_model_path)
        else:
            from gensim.models import KeyedVectors
            w2v = KeyedVectors.load_word2vec_format(
                w2v_model_path, binary=False,
            )

        logger.info("Init: done loading existing w2v model")

    except Exception as e:
        raise Exception(
            f"model load failed: {w2v_model_path} !"
            f"message: {e}",
        )

    str_to_idx = {}
    cnt = 0
    
    for token in keep_tokens:
        str_to_idx[token] = cnt
        cnt += 1

    embedding = torch.tensor(w2v.wv.vectors, dtype=torch.float64)

    for_pad = torch.zeros(1, embedding.shape[1], dtype=embedding.dtype)
    for_unk = torch.randn(1, embedding.shape[1], dtype=embedding.dtype)
    for_start = torch.zeros(1, embedding.shape[1], dtype=embedding.dtype)
    for_end = torch.randn(1, embedding.shape[1], dtype=embedding.dtype)

    embedding = torch.cat(
        [for_pad, for_unk, for_start, for_end, embedding], dim=0,
    )

    for token in w2v.wv.vocab.keys():
        # skip unk, pad, start, end
        str_to_idx[token] = w2v.wv.vocab[token].index + len(keep_tokens)

    idx_to_str = {v: k for k, v in str_to_idx.items()}

    return str_to_idx, idx_to_str, embedding


class Callback(CallbackAny2Vec):
    """Callback for gensim to print loss after each epoch during training."""

    def __init__(self):
        self.epoch = 0
        self.loss_previous_step = 0

    def on_epoch_end(self, model):
        loss = model.get_latest_training_loss()
        if self.epoch == 0:
            print('Loss after epoch {}: {}'.format(self.epoch, loss))
        else:
            print('Loss after epoch {}: {}'.format(
                self.epoch, loss - self.loss_previous_step)
            )
        self.epoch += 1
        self.loss_previous_step = loss


def train_w2v_from_line_file(
    train_from,
    save_to,
    tokenize=None,
    epochs=200,
    binary=False,
    size=256,
    min_count=1,
    window=6,
    sg=1,
    hs=0,
    negative=1,
    seed=12,
    callbacks=(Callback(),),
    compute_loss=True,
):
    """Train w2v model from line file.

    Args:
        train_from (str): path of text file to train w2v
        save_to (str): path save model to
        tokenize (callable, optional): tokenizer, default to None.
        
    Words must be already preprocessed and separated by whitespace, saved in 
    `train_from` one sentence per line.
    
    the model will be saved to `save_to` after done training.

    we can load the model through:
        >>> from gensim.models.keyedvectors import KeyedVectors
        >>> w2v = KeyedVectors.load_word2vec_format(save_to, binary=binary)
    
    or simply load w2v model and build vocab with pretrained embeddings 
    by calling load_wv_model() defined above.
    """
    model = Word2Vec(
        size=size,
        min_count=min_count, 
        window=window,
        sg=sg,
        hs=hs,
        negative=negative,
        seed=seed,
        callbacks=callbacks,
        compute_loss=compute_loss,
    )

    if tokenize:
        assert isinstance(tokenize("foo bar"), list), "bad tokenizer!"
        
        all_lines = []
        with open(train_from) as frd:
            for line in frd.readlines():
                all_lines.append(tokenize(line.strip()))
    else:
        sentences = LineSentence(train_from)
                
    sentences = PathLineSentences(train_from)
    model.build_vocab(sentences=sentences)

    model.train(
        sentences=sentences,
        epochs=epochs,
        total_examples=model.corpus_count,
        compute_loss=compute_loss,
    )

    model.wv.save_word2vec_format(save_to, binary=binary)
