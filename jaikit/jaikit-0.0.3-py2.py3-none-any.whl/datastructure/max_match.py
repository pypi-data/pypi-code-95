from typing import Dict

from jaikit.datastructure.trie import Trie


class MaxMatchTranslate:
    """
    按照正向最大匹配的原则，将文本中的词对照translate_map映射表进行翻译替换
    """
    def __init__(self, translate_map: Dict[str, str]):
        self.translate_map = translate_map
        self.max_len = max([len(item) for item in self.translate_map])
        self.trie = Trie()
        for word in self.translate_map:
            self.trie.insert(word)

    def max_match_translate(self, text: str):
        start = 0
        result = ""
        while start < len(text):
            match_window_len = 0
            match_word = ""
            for cur in range(1, self.max_len + 1):
                if start + cur > len(text):
                    break
                window = text[start : start + cur]
                if self.trie.search(window):
                    match_window_len = cur
                    match_word = window
            if match_window_len > 0:
                start += match_window_len
                result += self.translate_map[match_word]
            else:
                start += 1
                result += text[start - 1]
        return result
