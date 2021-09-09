import math, tqdm
import numpy as np
import tensorflow as tf
from tensorflow.keras import Input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, concatenate, Dense, Dropout, Flatten, Conv2D, \
    MaxPooling2D, AveragePooling2D, BatchNormalization
from mtnlpmodel.utils.model_util import Mish
from mtnlpmodel.utils.input_process_util import get_label_from_corpus, build_vacablookuper_from_corpus
from tokenizer_tools.tagset.offset.corpus import Corpus
from seq2annotation.input import Lookuper, index_table_from_file
from tf_crf_layer import keras_utils
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Layer
from tensorflow.python.ops import math_ops
from tensorflow.keras.metrics import categorical_accuracy


class MultiHeadDense(Dense):
    pass


@keras_utils.register_keras_custom_object
class RBF_Softmax_Layer(Layer):
    def __init__(self, class_num, scale=100, gamma=20, **kwargs):
        self.class_num = int(class_num)
        self.scale = scale
        self.gamma = gamma
        super(RBF_Softmax_Layer, self).__init__(**kwargs)

    def build(self, input_shape):
        # Create a trainable weight variable for this layer.
        self.kernel = self.add_weight(name='kernel',
                                      shape=(input_shape[1], self.class_num),
                                      initializer='glorot_normal',
                                      trainable=True)
        super(RBF_Softmax_Layer, self).build(input_shape)  # Be sure to call this at the end

    def call(self, x):
        embeddings = tf.nn.l2_normalize(x, axis=1, name='normed_embeddings')
        weights = tf.nn.l2_normalize(self.kernel, axis=0, name='normed_weights')
        logits = self.get_logits(embeddings, weights)
        softmax_prob = tf.nn.softmax(logits, axis=-1)
        # print_op = tf.print(logits, softmax_prob)
        # with tf.control_dependencies([print_op]):
        #     softmax_prob=tf.identity(softmax_prob)
        return softmax_prob

    def get_logits(self, embeddings, weights):
        diff = weights - tf.expand_dims(embeddings, axis=-1)
        diff_2 = math_ops.square(diff)
        metric = tf.reduce_sum(diff_2, axis=1)
        kernal_metric = tf.exp(-1.0 * metric / self.gamma)
        logits = self.scale * kernal_metric
        # print_op = tf.print(tf.shape(y_pred))
        # with tf.control_dependencies([print_op]):
        #     cos_t=tf.identity(cos_t)
        return logits

    def compute_output_shape(self, input_shape):
        return (input_shape[0], self.class_num)

    def get_config(self):
        config = {
            'class_num': self.class_num,
            'gamma': self.gamma,
            'scale': self.scale,
        }

        base_config = super().get_config().copy()
        return dict(list(base_config.items()) + list(config.items()))


@keras_utils.register_keras_custom_object
class ArcFace(Layer):
    '''Custom Keras layer implementing ArcFace including:
    1. Generation of embeddings
    2. Loss function
    3. Accuracy function
    cite: https://github.com/ktjonsson/keras-ArcFace/tree/master/src
    '''

    def __init__(self, class_num, margin=0.5, scale=64., **kwargs):
        self.class_num = int(class_num)
        self.margin = margin
        self.scale = scale
        assert self.scale > 0.0
        assert self.margin >= 0.0
        assert self.margin < (math.pi / 2)

        self.cos_m = tf.math.cos(margin)
        self.sin_m = tf.math.sin(margin)
        self.mm = self.sin_m * margin
        self.threshold = tf.math.cos(tf.constant(math.pi) - margin)
        super(ArcFace, self).__init__(**kwargs)

    def build(self, input_shape):
        # Create a trainable weight variable for this layer.
        self.kernel = self.add_weight(name='kernel',
                                      shape=(input_shape[1], self.class_num),
                                      initializer='glorot_normal',
                                      trainable=True)
        super(ArcFace, self).build(input_shape)  # Be sure to call this at the end

    def call(self, x):
        embeddings = tf.nn.l2_normalize(x, axis=1, name='normed_embeddings')
        weights = tf.nn.l2_normalize(self.kernel, axis=0, name='normed_weights')
        cos_t = tf.matmul(embeddings, weights, name='cos_t')
        logits = self.get_logits(cos_t)
        softmax_prob = tf.nn.softmax(logits, axis=-1)
        # print_op = tf.print(logits, softmax_prob)
        # with tf.control_dependencies([print_op]):
        # softmax_prob=tf.identity(softmax_prob)
        return softmax_prob, cos_t

    def get_logits(self, y_pred):
        cos_t = y_pred
        # print_op = tf.print(tf.shape(y_pred))
        # with tf.control_dependencies([print_op]):
        #     cos_t=tf.identity(cos_t)
        cos_t2 = tf.square(cos_t, name='cos_2')
        sin_t2 = tf.subtract(1., cos_t2, name='sin_2')
        sin_t = tf.sqrt(sin_t2, name='sin_t')
        cos_mt = self.scale * tf.subtract(tf.multiply(cos_t, self.cos_m), tf.multiply(sin_t, self.sin_m), name='cos_mt')
        cond_v = cos_t - self.threshold
        cond = tf.cast(tf.nn.relu(cond_v, name='if_else'), dtype=tf.bool)
        keep_val = self.scale * (cos_t - self.mm)
        cos_mt_temp = tf.where(cond, cos_mt, keep_val)
        labels = K.argmax(cos_t2, axis=-1)
        mask = tf.one_hot(labels, depth=self.class_num, name='one_hot_mask')
        inv_mask = tf.subtract(1., mask, name='inverse_mask')
        s_cos_t = tf.multiply(self.scale, cos_t, name='scalar_cos_t')
        logits = tf.add(tf.multiply(s_cos_t, inv_mask), tf.multiply(cos_mt_temp, mask), name='arcface_logits')
        return logits

    def compute_output_shape(self, input_shape):
        return (input_shape[0], self.class_num)

    def get_config(self):
        config = {
            'class_num': self.class_num,
            'margin': self.margin,
            'scale': self.scale,
        }

        base_config = super().get_config().copy()
        return dict(list(base_config.items()) + list(config.items()))


