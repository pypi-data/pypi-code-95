from sklearn.model_selection import train_test_split
import numpy as np

def train_test_val_split(data, save: bool = False):

    X_train, X_test = train_test_split(data, test_size=1000, random_state=42, shuffle=True)
    X_train, X_val = train_test_split(X_train, test_size=1000, random_state=42, shuffle=True)

    return X_train, X_test, X_val
    
'''
format_as_matrix() given by the instructor.
'''
def format_as_matrix(representations, captions, max_caption_length, word_to_idx):
        if representations.shape[0] != len(captions):
            raise AssertionError("Different number of representations and captions.")
        
        N = representations.shape[0]
        duplicate_representations = None
        labels = None
        for k in range(5):
            cur_labels = np.zeros((N, max_caption_length), dtype=np.uint32)
            for l in range(N):
                for count, w in enumerate(captions[l][k]):
                    cur_labels[l, count] = word_to_idx[w]

            if duplicate_representations is None:
                duplicate_representations = representations
                labels = cur_labels
            else:
                duplicate_representations = np.concatenate((duplicate_representations, representations), 0)
                labels = np.concatenate((labels, cur_labels), 0)
        
        return duplicate_representations, labels