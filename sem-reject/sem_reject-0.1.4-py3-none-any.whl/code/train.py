import os, sys
sys.path.append('.')
import tensorflow as tf
from tensorflow.keras.backend import set_session
# tf.enable_eager_execution()
from mtnlpmodel.utils.input_process_util import _read_configure
from mtnlpmodel.utils.ctrldir_util import (create_dir_if_needed,
                                           create_file_dir_if_needed,
                                           create_or_rm_dir_if_needed)
from mtnlpmodel.utils.deliverablemodel_util import ConverterForVector
from deliverable_util import (ConverterForRequest,
                              export_as_vector_deliverable_model,
                              export_as_deliverable_model,
                              ConverterForResponse)

def main():
    # get configure
    config = _read_configure("./configure.yaml")

    # get Parameters (controller)
    EPOCHS = config.get("epochs", 10)
    BATCHSIZE = config.get("batch_size", 32)
    LEARNINGRATE = config.get("learning_rate", 0.001)
    MAX_SENTENCE_LEN = config.get("max_sentence_len", 25)
    LRDECAY = config.get('lr_decay', False)
    EARLYSTOP = config.get('early_stop', False)

    # get Parameters (model structure)
    EMBED_DIM = config.get("embedding_dim", 128)

    # set gpu occupancy rate
    gpu_cfg = tf.ConfigProto()
    gpu_cfg.gpu_options.allocator_type = 'BFC'  # A "Best-fit with coalescing" algorithm, simplified from a version of dlmalloc.
    gpu_cfg.gpu_options.per_process_gpu_memory_fraction = 0.5
    gpu_cfg.gpu_options.allow_growth = True
    set_session(tf.Session(config=gpu_cfg))

    # get preprocessed input data dict
    from core import input_data_process
    # to build a fixed training environment, input data should be fixed.
    # input_data should be shuffled and remove duplication outside the trainer before running the program.
    # input data should be corpus(no duplication, shuffle well)
    data_dict = input_data_process(config, **{'MAX_SENTENCE_LEN': MAX_SENTENCE_LEN,})
    
    # get lookupers
    cls_label_lookuper = data_dict['cls_label_lookuper']
    vocabulary_lookuper = data_dict['vocabulary_lookuper']

    # get train/test data for training model
    cls_train_x, cls_train_y = data_dict['cls_train_x'], data_dict['cls_train_y']
    cls_test_x, cls_test_y = data_dict['cls_test_x'], data_dict['cls_test_y']

    # build model or finetuning
    from core import build_model
    params = {'EMBED_DIM': EMBED_DIM,
              'input_length': MAX_SENTENCE_LEN,
              'vocab_size': vocabulary_lookuper.size(),
              'output_dim': cls_label_lookuper.size(),
              }
    # train the model by random initializer(make a fresh start to train a model)
    model = build_model(**params)  # to build the model and get cls_vector

    model.summary()

    # build callbacks list
    callbacks_list = []

    tensorboard_callback = tf.keras.callbacks.TensorBoard(
        log_dir=create_dir_if_needed(config["summary_log_dir"]),
        #log_dir='.\\results\\summary_log_dir',  # for windows
        batch_size=BATCHSIZE,
    )
    callbacks_list.append(tensorboard_callback)

    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        os.path.join(create_dir_if_needed(config["model_dir"]), "cp-{epoch:04d}.ckpt"),
        load_weights_on_restart=True,
        verbose=1,
    )
    callbacks_list.append(checkpoint_callback)

    # early stop util
    if EARLYSTOP:
        early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss',  # early stop index
                                                      patience=3,  # early stop delay epoch
                                                      verbose=2,  # display mode
                                                      mode='auto')
        callbacks_list.append(early_stop)

    # learning rate decay util
    if LRDECAY:
        reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1,
                                                         mode='auto', epsilon=0.0001, cooldown=0, min_lr=0.00001)
        callbacks_list.append(reduce_lr)

    # set optimizer
    adam_optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNINGRATE, beta_1=0.9, beta_2=0.999, amsgrad=True)

    CLS_out_name = 'CLS'

    # train 
    model.compile(optimizer=adam_optimizer,
                            loss={CLS_out_name: 'binary_crossentropy'},
                            metrics={CLS_out_name: 'accuracy'})
    
    #from adversal_embedding.core import adversarial_training
    #adversarial_training(model, 'embedding', 0.5) 
    
    model.fit(
        {'cls_input': cls_train_x},
        { CLS_out_name: cls_train_y},
        epochs=EPOCHS,
        batch_size=BATCHSIZE,
        #class_weight={CLS_out_name: 'auto'},
        validation_data=[{'cls_input': cls_test_x},
                         {CLS_out_name: cls_test_y}],
        callbacks=callbacks_list, )


    # save model
    model.save(create_file_dir_if_needed(config["h5_model_file"]))

    model.save_weights(create_file_dir_if_needed(config["h5_weights_file"]))

    tf.keras.experimental.export_saved_model(
        model, create_or_rm_dir_if_needed(config["saved_model_dir"])
    )

    # save cos_t&NER deliverable model
    export_as_deliverable_model(
        create_dir_if_needed(config["deliverable_model_dir"]),
        keras_saved_model=config["saved_model_dir"],
        converter_for_request=ConverterForRequest(),
        converter_for_response=ConverterForResponse(),
        lookup_tables={'vocab_lookup': vocabulary_lookuper,
                       'label_lookup': cls_label_lookuper},
        padding_parameter={"maxlen": MAX_SENTENCE_LEN, "value": 0, "padding": "post"},
        addition_model_dependency=["tf-crf-layer"],
        custom_object_dependency=["tf_crf_layer"],
    )


if __name__ == "__main__":
    main()
