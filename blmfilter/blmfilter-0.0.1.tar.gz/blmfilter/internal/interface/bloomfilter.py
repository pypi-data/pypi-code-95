# coding: utf-8
import zlib

from blmfilter.pkg.bitmap import Bitmap

__all__ = ['BloomFilter']


class BloomFilter:

    def __init__(self, bit=1024):
        self.rdm = ["@", "#", "*", "&"]  # single hash, multi key
        self.bit = bit
        self.bitmap = Bitmap(bit)

    def add(self, key: str) -> None:
        for rdm in self.rdm:
            index = zlib.crc32((key + rdm).encode()) % self.bit
            self.bitmap[index] = 1

    def check(self, key: str) -> bool:
        for rdm in self.rdm:
            index = zlib.crc32((key + rdm).encode()) % self.bit
            if self.bitmap[index] != 1:
                return False
        return True


if __name__ == '__main__':
    bf = BloomFilter()
    bf.add("element")
    assert bf.check("element") == True
    assert bf.check("random") == False
