# -*- coding: utf-8 -*-
import os
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pickle

from image_representations import get_image_representations
from caption_preprocessing import get_caption_dictionaries
from split_and_format import train_test_val_split, format_as_matrix


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    print("Loading data from data/raw.")
    raw_file_path = os.path.join(input_filepath, "Flickr8k_processed.pkl")
    images, captions = pickle.load(open(raw_file_path, 'rb'))
    print('images shape: ', images.shape, ' captions length: ', len(captions))

    # Get representations
    image_representations = get_image_representations(images)
    image_representations = image_representations.reshape(len(images), 20480)
    print(image_representations.shape)

    # Preprocess captions
    idx_to_word, word_to_idx, max_caption_length, total_words, num_words = get_caption_dictionaries(captions)
    print('idx_to_word', list(idx_to_word.items())[:10])
    print('word_to_idx', list(word_to_idx.items())[:10])

    ''' OUTPUT
    idx_to_word [(0, '_'), (1, 'a'), (2, 'in'), (3, 'the'), (4, 'on'), 
                (5, 'is'), (6, 'and'), (7, 'dog'), (8, 'with'), (9, 'man')]
    word_to_idx [('_', 0), ('a', 1), ('in', 2), ('the', 3), ('on', 4), 
                ('is', 5), ('and', 6), ('dog', 7), ('with', 8), ('man', 9)]
    '''

    # Store dictionaries
    idx_to_word_output_path = os.path.join(output_filepath, "idx_to_word.pkl")
    word_to_idx_output_path = os.path.join(output_filepath, "word_to_idx.pkl")
    pickle.dump(idx_to_word, open(idx_to_word_output_path, 'wb'))
    pickle.dump(word_to_idx, open(word_to_idx_output_path, 'wb'))

    # Split data into train, test, and validation 
    images_train, images_test, images_val = train_test_val_split(images)
    image_representations_train, image_representations_test, image_representations_val = train_test_val_split(image_representations)
    captions_train, captions_test, captions_val = train_test_val_split(captions)

    # Format representations and captions as matrices
    image_representations_train, captions_train = format_as_matrix(image_representations_train, captions_train, max_caption_length, word_to_idx)
    image_representations_test, captions_test = format_as_matrix(image_representations_test, captions_test, max_caption_length, word_to_idx)
    image_representations_val, captions_val = format_as_matrix(image_representations_val, captions_val, max_caption_length, word_to_idx)

    # Store images, image_representations, and captions
    pickle.dump(images_train, open(os.path.join(output_filepath, "images_train.pkl"), 'wb'))
    pickle.dump(images_test, open(os.path.join(output_filepath, "images_test.pkl"), 'wb'))
    pickle.dump(images_val, open(os.path.join(output_filepath, "images_val.pkl"), 'wb'))

    pickle.dump(image_representations_train, open(os.path.join(output_filepath, "image_representations_train.pkl"), 'wb'))
    pickle.dump(image_representations_test, open(os.path.join(output_filepath, "image_representations_test.pkl"), 'wb'))
    pickle.dump(image_representations_val, open(os.path.join(output_filepath, "image_representations_val.pkl"), 'wb'))

    pickle.dump(captions_train, open(os.path.join(output_filepath, "captions_train.pkl"), 'wb'))
    pickle.dump(captions_test, open(os.path.join(output_filepath, "captions_test.pkl"), 'wb'))
    pickle.dump(captions_val, open(os.path.join(output_filepath, "captions_val.pkl"), 'wb'))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