def read_dataset_from_file(filepath):
    from tokenizer_tools.tagset.offset.document import Document
    with open(filepath, 'rt', encoding='utf-8') as f:
        dataset = [line.strip().split('||-||') for line in f.readlines()]
    corpus = Corpus([])
    for data in tqdm.tqdm(dataset):
        text, label = data
        doc = Document(text=text, label=label)
        corpus.append(doc)
    return corpus


def get_label_from_file(label_filepath):
    with open(label_filepath, 'rt', encoding='utf-8') as f:
        labels = f.readlines()
    return labels


def input_data_process_finetuning(config, **hyperparams):
    # read data
    data = read_dataset_from_file(config['data'])
    label_file = config['label_file']
    # get train/test corpus
    labels = get_label_from_file(label_file)
    #labels = [label for label in labels if label != 'UNK']
    # labels.insert(0, 'UNK')

    test_ratio = config['test_ratio']
    if len(data)<10:
        cls_train_data = cls_eval_data =data
    else:
        cls_train_data, cls_eval_data = data.train_test_split(test_size=test_ratio, random_state=50)

    # build lookupers
    cls_label_lookuper = Lookuper({v: i for i, v in enumerate(labels)})

    vocab_data_file = config.get("vocabulary_file", None)
    assert vocab_data_file

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

    #write_to_txt(vocabulary_lookuper, './data/vocab.txt')
    #write_to_txt(cls_label_lookuper, './data/label.txt')
    return output_dict


def build_model(**config):
    input_length = config['input_length']
    output_dim = config['output_dim']
    vocab_size = config['vocab_size']
    EMBED_DIM = config['EMBED_DIM']
    model_weights_path = config['model_weights_path']
    n_channels = 8

    input_layer = Input(shape=(input_length,), dtype='int32', name='cls_input')

    embedding_layer = Embedding(vocab_size,
                                EMBED_DIM,
                                mask_zero=True,
                                input_length=input_length,
                                name='embedding_vocab'
                                )(input_layer)

    # TextCNN
    if n_channels > 1:
        embedding_layer = tf.keras.layers.Reshape((input_length, EMBED_DIM // n_channels, n_channels))(
            embedding_layer)

    kernel_sizes = [1, 2, 3, 4, 5]

    pooling_out = []

    for kernel_size in kernel_sizes:
        cls_conv_layer = Conv2D(filters=32, kernel_size=(kernel_size, EMBED_DIM // n_channels), padding='valid',
                                strides=1, activation='relu')(embedding_layer)
        cls_conv_layer_neck = Conv2D(filters=1, kernel_size=(1, 1), padding='valid',
                                strides=1, activation='relu')(cls_conv_layer)
        cls_conv_layer_highway = tf.keras.layers.Reshape((1, 1, (input_length-kernel_size+1)*1))(cls_conv_layer_neck)
        cls_conv_shortcut = Conv2D(filters=32, kernel_size=(1, 1), padding='valid',
                                strides=1, activation='relu')(cls_conv_layer_highway)

        cls_pooling_layer = MaxPooling2D(pool_size=(int(cls_conv_layer.shape[1]), 1))(cls_conv_layer)
        pooling_out.append(cls_pooling_layer)
        pooling_out.append(cls_conv_shortcut)

    pool_output = concatenate([p for p in pooling_out])

    cls_flat = Flatten()(pool_output)
    cls_flat = Dropout(0.3)(cls_flat)

    # vector
    cls_layer = Dense(64, activation='relu')(cls_flat)
    cls_layer = Dense(output_dim, activation='sigmoid', name='CLS')(cls_layer)
    cls_output = cls_layer

    model = Model(inputs=input_layer, outputs=cls_output)
    model.load_weights(model_weights_path)

    return model

