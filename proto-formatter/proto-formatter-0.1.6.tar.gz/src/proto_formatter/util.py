def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def remove_suffix(text, suffix):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def is_word(line, target_index):
    if target_index + 1 > len(line):
        i = 0
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
        if len(line) <= length:
            lines.append(line)
            break

        if not is_word(line, length - 1):
            lines.append(line[:length - 1])
            sub_line = line[:length - 1]
            line = line[length - 1:].strip()
        else:
            index = find_word_start_index(line, length - 1)
            sub_line = line[:index]
            line = line[index:].strip()

        lines.append(sub_line)

    return lines
