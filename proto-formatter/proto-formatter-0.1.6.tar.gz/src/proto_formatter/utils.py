def is_word(line, target_index):
    return line[target_index + 1].lower() not in ' \n' or line[target_index - 1].lower() not in ' \n'


def find_word_start_index(line, target_index):
    index = target_index - 1
    while (True):
        if line[index].lower() in ' \n':
            return index
        index = index - 1
    return target_index


def find_word_end_index(line, target_index):
    index = target_index + 1
    while (True):
        if line[index].lower() in ' \n':
            return index
        index = index + 1
    return target_index


def to_lines(line, length):
    lines = []
    while (True):
        if not is_word(line, length - 1):
            lines.append(line[:length - 1])
            sub_line = line[:length - 1]
            line = line[length - 1:].strip()
        else:
            index = find_word_start_index(line, length - 1)
            sub_line = line[:index]
            line = line[index:].strip()

        lines.append(sub_line)
        if len(line) <= length:
            lines.append(line)
            break

    return lines


s = """In botany, a tree is a perennial plant with an elongated stem, or trunk, supporting branches and leaves in most species. In some usages, the definition of a tree may be narrower, including only wood plants with secondary growth, plants that are usable as lumber or plants above a specified height. In wider definitions, the taller palms, tree ferns, bananas, and bamboos are also trees. Trees are not a taxonomic group but include a variety of plant species that have independently evolved a trunk and branches as a way to tower above other plants to compete for sunlight. Trees tend to be long-lived, some reaching several thousand years old. Trees have been in existence for 370 million years. It is estimated that there are some three trillion mature trees in the world.[1]

A tree typically has many secondary branches supported clear of the ground by the trunk. This trunk typically contains woody tissue for strength, and vascular tissue to carry materials from one part of the tree to another. For most trees it is surrounded by a layer of bark which serves as a protective barrier. Below the ground, the roots branch and spread out widely; they serve to anchor the tree and extract moisture and nutrients from the soil. Above ground, the branches divide into smaller branches and shoots. The shoots typically bear leaves, which capture light energy and convert it into sugars by photosynthesis, providing the food for the tree's growth and development.

Trees usually reproduce using seeds. Flowers and fruit may be present, but some trees, such as conifers, instead have pollen cones and seed cones. Palms, bananas, and bamboos also produce seeds, but tree ferns produce spores instead."""
ss = to_lines(s, 50)
print('\n'.join(ss))
