class ScoreConfig:

    def __init__(self):
        # 読みが同じ時にかける値
        self.same_yomi_scale = 1.2
        # 出現数の差の正規化数([0,1])にかける値
        self.occurrences_sacle = 1.0
        # 読みが同じかつ、長音が消えてる場合にかける値
        self.same_yomi_with_remove_long_vowel_scale = 0.8
        # 片方を内包し、末尾の長音の差分のみの場合にかける値
        self.diff_only_long_vowel_scale = 1.2
        # 片方を内包している場合にかける値
        self.inclue_other_one = 0.5


score_config = ScoreConfig()
