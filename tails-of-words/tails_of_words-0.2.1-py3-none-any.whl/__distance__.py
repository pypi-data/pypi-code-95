import Levenshtein

zen2han = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})


class EditDistance:

    def __init__(self, midasi, yomi):
        self.midasi = midasi
        self.yomi = yomi


class Distance:

    def __init__(self, a, b, use_jaro_winkler):
        self.section = [a, b]
        self.use_jaro_winkler = use_jaro_winkler
        a_midasi = self.normalize(a.midasi)
        b_midasi = self.normalize(b.midasi)
        self.levenshtein = EditDistance(
            Levenshtein.distance(a_midasi, b_midasi),
            Levenshtein.distance(a.yomi, b.yomi)
        )
        # 0 : 不一致
        # 1 : 一致
        self.normalized = EditDistance(
            1.0 - (self.levenshtein.midasi / max(len(a_midasi), len(b_midasi))),
            1.0 - (self.levenshtein.yomi / max(len(a.yomi), len(b.yomi)))
        )
        self.jaro_winkler = EditDistance(
            Levenshtein.jaro_winkler(a_midasi, b_midasi),
            Levenshtein.jaro_winkler(a.yomi, b.yomi)
        )

    def normalized_distance(self):
        if self.use_jaro_winkler:
            return self.jaro_winkler
        else:
            return self.normalized

    def normalize(self, s):
        # 編集距離を取るときに正規化を行うことで距離が短いのに違う単語を検出しやすくする
        return s.translate(zen2han).lower()

    def format(self):
        if self.use_jaro_winkler:
            return "{:.2f}, {:.2f}".format(self.jaro_winkler.midasi, self.jaro_winkler.yomi)
        else:
            return "{}, {:.2f}, {:.2f}".format(self.levenshtein.midasi, self.normalized.midasi, self.normalized.yomi)
