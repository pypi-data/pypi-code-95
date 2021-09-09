import math, tqdm, random
import numpy as np
import tensorflow as tf
from tensorflow.python.ops import nn
from tensorflow.keras import Input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, concatenate, Dense, Dropout, Flatten, Conv2D, \
    MaxPooling2D, add
from mtnlpmodel.utils.model_util import Mish
from mtnlpmodel.utils.input_process_util import get_label_from_corpus, build_vacablookuper_from_corpus
from tokenizer_tools.tagset.offset.corpus import Corpus
from seq2annotation.input import Lookuper, index_table_from_file
from tf_crf_layer import keras_utils
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Layer
from tensorflow.python.ops import math_ops
from tensorflow.keras.metrics import categorical_accuracy
from tensorflow.python.util.tf_export import keras_export


@keras_utils.register_keras_custom_object
class TokenAndPositionEmbedding(tf.keras.layers.Layer):
    def __init__(self, vocab_size, embed_dim, input_length, mask_zero=True, **kwargs):
        super(TokenAndPositionEmbedding, self).__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.input_length = input_length
        self.mask_zero = mask_zero

    def call(self, x):
        self.token_emb = tf.keras.layers.Embedding(input_dim=self.vocab_size, output_dim=self.embed_dim,
                                                   mask_zero=self.mask_zero)
        self.pos_emb = tf.keras.layers.Embedding(input_dim=self.input_length, output_dim=self.embed_dim,
                                                 mask_zero=self.mask_zero)
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions

    def get_config(self):
        config = {
            "vocab_size": self.vocab_size,
            "embed_dim": self.embed_dim,
            "input_length": self.input_length,
            "mask_zero": self.mask_zero
        }

        base_config = super().get_config().copy()
        return dict(list(base_config.items()) + list(config.items()))


@keras_utils.register_keras_custom_object
@keras_export('keras.layers.MinPool2D', 'keras.layers.MinPooling2D')
class MinPooling2D(MaxPooling2D):

    def __init__(self, pool_size=(2, 2), strides=None,
                 padding='valid', data_format=None, **kwargs):
        # import pdb
        # pdb.set_trace()
        super(MaxPooling2D, self).__init__(self.pool_function, pool_size, strides, padding,
                                           data_format, **kwargs)
        self.pool_size = tuple(pool_size)
        self.strides = tuple(strides)
        self.padding = 'valid'
        self.data_format = data_format

    def call(self, inputs):
        return self.pool_function(inputs, self.pool_size, self.strides, self.padding, self.data_format)

    def pool_function(self, inputs, ksize, strides, padding, data_format):
        # import pdb
        # pdb.set_trace()
        return -K.pool2d(-inputs, ksize, strides, padding, data_format, pool_mode='max')


def expand_short_pattern(data, max_len, ratio=4):
    shorts = [i for i in data if len(i.text) <= max_len]
    longs = [i for i in data if len(i.text) > max_len]
    shorts = ratio * shorts
    out = []
    out.extend(shorts)
    out.extend(longs)
    random.shuffle(out)
    return Corpus(out)


def read_dataset_from_file(filepath):
    from tokenizer_tools.tagset.offset.document import Document
    with open(filepath, 'rt', encoding='utf-8') as f:
        dataset = [line.strip().split('||-||') for line in f.readlines()]
    corpus = Corpus([])
    for data in tqdm.tqdm(dataset):
        text, label = data
        doc = Document(text=text, label=label)
        corpus.append(doc)
    # corpus = expand_short_pattern(corpus, max_len=3, ratio=2)
    return corpus


