import locale


def number_format(num, places=0):
    return locale.format_string("%.*f", (places, num), True)


def get_amount_uni(amount, reverse=False):
    exp = 18
    if reverse:
        exp = -18
    numb = amount * pow(10, exp)
    prepared_num = number_format(numb, 0)
    return prepared_num


def from_words(words):
    res = convert(words, 5, 8, False)
    return res


def convert(data, in_bits, out_bits, pad):
    value = 0
    bits = 0
    max_v = (1 << out_bits) - 1

    result = []
    i = 0
    while i < len(data):
        value = (value << in_bits) | data[i]
        bits += in_bits

        while bits >= out_bits:
            bits -= out_bits
            result.append((value >> bits) & max_v)
        i += 1

    if pad:
        if bits > 0:
            result.append((value << (out_bits - bits)) & max_v)
    else:
        if bits >= in_bits:
            return 'Excess padding'
        if (value << (out_bits - bits)) & max_v:
            return 'Non-zero padding'

    return result
