from pathlib import Path
import os
import pickle

# globals
data_folder = Path("data/processed/")
model_folder = Path("models/")

def load_train():
    image_representations_train = pickle.load(
        open(os.path.join(data_folder, "image_representations_train.pkl"), 'rb'))
    captions_train = pickle.load(
        open(os.path.join(data_folder, "captions_train.pkl"), 'rb'))  
    images_train = pickle.load(
        open(os.path.join(data_folder, "images_train.pkl"), 'rb'))  
    return image_representations_train, captions_train, images_train

def load_val():
    image_representations_val = pickle.load(
        open(os.path.join(data_folder, "image_representations_val.pkl"), 'rb'))
    captions_val = pickle.load(
        open(os.path.join(data_folder, "captions_val.pkl"), 'rb')) 
    images_val = pickle.load(
        open(os.path.join(data_folder, "images_val.pkl"), 'rb'))  
    return image_representations_val, captions_val, images_val

def load_test():
    image_representations_test = pickle.load(
        open(os.path.join(data_folder, "image_representations_test.pkl"), 'rb'))
    captions_test = pickle.load(
        open(os.path.join(data_folder, "captions_test.pkl"), 'rb')) 
    images_test = pickle.load(
        open(os.path.join(data_folder, "images_test.pkl"), 'rb'))  
    return image_representations_test, captions_test, images_test

def load_idx_word_dicts():
    idx_to_word = pickle.load(open(os.path.join(data_folder, "idx_to_word.pkl"), 'rb'))
    word_to_inx = pickle.load(open(os.path.join(data_folder, "word_to_idx.pkl"), 'rb'))
    return idx_to_word, word_to_inx

def load_predictions():
    return pickle.load(open(os.path.join(data_folder, "predictions_word_test.pkl"), 'rb'))
    

if __name__ == "__main__":
    image_representations_train, captions_train, images_train = load_train()
    image_representations_val, captions_val, images_val = load_val()
    image_representations_test, captions_test, images_test = load_test()
    print("Train representations {}, captions {}, images {}".format(image_representations_train.shape, captions_train.shape, images_train.shape))
    print("Validation representations {}, captions {}, images {}".format(image_representations_val.shape, captions_val.shape, images_val.shape))
    print("Test representations {}, captions {}, images {}".format(image_representations_test.shape, captions_test.shape, images_test.shape))

    idx, word = load_idx_word_dicts()
    print("First 5 ind_to_word pairs {}".format(list(idx.items())[:5]))
    print("First 5 word_to_idx pairs {}".format(list(word.items())[:5]))

    predictions = load_predictions()
    print("{} Predictions".format(len(predictions)))


