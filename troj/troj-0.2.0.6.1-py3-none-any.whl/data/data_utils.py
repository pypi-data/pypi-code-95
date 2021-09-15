import os
import PIL


def DatasetFormatConverterLabelled(dset, dset_dir, split, label_id_map, extension='.jpeg', verbose=True):
    '''
    Takes in a PyTorch dataset and converts it to the Imagenet folder structure.

    :param dset: Pytorch dataset object.
    :param dset_dir: Directory to save the new dataset.
    :param split: Split name (i.e train, test, val)
    :param label_id_map: a dictionary where the keys are the names of the classes and the values are the assigned integer labels.
    :param extension: File extension to save the data with (i.e)
    :param verbose: Whether or not to print progress.
    :return: A dataset split saved at dset_dir/split.
    '''
    rev_lab_id_map = dict(zip(label_id_map.values(), label_id_map.keys()))
    if os.path.exists(dset_dir) == False:
        os.mkdir(dset_dir)
    split_dir = os.path.join(dset_dir, split)
    os.mkdir(split_dir)
    for class_name in list(label_id_map.keys()):
        class_dir = os.path.join(split_dir, class_name)
        os.mkdir(class_dir)
    tracker = 0
    for data_lab_pair in dset:
        if verbose:
            if tracker%100==0:
                print('{}/{} converted'.format(tracker, len(dset)))
        img = data_lab_pair[0]
        label = data_lab_pair[1]
        class_name = rev_lab_id_map[label]
        class_dir = os.path.join(split_dir, class_name)
        save_file = '{}_{}{}'.format(label, tracker, extension)
        save_loc = os.path.join(class_dir, save_file)
        img.save(save_loc)
        tracker += 1


def DatasetFormatConverterUnlabelled(dset, dset_dir, split='unlabeled',extension='.jpeg', verbose=True):
    '''
    Takes in a PyTorch dataset and converts it to the Imagenet folder structure, however there are no class folders.

    :param dset: Pytorch dataset object.
    :param dset_dir: Directory to save the new dataset.
    :param split: Split name (i.e train, test, val)
    :param extension: File extension to save the data with (i.e)
    :param verbose: Whether or not to print progress.
    :return: A dataset split saved at dset_dir/split.
    '''
    if os.path.exists(dset_dir) == False:
        os.mkdir(dset_dir)
    split_dir = os.path.join(dset_dir, split)
    os.mkdir(split_dir)
    tracker = 0
    for data_lab_pair in dset:
        if verbose:
            if tracker%100==0:
                print('{}/{} converted'.format(tracker, len(dset)))
        img = data_lab_pair[0]
        save_file = 'unlab_{}{}'.format(tracker, extension)
        save_loc = os.path.join(split_dir, save_file)
        img.save(save_loc)
        tracker += 1