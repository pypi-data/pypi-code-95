import unicodedata


CJK_Char_LIST = [
    [range(13312, 19893), "CJK Unified Ideographs Extension A 3.0"],
    [range(19968, 40869), "CJK Unified Ideographs 1.1"],
    [range(40870, 40891), "CJK Unified Ideographs 4.1"],
    [range(40892, 40899), "CJK Unified Ideographs 5.1"],
    [range(40900, 40907), "CJK Unified Ideographs 5.2"],
    [range(40908, 40909), "CJK Unified Ideographs 6.1"],
    [range(40909, 40917), "CJK Unified Ideographs 8.0"],
    [range(40918, 40938), "CJK Unified Ideographs 10.0"],
    [range(40939, 40943), "CJK Unified Ideographs 11.0"],
    [range(63744, 64045), "CJK Compatibility Ideographs 1.1"],
    [range(64046, 64047), "CJK Compatibility Ideographs 6.1"],
    [range(64048, 64106), "CJK Compatibility Ideographs 3.2"],
    [range(64107, 64109), "CJK Compatibility Ideographs 5.2"],
    [range(64112, 64217), "CJK Compatibility Ideographs 4.1"],
    [range(131072, 173782), "CJK Unified Ideographs Extension B 3.1"],
    [range(173824, 177972), "CJK Unified Ideographs Extension C 5.2"],
    [range(177984, 178205), "CJK Unified Ideographs Extension D 6.0"],
    [range(178208, 183983), "CJK Unified Ideographs Extension E 8.0"],
    [range(183984, 191456), "CJK Unified Ideographs Extension F 10.0"],
    [range(194560, 195101), "CJK Compatibility Supplement 3.1"],
    [range(11904, 11929), "CJK Radicals Supplement 3.0"],
    [range(11931, 12019), "CJK Radicals Supplement 3.0"],
    [range(12032, 12245), "Kangxi Radicals 3.0"],
    [range(12272, 12283), "Ideographic Description Characters 3.0"],
    [range(12288, 12343), "CJK Symbols and Punctuation 1.1"],
    [range(12344, 12346), "CJK Symbols and Punctuation 3.0"],
    [range(12347, 12349), "CJK Symbols and Punctuation 3.2"],
    [range(12350, 12351), "CJK Symbols and Punctuation 3.0"],
    [range(12351, 12352), "CJK Symbols and Punctuation 1.1"],
    [range(12549, 12588), "Bopomofo 1.1"],
    [range(12589, 12590), "Bopomofo 5.1"],
    [range(12688, 12703), "Kanbun 1.1"],
    [range(12704, 12727), "Bopomofo Extended 3.0"],
    [range(12736, 12751), "CJK Strokes 4.1"],
    [range(12752, 12771), "CJK Strokes 5.1"],
    [range(12832, 12867), "Enclosed CJK Letters and Months 1.1"],
    [range(12928, 12976), "Enclosed CJK Letters and Months 1.1"],
    [range(12992, 13003), "Enclosed CJK Letters and Months 1.1"],
    [range(13144, 13168), "CJK Compatibility 1.1"],
    [range(13179, 13183), "CJK Compatibility 1.1"],
    [range(13280, 13310), "CJK Compatibility 1.1"],
]


def CJK_detail(Character):
    try:
        Udata = unicodedata.name(Character)
    except:
        Udata = ""
    for _ in CJK_Char_LIST:
        if ord(Character) in _[0]:
            return ord(Character), _[1], Udata
    return ord(Character), "Not CJK", Udata
