from string import ascii_letters


def split_by_symbol(expression):

    num_list = []
    num = ""

    for char in expression:
        if char.isdigit() or char in ascii_letters:
            num += char

        else:
            num_list.append(num)
            num_list.append(char)

            num = ""
    if num:
        num_list.append(num)

    return list(filter(lambda x: x, num_list))