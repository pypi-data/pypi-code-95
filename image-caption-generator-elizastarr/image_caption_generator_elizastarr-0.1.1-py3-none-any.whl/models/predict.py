"""
Script to predict captions using 
    1) a decoder with the LSTM learner weights and 
    2) test image representations.
Predictions are saved in the data/processed directory in word format (not integers).
"""

from pathlib import Path
import os
import pickle

from src.data.load_data import load_test, load_idx_word_dicts
from decoder import Decoder


def predict_decoder():
    model_folder = Path("models/")
    data_folder = Path("data/processed")
    idx_to_word, _ = load_idx_word_dicts()
    image_representations_test, _, _ = load_test()

    # Get decoder (with LSTM weights)
    decoder = Decoder()
    decoder.build(input_shape=(5000, 20480))
    decoder.load_weights(
        os.path.join(model_folder, "LSTM_learner.h5"), by_name=True, skip_mismatch=True
    )

    # Get predictions
    predictions_idx = decoder.predict(image_representations_test)
    predictions_word = [
        [idx_to_word.get(key) for key in prediction] for prediction in predictions_idx
    ]

    # Save predictions
    pickle.dump(
        predictions_word,
        open(os.path.join(data_folder, "predictions_word_test.pkl"), "wb"),
    )



predict_decoder()

