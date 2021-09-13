''' This file is for preprocessing all of the different geese images I used for creating the model to train off of.'''
import cv2 as cv
import os
import json
import random
import argparse

from pytorch_vision_utils.Utilities import clear_dirs, random_sampling


parser = argparse.ArgumentParser(description="Adds more customization for the dataset.")
parser.add_argument("--num_of_images", "-n", type=int, required=False, default=5000)
parser.add_argument("--rebalance", "-r", type=str, required=False, default="True")
parser.add_argument("--debug", "-d", type=str, required=False, default="True")
parser.add_argument("--train", "-t", type=str, required=False, default="True")
parser.add_argument("--parameters_path", "-c", type=str, required=False, default="config.json")
args = parser.parse_args().__dict__
num_of_images = args["num_of_images"]
rebalance = args["rebalance"] == "True"
debug = args["debug"] == "True"
train = args["train"] == "True"
parameters_path = args["parameters_path"]

curPATH = os.getcwd()
with open(parameters_path, "r") as f:
    classes = json.load(f)["CLASSES"]
    PATHS = [classes[c].lower()+'/' for c in classes]
    


PRE_PATH = '../unformatted_data/' if train else '../unformatted_test_data/'
POST_PATH = '../data/' if train else '../test_data/'
print("num_of_images:", num_of_images, "rebalance:", rebalance, "debug:",  debug, "train mode:", train, "parameters_path": parameters_path, "classes:", classes)

for PATH in PATHS:
    try:
        os.makedirs(curPATH+'/'+POST_PATH+PATH)
    except FileExistsError:
        continue


def get_prefix(num):
    ''' Used to create the numbering for the files.'''
    
    length = 6
    prepend = '0' * (length - len(str(num)))
    return prepend


def process_images(num_of_images, path, rebalance=True, debug=False):
    ''' Processes all of the images, and puts them into the training and testing folders.'''
    
    dataset = dict(zip(range(len(PATHS)), [list() for i in range(len(PATHS))]))
    for idx, DIR in enumerate(PATHS):
        prPATH = PRE_PATH + DIR

        print(f"Loading images from {DIR[:-1]}")
        for img in os.listdir(prPATH):
            f = os.path.join(prPATH, img)
            old_file = cv.imread(f)
            old_file = cv.resize(old_file, (300, 300))
            dataset[idx].append(old_file)
            
    if rebalance:
        print("Loaded images. Starting random sampling...")
        dataset = random_sampling(dataset, num_of_images=num_of_images)
        print(f"Random sampling completed.")
        
    else:
        print("Loaded images.")
        
    num = 1
    start = 0
    end = num_of_images
    
    clear_dirs(path)
    for idx, DIR in enumerate(PATHS):
        poPATH = POST_PATH + DIR
        print(f"Saving images to {poPATH}")
        
        if rebalance:
            for img in dataset[start:end]:
                prefix = get_prefix(num) + str(num)
                cv.imwrite(os.path.join(poPATH, prefix +'.jpg'), img)
                if debug:
                    print(os.path.join(poPATH, prefix +'.jpg'))
                num += 1
                
            start = end
            end += num_of_images
                
                  
        else:
            for jdx, img in enumerate(dataset[idx]):
                prefix = get_prefix(num) + str(num)
                cv.imwrite(os.path.join(poPATH, prefix +'.jpg'), img)
                if debug:
                    print(os.path.join(poPATH, prefix +'.jpg'))
                num += 1               


        num = 1
        
      
    if rebalance:
          print(f"{len(dataset)} images loaded")
          
    else:
        s = sum([len(dataset[idx]) for idx in range(len(dataset))]) 
        print(f"{s} images loaded")


if __name__ == "__main__":
    process_images(args["num_of_images"], POST_PATH, rebalance=rebalance, debug=debug)