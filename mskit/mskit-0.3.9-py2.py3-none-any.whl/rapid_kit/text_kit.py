import re

from .data_struc_kit import str_mod_to_list


def get_title2idx_dict(title_content: str) -> dict:
    title_dict = dict([(__, _) for _, __ in enumerate(
        title_content.strip('\n').split('\t'))])
    return title_dict


def combine_delimited_text(*sn: str, delimiter: str = ';', keep_order: bool = False) -> str:
    """
    This will combine two strings with semicolons and drop duplication
    Example: s1='Q1;Q2', s2='Q2;Q3' -> 'Q1;Q2;Q3'
    Note that the order may change if keep_order=False
    """
    s_list = map(lambda _: _.strip(delimiter).split(delimiter), sn)
    flatten_s = list(filter(lambda x: True if x else False, sum(s_list, [])))
    unique_s = list(set(flatten_s))
    if keep_order:
        unique_s = sorted(unique_s, key=flatten_s.index)
    return ';'.join(unique_s)


def find_substring(s: str, start_char='[', end_char=']', substring_trans_dict: dict = None):
    """
    This will find the substrings start with param "start" and end with param "end" in input "string"
    This will return
        a string with no substrings
        a list of positions of substrings (the 1-indexed)
        a list of substrings
    Example:
        substring_finder('AM(ox)M(Oxidation (M))C(Carbamidomethyl (C))DEEHC(Carb)K', '(', ')')
            ('AMMCDEEHCK',
            [2, 3, 4, 9],
            ['(ox)', '(Oxidation (M))', '(Carbamidomethyl (C))', '(Carb)'])
        substring_finder('AM[ox]M[Oxidation (M)]C[Carbamidomethyl (C)]DEEHC[Carb]K', '[', ']')
            ('AMMCDEEHCK',
            [2, 3, 4, 9],
            ['[ox]', '[Oxidation (M)]', '[Carbamidomethyl (C)]', '[Carb]'])
    TODO 再返回一个对应位点氨基酸的 list  注意 N 和 C 端
    TODO substring_trans_dict
    """
    start_num = 0
    end_num = 0
    substrings = []
    pos = []
    substring_start = False
    sub_total_len = 0
    main_str = ''
    sub_str = ''
    for i, char in enumerate(s):
        if char == start_char:
            sub_str += char
            substring_start = True
            start_num += 1
        elif char == end_char:
            sub_str += char
            end_num += 1
            if start_num == end_num:
                substrings.append(sub_str)
                sub_total_len += len(sub_str)
                pos.append(i - sub_total_len + 1)
                start_num = 0
                end_num = 0
                sub_str = ''
                substring_start = False
        else:
            if substring_start:
                sub_str += char
            else:
                main_str += char
    return main_str, pos, substrings


substring_finder = find_substring


def fillin_annotation(s, anno_pos, anno_text, existed_anno_start_char: str = None, existed_anno_end_char: str = None):
    if isinstance(anno_pos, (str, int)):
        anno_pos = [int(anno_pos)]
    if isinstance(anno_text, str):
        anno_text = [anno_text]

    if existed_anno_start_char is not None and existed_anno_end_char is not None:
        s, exist_anno_pos, exist_anno_text = find_substring(s, start_char=existed_anno_start_char, end_char=existed_anno_end_char)
    elif existed_anno_start_char is None and existed_anno_end_char is None:
        exist_anno_pos, exist_anno_text = [], []
    else:
        raise ValueError(
            'Both `existed_anno_start_char` and `existed_anno_end_char` need to be passed or set to None as default. '
            f'Now {existed_anno_start_char} and {existed_anno_end_char}'
        )

    exist_anno_pos += anno_pos
    exist_anno_text += anno_text

    t = sorted([(i, v) for i, v in enumerate(exist_anno_pos)], key=lambda x: x[1])
    anno_pos = [_[1] for _ in t]
    anno_text = [anno_text[i] for i in [_[0] for _ in t]]
    anno_s = ''
    _ = 0
    for pos_idx, pos in enumerate(anno_pos):
        anno_s += s[_: pos]
        anno_s += anno_text[pos_idx]
        _ = pos
    anno_s += s[pos:]
    return anno_s


def extract_bracket(str_with_bracket, ):  # Need a parameter to choose to use () or [] or others (by manurally define?) and a parameter to skip how many additional brackets
    bracket_start = [left_bracket.start() for left_bracket in re.finditer('\(', str_with_bracket)]  # Add [::2] if there is one additional bracket in the expected one
    bracket_end = [right_bracket.start() for right_bracket in re.finditer('\)', str_with_bracket)]  # Add [1::2] if add the additional operation at the last step
    return bracket_start, bracket_end


def split_fragment_name(fragment_name):
    frag_type, frag_num, frag_charge, frag_loss = re.findall(
        '([abcxyz])(\\d+)\\+(\\d+)-?(.*)', fragment_name)[0]
    return frag_type, int(frag_num), int(frag_charge), frag_loss


def split_prec(prec: str, keep_underline=False):
    modpep, charge = prec.split('.')
    if not keep_underline:
        modpep = modpep.replace('_', '')
    return modpep, int(charge)


def assemble_prec(modpep, charge):
    if not modpep.startswith('_'):
        modpep = f'_{modpep}_'
    return f'{modpep}.{charge}'


def split_mod(modpep, mod_ident='bracket'):
    if mod_ident == 'bracket':
        mod_ident = ('[', ']')
    elif mod_ident == 'parenthesis':
        mod_ident = ('(', ')')
    else:
        pass
    re_find_pattern = '(\\{}.+?\\{})'.format(*mod_ident)
    re_sub_pattern = '\\{}.*?\\{}'.format(*mod_ident)
    modpep = modpep.replace('_', '')
    mod_len = 0
    mod = ''
    for _ in re.finditer(re_find_pattern, modpep):
        _start, _end = _.span()
        mod += '{},{};'.format(_start - mod_len, _.group().strip(''.join(mod_ident)))
        mod_len += _end - _start
    stripped_pep = re.sub(re_sub_pattern, '', modpep)
    return stripped_pep, mod


def add_mod(pep, mod, mod_processor):
    """
    mod_process is the ModOperation class
    """
    if mod:
        if isinstance(mod, str):
            mod = str_mod_to_list(mod)
        mod = sorted(mod, key=lambda x: x[0])
        mod_pep_list = []
        prev_site_num = 0
        for mod_site, mod_name in mod:
            mod_pep_list.append(pep[prev_site_num: mod_site])
            if mod_site != 0:
                mod_aa = mod_pep_list[-1][-1]
            else:
                mod_aa = pep[0]
            mod_pep_list.append(mod_processor(mod=mod_name, aa=mod_aa))
            prev_site_num = mod_site
        mod_pep_list.append(pep[prev_site_num:])
        mod_pep = ''.join(mod_pep_list)
    else:
        mod_pep = pep
    mod_pep = f'_{mod_pep}_'
    return mod_pep


def fasta_title(title: str, title_type='uniprot'):
    title = title.lstrip('>')

    if '|' in title:
        ident = title.split('|')[1]
    else:
        ident = title.split(' ')[0]
    return ident


def join_seqtext_in_fasta(seq_text):
    return ''.join(seq_text.split('\n'))


def join_seqlines_in_fasta(seq_lines):
    return ''.join([_.strip('\n') for _ in seq_lines])