def input_data_process(config, **hyperparams):
    # read data
    data = read_dataset_from_file(config['data'])

    # get train/test corpus
    labels = get_label_from_corpus(data)
    labels = [label for label in labels if label != 'UNK']
    # labels.insert(0, 'UNK')

    test_ratio = config['test_ratio']
    cls_train_data, cls_eval_data = data.train_test_split(test_size=test_ratio, random_state=50)

    # build lookupers
    cls_label_lookuper = Lookuper({v: i for i, v in enumerate(labels)})

    vocab_data_file = config.get("vocabulary_file", None)

    if not vocab_data_file:
        # get vacab_data for corpus
        vocabulary_lookuper = build_vacablookuper_from_corpus(*(data, Corpus([])),
                                                              config={'oov_key': 'UNK'})  # from corpus
    else:
        vocabulary_lookuper = index_table_from_file(vocab_data_file, config={'oov_key': 'UNK'})  # from vocab_file

    # cls (data&label) str->int
    def cls_preprocss_softmax(data, maxlen, **kwargs):
        raw_x_cls = []
        raw_y_cls = []

        for offset_data in data:
            label = offset_data.label
            words = offset_data.text

            if label == 'UNK':
                label_id = 0
            else:
                label_id = cls_label_lookuper.lookup(label) + 1

            word_ids = [vocabulary_lookuper.lookup(i) for i in words]

            raw_x_cls.append(word_ids)
            raw_y_cls.append(label_id)

        if maxlen is None:
            maxlen = max(len(s) for s in raw_x_cls)

        print(">>> maxlen: {}".format(maxlen))

        x_cls = tf.keras.preprocessing.sequence.pad_sequences(
            raw_x_cls, maxlen, padding="post"
        )  # right padding

        from tensorflow.keras.utils import to_categorical
        y_cls = np.asarray(raw_y_cls)
        y_cls = y_cls[:, np.newaxis]
        y_cls = to_categorical(y_cls, kwargs.get('cls_dims', 81))

        return x_cls, y_cls

    def cls_preprocess_sigmoid(data, maxlen, **kwargs):
        raw_x_cls = []
        raw_y_cls = []

        for offset_data in data:
            label = offset_data.label
            words = offset_data.text

            if label == 'UNK':
                label_id = 0
            else:
                label_id = cls_label_lookuper.lookup(label) + 1
            word_ids = [vocabulary_lookuper.lookup(i) for i in words]

            raw_x_cls.append(word_ids)
            raw_y_cls.append(label_id)

        if maxlen is None:
            maxlen = max(len(s) for s in raw_x_cls)

        print(">>> maxlen: {}".format(maxlen))

        x_cls = tf.keras.preprocessing.sequence.pad_sequences(
            raw_x_cls, maxlen, padding="post"
        )  # right padding

        from tensorflow.keras.utils import to_categorical
        def to_categorical_sigmoid(y, num_classes, dtype='float32'):
            y = np.array(y, dtype='int')
            input_shape = y.shape
            if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
                input_shape = tuple(input_shape[:-1])
            y = y.ravel()
            n = y.shape[0]
            categorical = np.zeros((n, num_classes), dtype=dtype)
            for index, label in enumerate(y):
                if label == 0:
                    categorical[index, label] = 0
                else:
                    categorical[index, label - 1] = 1
            output_shape = input_shape + (num_classes,)
            categorical = np.reshape(categorical, output_shape)
            return categorical

        y_cls = np.array(raw_y_cls)
        y_cls = y_cls[:, np.newaxis]
        y_cls = to_categorical_sigmoid(y_cls, kwargs.get('cls_dims', 81))

        return x_cls, y_cls

    cls_train_x, cls_train_y = cls_preprocess_sigmoid(cls_train_data, hyperparams['MAX_SENTENCE_LEN'],
                                                      **{'cls_dims': cls_label_lookuper.size()})
    cls_test_x, cls_test_y = cls_preprocess_sigmoid(cls_eval_data, hyperparams['MAX_SENTENCE_LEN'],
                                                    **{'cls_dims': cls_label_lookuper.size()})

    # cls_class_weight = get_class_weight(cls_train_data, cls_label_lookuper)

    output_dict = {'cls_train_x': cls_train_x, 'cls_train_y': cls_train_y,
                   'cls_test_x': cls_test_x, 'cls_test_y': cls_test_y,
                   'cls_label_lookuper': cls_label_lookuper,
                   'vocabulary_lookuper': vocabulary_lookuper,
                   }

    def write_to_txt(lookuper, path):
        out = lookuper.inverse_table.values()
        with open(path, 'wt', encoding='utf-8') as f:
            f.write('\n'.join(out))

    write_to_txt(vocabulary_lookuper, './data/vocab.txt')
    write_to_txt(cls_label_lookuper, './data/label.txt')
    return output_dict


def build_model(**config):
    input_length = config['input_length']
    output_dim = config['output_dim']
    vocab_size = config['vocab_size']
    EMBED_DIM = config['EMBED_DIM']
    n_channels = 8

    input_layer = Input(shape=(input_length,), dtype='int32', name='cls_input')

    embedding_layer = TokenAndPositionEmbedding(vocab_size,
                                                EMBED_DIM,
                                                mask_zero=True,
                                                input_length=input_length,
                                                name='embedding'
                                                )(input_layer)

    # TextCNN
    if n_channels > 1:
        embedding_layer = tf.keras.layers.Reshape((input_length, EMBED_DIM // n_channels, n_channels))(
            embedding_layer)

    kernel_sizes = [1, 2, 3, 5, 7, 9]

    pooling_out = []
    for kernel_size in kernel_sizes:
        
        if kernel_size<5:  
          cls_conv_layer = Conv2D(filters=128, kernel_size=(kernel_size, EMBED_DIM // n_channels), padding='valid',
                          strides=(kernel_size+1)//2, activation='tanh')(embedding_layer)    
          max_pooling_layer = MaxPooling2D(pool_size=(int(cls_conv_layer.shape[1]), 1))(cls_conv_layer)
          pooling_out.append(max_pooling_layer)
        else:
          cls_conv_layer = Conv2D(filters=128, kernel_size=(kernel_size, EMBED_DIM // n_channels), padding='valid',
                                strides=(kernel_size+2)//3, activation='tanh')(embedding_layer)
          min_pooling_layer = MinPooling2D(pool_size=(int(cls_conv_layer.shape[1]), 1), strides=(int(cls_conv_layer.shape[1]),1))(cls_conv_layer)
          pooling_out.append(min_pooling_layer)

    pool_output = concatenate([p for p in pooling_out])

    cls_flat = Flatten()(pool_output)
    cls_flat = Dropout(0.3)(cls_flat)

    cls_layer = cls_flat
    cls_layer = Dense(output_dim, activation='sigmoid', name='CLS')(cls_layer)
    cls_output = cls_layer

    model = Model(inputs=input_layer, outputs=cls_output)

    return model  
