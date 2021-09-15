#!/usr/bin/env python3
from multiprocessing.shared_memory import ShareableList
from functools import lru_cache
import sys
from pathlib import Path
from nokogiri.tqdm_load import tqdm_load

"""
【目的】
新しいノートブックを立ち上げた時にpickleをloadする無駄な時間を削減すべく、
あらかじめ立ち上げておいたプロセスから共有メモリを介して利用できるようにします。

【使用方法】
あらかじめ別の端末から
python -m nokogiri.shared_map /path/to/*.pkl
を実行してください。

次に別のnotebookやPythonプログラムから次のようにインスタンス化してください。
from nokogiri.shared_map import shared_map
sm = shared_map("/path/to")

/path/to/hoge.pklといったファイルが存在する場合は、
for x in tqdm(range(100)):
    y = sm.hoge(x)
などsm.ファイル名で関数のように利用できます。
事前に立ち上げた共有メモリを利用しているため、loadの時間はゼロです。
初回アクセスでも20it/s~40it/sの速度が出ます。さらに、メモ化されるため、
二回目のアクセスは通常の辞書へのアクセスと同等の速度が出ます。
しかし、全体をスキャンするなどの大量のアクセスが必要な場合は、
sm.hoge.load()
を実行することでpickleをloadし今までと変わらず使うことができます。

デフォルトではlistのように区間 0,1, … len(sm.hoge)-1 を定義域としたMapを提供しますが、
fuga = ["f", "u", "g", "a"]
fuga_inv = {fuga[i]:i for i in range(fuga)}
といった、座標圧縮のデータを用意し、
sm.hoge.input = fuga_inv.get
などのように入力時に前処理を行う関数を置き換えることで
sm.hoge("f")
などと数値以外を定義域としたMapを表現することができます。
使用できるpickleは下記の制約を受けるため値域に制約がかかります、そのため
sm.hoge.output = lambda x: x.split()
このように出力前に後処理を行う関数を置き換えることで配列などを値域とするMapが表現できます。

※注意：使用するpickleは
https://docs.python.org/3/library/multiprocessing.shared_memory.html#multiprocessing.managers.SharedMemoryManager.ShareableList
「multiprocessing.shared_memory.ShareableList」の制約を満たす必要があります。
"""

class inner_map:
    def __init__(self, listlike, name, parent):
        self.listlike = listlike
        self.input = int
        self.output = lambda x: x
        self.name = name
        self.parent = parent
    @lru_cache(maxsize=None)
    def __call__(self, x):
        x = self.input(x)
        x = self.listlike[x]
        x = self.output(x)
        return x
    def load(self):
        return self.parent._load(self.name)

class shared_map:
    def __init__(self, root):
        self.root = Path(root)
        self.sharedlists = dict()
        self.pickles = dict()

    def __getattr__(self, name):
        if name in self.pickles:
            return self.pickles[name]
        if name in self.sharedlists:
            return self.sharedlists[name]
        try:
            self.sharedlists[name] = inner_map(
                ShareableList(name=name),
                name,
                self,
            )
            return self.sharedlists[name]
        except FileNotFoundError:
            print(f"{name}: shared_map not found")
            print(f"try, variable.{name}.load()")

    def _load(self, name):
        self.pickles[name] = inner_map(
                tqdm_load(self.root/f"{name}.pkl"),
                name,
                self,
            )

def release(name):
    try:
        sl = ShareableList(name=name)
        sl.shm.close()
        sl.shm.unlink()
        del sl
        print(f"{name}: shared_map released")
    except FileNotFoundError:
        print(f"{name}: shared_map not found")

if __name__ == "__main__":
    sl = dict()
    for path in map(Path, sys.argv[1:]):
        name = path.stem
        arr = tqdm_load(path)
        release(name)
        sl[name] = ShareableList(arr, name=name)
    while input("Type yes to exit > ") != "yes":
        pass
    for name in sl:
        release(name)