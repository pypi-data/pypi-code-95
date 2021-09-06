# -*- coding: utf-8 -*-
#
#    TypeAtlas Block Math
#    Copyright (C) 2018-2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas libraries)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#

"""A library that allows one to perform basic operations on discrete blocks
of e.g. codepoints defined by first and last number. They are simple,
defined by (lists of) two-element tuples. For more complex
operations, look in the rangemath module."""

from itertools import chain
from collections import namedtuple
from operator import itemgetter
from typeatlas.util import generic_type
import bisect


Union = generic_type('Union')
Optional = generic_type('Optional')
TupleOf = generic_type('Tuple')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')


class _BlockLikeMeta(type):

    def __instancecheck__(cls, instance):
        return (isinstance(instance, tuple) and
                len(instance) >= 2 and (isinstance(x, int) for x in instance[:2]))

    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, tuple)


class BlockLike(metaclass=_BlockLikeMeta):
    """A tuple of at least two integer arguments, specifying start and
    end."""

    def __init__(self):
        raise TypeError

Block = namedtuple('Block', 'start end')


_UNSPECIFIED = object()


def iterblock(block: BlockLike) -> IteratorOf[int]:
    """Iterate over the indexes (e.g. characters) inside any block
    described by a (start, end) inclusive tuple"""
    return range(block[0], block[1] + 1)


def iterblocks(blocks: IterableOf[BlockLike]) -> IteratorOf[int]:
    """Iterate over the indexes (e.g. characters) inside an iterable
    of blocks  described by a (start, end) inclusive tuples."""
    return chain.from_iterable(range(block[0], block[1] + 1)
                               for block in blocks)


def blocklen(block: BlockLike) -> int:
    """Return the length of a block"""
    return block[1] - block[0] + 1


def blockslen(blocks: IterableOf[BlockLike]) -> int:
    """Return the length of a block"""
    return sum(block[1] - block[0] + 1 for block in blocks)


def toblocks_inorder(values: IterableOf[int]) -> IteratorOf[BlockLike]:
    """Like toblocks, but does not sort. This can be an optimisation if
    the values are already sorted, or if you're doing something unusual
    (e.g. finding the continuous blocks in an unordered sequence)"""

    start = None
    end = None

    for i in values:
        if end != i - 1:
            if start is not None:
                yield Block(start, end)
            start = i
        end = i

    if start is not None:
        yield Block(start, end)


def have_intersection(a: BlockLike, b: BlockLike) -> bool:
    """Return True if the two blocks have an intersection."""

    # Verify both implementations work

    astart = a[0]
    aend = a[1]

    bstart = b[0]
    bend = b[1]

    # No need to check if bstart <= aend <= bend, as then either
    # bstart <= astart <= bend or astart <= bstart <= aend.
    return (astart <= bstart <= aend or astart <= bend <= aend or 
            bstart <= astart <= bend)


def intersection(a: BlockLike, b: BlockLike,
                 default=_UNSPECIFIED) -> Optional[BlockLike]:
    """Return the intersection of the two blocks."""

    start = max(a[0], b[0])
    end = min(a[1], b[1])

    if start <= end:
        return Block(start, end)

    if default is _UNSPECIFIED:
        raise ValueError("blocks have no intersection")
    return default


def toblocks(values: IterableOf[int]) -> IteratorOf[BlockLike]:
    """Turn an unsorted sequence of integers into a sequence of 
    Block named tuples describing the start and end (inclusive)
    of the continuous numbers."""
    return toblocks_inorder(sorted(values))


OverlapTuple = TupleOf[BlockLike, BlockLike, BlockLike]

#def overlapping_blocks(aseq: IterableOf[int],
#                       bseq: IterableOf[int]) -> IteratorOf[OverlapTuple]:
#    """Return an iterable of overlapping blocks from the aseq and bseq,
#    as a tuple of (a, b, overlap), where a is a block from aseq, b is 
#    a block from bseq, and overlap is a block with their overlap."""
#
#    aseq = sorted(aseq)
#    astarts = list(map(itemgetter(0), aseq))
#    aends = list(map(itemgetter(1), aseq))
#    bseq = sorted(bseq)
#
#    for b in bseq:
#        bstart = b[0]
#        bend = b[1]
#
#        #i = bisect.bisect_right(astarts, bstart) - 1
#        #j = bisect.bisect_left(aends, bend) + 1
#        
#        i = bisect.bisect_left(bends, astart)
#        j = bisect.bisect_right(bstarts, aend)
#
#        for a in aseq[i:j]:
#            overlap = intersection(a, b)
#            if overlap is not None:
#                yield a, b, overlap


def overlapping_blocks(aseq: IterableOf[BlockLike],
                       bseq: IterableOf[BlockLike],
                       asymmetric: bool=False
                       ) -> IteratorOf[Union[BlockLike, OverlapTuple]]:

    """Return an iterable of overlapping blocks from the aseq and bseq,
    as a tuple of (a, b, overlap), where a is a block from aseq, b is 
    a block from bseq, and overlap is a block with their overlap.
    
    If asymmetric is True, only return the blocks from aseq that 
    overlap with some block from bseq. In other words, aseq is a haystack, 
    and bseq is a sequence of needles to locate the blocks from the 
    haystack."""

    aseq = sorted(aseq)
    bseq = sorted(bseq)
    bstarts = list(map(itemgetter(0), bseq))
    bends = list(map(itemgetter(1), bseq))

    for a in aseq:
        astart = a[0]
        aend = a[1]

        ## These are very wrong, but I'm keeping to figure out why I thought
        ## this would ever make sense.
        #i = bisect.bisect_right(bstarts, astart) - 1
        #j = bisect.bisect_left(bends, aend) + 1

        i = bisect.bisect_left(bends, astart)
        j = bisect.bisect_right(bstarts, aend)

        for b in bseq[i:j]:
            overlap = intersection(a, b, None)
            if overlap is not None:
                if asymmetric:
                    yield a
                    break
                yield a, b, overlap


def intersect_many(aseq: IterableOf[BlockLike],
                   bseq: IterableOf[BlockLike]) -> IteratorOf[BlockLike]:
    """Return the intersection of the two sequences of blocks.

    This is used to unit test overlap() and overlapping_blocks() in
    one go. For this complex an operation, rangemath may be more useful.
    """
    yield from map(itemgetter(2), overlapping_blocks(aseq, bseq))


def union(*block_sequences: IterableOf[BlockLike],
          merge_adjacent: bool=True) -> IteratorOf[BlockLike]:
    """Given a few block sequences, yield a single block iterable
    with the union of all blocks. You can also pass a single
    sequence of overlapping blocks, and the function will still work.


    Adjacent blocks will be merged, unless you pass merge_adjacent=True.
    """

    blocks = sorted(chain.from_iterable(block_sequences))

    adjoff = 1 if merge_adjacent else 0

    i = 0

    while i < len(blocks):
        start = blocks[i][0]
        end = blocks[i][1]

        # Until the next block overlaps, merge with the current one, and
        # skip it in the main loop.
        for j in range(i + 1, len(blocks)):

            # To return the promised result, we only need to break when the
            # start of the next is larger than the end, but if also keep
            # going when the start is right next to the end, we'd also merge
            # adjacent blocks.
            if blocks[j][0] > end + adjoff:
                break
            end = max(end, blocks[j][1])
            i += 1

        i += 1

        yield Block(start, end)
