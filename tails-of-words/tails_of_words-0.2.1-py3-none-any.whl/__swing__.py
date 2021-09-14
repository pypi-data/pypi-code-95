import re
import logging

from .__config__ import score_config
from .__distance__ import Distance

re_katakana = re.compile(r'[\u30A1-\u30F4ー]+')
use_jaro_winkler = False


def calc_socre_include(score, a, b):
    # 片方を含む場合はスコアダウン
    if a in b:
        # 長音ルールのゆれはスコアアップ
        if (a + "ー") == b and re_katakana.fullmatch(a):
            return score * score_config.diff_only_long_vowel_scale
        else:
            return score * score_config.inclue_other_one
    return score


def calc_score(section):
    # 編集距離が近いほどスコア大
    score = section.distance.normalized_distance().midasi
    # 出現数の差が大きいほどスコア大
    la = len(section.a.mrphs)
    lb = len(section.b.mrphs)
    ls = (1.0 - min(la,lb)/(la+lb)*2)
    score *= 1.0 + (ls * score_config.occurrences_sacle)
    # 読みが同じならスコアアップ
    if section.distance.normalized_distance().yomi >= 1.0:
        score *= score_config.same_yomi_scale
    score = calc_socre_include(score, section.a.midasi, section.b.midasi)
    score = calc_socre_include(score, section.b.midasi, section.a.midasi)
    # 読みが同じで、読みから長音が消えてる場合、スコアを下げる
    if section.a.get_rep_mrph().yomi == section.b.get_rep_mrph().yomi:
        if 'ー' not in section.a.get_rep_mrph().yomi and ('ー' in section.a.midasi or 'ー' in section.b.midasi):
            score *= score_config.same_yomi_with_remove_long_vowel_scale
    return score

class SectionPoint:

    def __init__(self, k, mrphs):
        self.midasi = k
        self.mrphs = mrphs

    def get_rep_mrph(self):
        return self.mrphs[0].mrph

    def get_rep_mrph_dict(self):
        mrph = self.get_rep_mrph()
        d = {
                "midasi": mrph.midasi,
                "yomi": mrph.yomi,
                "genkei": mrph.genkei,
                "hinsi": mrph.hinsi,
                "hinsi_id": mrph.hinsi_id,
                "bunrui": mrph.bunrui,
                "bunrui_id": mrph.bunrui_id,
                "katuyou1": mrph.katuyou1,
                "katuyou1_id": mrph.katuyou1_id,
                "katuyou2": mrph.katuyou2,
                "katuyou2_id": mrph.katuyou2_id,
                "imis": mrph.imis,
                "fstring": mrph.fstring
            }
        return d

class Section:

    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b
        self.distance = Distance(a.get_rep_mrph(), b.get_rep_mrph(), use_jaro_winkler)
        self.score = calc_score(self)

    def format(self):
        a = "{}({})".format(self.a.midasi, len(self.a.mrphs))
        b = "{}({})".format(self.b.midasi, len(self.b.mrphs))
        return "{}: {} vs {} : {:.2f}".format(self.distance.format(), a, b, self.score)


class SwingOption:

    def __init__(self, exclude_alphabet, exclude_ascii, jaro_winkler):
        self.exclude_alphabet = exclude_alphabet
        self.exclude_ascii = exclude_ascii
        self.jaro_winkler = jaro_winkler


class Swing:

    def __init__(self, option):
        global use_jaro_winkler
        self.option = option
        use_jaro_winkler = option.jaro_winkler
        self.logger = logging.getLogger(__name__)

    def distance(self, words, ids):
        inputs = {}
        for id in ids:
            if id in words.hinsi:
                target = filter(lambda x: self.target_filter(x[0], x[1]), words.hinsi[id].items())
                inputs.update(sorted(target, key=lambda x: len(x[1])))
        self.logger.debug('combinations')
        keys = list(inputs.keys())
        while len(keys) > 0:
            lhs = keys.pop(0)
            d = []
            for rhs in keys:
                a = SectionPoint(lhs, inputs[lhs])
                b = SectionPoint(rhs, inputs[rhs])
                d.append(Section(a, b))
            yield sorted(d, key=lambda x: x.distance.normalized_distance().midasi)

    def swing(self, words, ids):
        for d in self.distance(words, ids):
            yield sorted(filter(lambda x: x.score > 0, d), reverse=True, key=lambda x: x.score)

    def target_filter(self, midasi, mrphs):
        # 数値は除外
        if midasi.isnumeric():
            return False
        # 英数字も除外
        if self.option.exclude_alphabet:
            if midasi.encode('utf-8').isalnum():
                return False
        # ASCII のみは除外
        if self.option.exclude_ascii:
            if midasi.encode('utf-8').isascii():
                return False
        # 数詞は除外
        mrph = mrphs[0].mrph
        if mrph.hinsi_id == 6 and mrph.bunrui_id == 7:
            return False
        return True
