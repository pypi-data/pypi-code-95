import pickle
from itertools import permutations
from typing import List, Tuple, Optional


def del_sub(pos_ls: List[Tuple]) -> List[Tuple]:
    """
    一个范围是另一范围的子集时，删除子集范围
    :pos_ls:原tuple列表
    :return:删除子集后的tuple列表
    """
    del_set = set()  # 要删除的子集
    for tp in list(permutations(list(range(len(pos_ls))), 2)):
        if (
            pos_ls[tp[0]][1] <= pos_ls[tp[1]][1]
            and pos_ls[tp[0]][0] >= pos_ls[tp[1]][0]
        ):  # 子集判断
            del_set.add(tp[0])  # 如果是子集，就添加
    return [_ for _idx, _ in enumerate(pos_ls) if not _idx in del_set]


class Trie:
    def __init__(self, load_path: Optional[str]=None):
        if load_path is None:
            self.root = {}
        else:
            with open(load_path, "rb") as f:
                self.root = pickle.load(f)
        self.word_end = -1

    def insert(self, word):
        curNode = self.root
        for c in word:
            if not c in curNode:
                curNode[c] = {}
            curNode = curNode[c]
        curNode[self.word_end] = True

    def search(self, word) -> bool:
        curNode = self.root
        for c in word:
            if not c in curNode:
                return False
            curNode = curNode[c]
        if self.word_end not in curNode:
            return False
        return True

    def starts_with(self, prefix) -> bool:
        curNode = self.root
        for c in prefix:
            if not c in curNode:
                return False
            curNode = curNode[c]
        return True

    def scan_item(self, target, greedy_mode=False):
        # TODO 从target中找出命中的，需要改 t.scan_item("aba") ['ab', 'ba']重复
        if not greedy_mode:
            pos_ls = []
            found_ls = []
            for _idx, _ in enumerate(target):
                if self.starts_with(_):
                    for id in range(len(target) - _idx + 1):
                        if self.search(target[_idx : _idx + id]):
                            pos_ls.append((_idx, _idx + id))
            for pos_tp in del_sub(pos_ls):
                fd = target[pos_tp[0] : pos_tp[1]]
                found_ls.append(fd)
        else:
            found_ls = []
            for _idx, _ in enumerate(target):
                if self.starts_with(_):
                    for id in range(len(target) - _idx + 1):
                        fd = target[_idx : _idx + id]
                        if self.search(fd):
                            found_ls.append(fd)
        return found_ls

    def remove_item(self, word: str) -> dict:
        """从Trie树中删除某词"""
        if not self.search(word):
            return self.root
        leaf_dict = self.root
        upper_dict = leaf_dict
        for char in word[:-1]:
            upper_dict = leaf_dict
            leaf_dict = leaf_dict[char]
        if len(leaf_dict[word[-1]]) == 1:
            leaf_dict.pop(word[-1])
            upper_dict.pop(word[-2], None)
        else:
            leaf_dict[word[-1]].pop(-1)
        return self.root
