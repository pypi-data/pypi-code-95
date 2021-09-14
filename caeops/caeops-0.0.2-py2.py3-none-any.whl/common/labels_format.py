import json


def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def labels_format(new_labels):
    # Convert the input inti json format
    new_labels = new_labels.replace("=", ":")
    new_labels = new_labels.replace("[", "")
    new_labels = new_labels.replace("]", "")
    count1 = new_labels.count("{")
    count2 = new_labels.count("}")
    count3 = new_labels.count("'")
    if count1 != count2:
        raise Exception("Check input parameters format")
    if count3 > 0:
        count1 == 2 * count3
    new_labels = new_labels.replace("{", "")
    new_labels = new_labels.replace("}", "")
    index = find(new_labels, ":")
    counter = 0
    for i in index:
        if counter == 0:
            new_labels = '{"' + new_labels[0:]
            new_labels = new_labels[0 : len(new_labels)] + '"}'
            counter = 2
        i = i + counter
        new_labels = (
            new_labels[0:i] + '"' + new_labels[i : i + 1] + '"' + new_labels[i + 1 :]
        )
        counter = counter + 2
    index = find(new_labels, ",")
    counter = 0
    for i in index:
        i = i + counter
        new_labels = (
            new_labels[0:i] + '"' + new_labels[i : i + 1] + '"' + new_labels[i + 1 :]
        )
        counter = counter + 2
    return new_labels
