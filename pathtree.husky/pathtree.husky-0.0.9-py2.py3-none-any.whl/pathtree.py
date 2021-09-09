# -*- coding: utf-8 -*-
import logging
import pprint

printer = pprint.PrettyPrinter(indent=2)


class Leaf(object):
    def __init__(self, value, extra_data, order):
        self.extra_data = extra_data
        self.value = value
        self.order = order


def Tree(logger=logging, separate_char="/"):
    return Node({}, [], {}, 0, logger, separate_char)


class Node(object):
    def __init__(self, edges, leaf, extra_data, leaf_cnt=0,
                 logger=logging, separate_char="/"):
        self.extra_data = extra_data
        self.edges = edges
        self.leaf = leaf
        self.leaf_cnt = leaf_cnt
        self.logger = logger
        self.separate_char = separate_char

    def Add(self, path, val, extra_data=None):
        if extra_data is None:
            extra_data = {}
        if not path or not path.startswith(self.separate_char):
            self.logger.error("Path must begin with %s" % self.separate_char)
            return None, "Path must begin with %s" % self.separate_char
        self.leaf_cnt += 1
        return self.add(self.leaf_cnt, self.splitPath(path, self.separate_char),
                        val, extra_data)

    def addLeaf(self, leaf):
        if not self.leaf:
            self.leaf = []
        self.leaf.append(leaf)
        return ""

    def add(self, order, elements, val, extra_data):
        if len(elements) == 0:
            self.logger.debug("Add Leaf: %s  %s" % (val, order))
            leaf = Leaf(val, extra_data, order)
            return self.addLeaf(leaf)

        el, elements = elements[0], elements[1:]
        if el == "":
            self.logger.error("empty path elements are not allowed")
            return "empty path elements are not allowed"

        try:
            e = self.edges[el]
        except Exception as _:
            e = Node({}, [], {}, 0, self.logger)
            self.edges[el] = e
            self.logger.debug(
                "--------------- add order: %d, elements: %s, val: %s" % (
                    order, elements, val))
        return e.add(order, elements, val, extra_data)

    def Find(self, path):
        if len(path) == 0 or path[0] != self.separate_char:
            return None, None
        return self.find(self.splitPath(path, self.separate_char))

    def FindLeaf(self, path, value):
        if len(path) == 0 or path[0] != self.separate_char:
            return None, None
        leafs = self.find(self.splitPath(path, self.separate_char))
        for leaf in leafs:
            if leaf.value == value:
                return leaf
        return None

    def find(self, elements):
        leaf = None
        if len(elements) == 0:
            return self.leaf
        el, elements = elements[0], elements[1:]
        if el in self.edges:
            nextNode = self.edges[el]
            if nextNode:
                leaf = nextNode.find(elements)
        return leaf

    def FindPath(self, path):
        if len(path) == 0 or path[0] != self.separate_char:
            return None
        return self.find_path(self.splitPath(path, self.separate_char))

    def find_path(self, elements):
        target_node = None
        if not len(elements):
            return self, self

        if len(elements) == 1:
            if self.edges and elements[0] in self.edges:
                target_node = self.edges[elements[0]]
            return target_node

        el, elements = elements[0], elements[1:]
        if el in self.edges:
            nextNode = self.edges[el]
            if nextNode:
                target_node = nextNode.find_path(elements)
        return target_node

    def DeleteLeaf(self, path, value):
        if len(path) == 0 or path[0] != self.separate_char:
            return None, None
        leaf, target_node = self.delete_leaf(
            self.splitPath(path, self.separate_char), value)
        return leaf, target_node

    @staticmethod
    def pop_leaf(leafs, target_leaf):
        if leafs and target_leaf and target_leaf in leafs:
            leafs.pop(leafs.index(target_leaf))

    def delete_leaf(self, elements, value):
        leaf = None
        target_node = None
        expansions = list()
        if len(elements) == 0:
            matched_leaf = self.matchLeaf(self.leaf, value)
            if matched_leaf:
                target_node = self
                self.pop_leaf(self.leaf, matched_leaf)
            return self.leaf, target_node

        el, elements = elements[0], elements[1:]
        if el in self.edges:
            nextNode = self.edges[el]
            if nextNode:
                leaf, target_node = nextNode.delete_leaf(elements, value)
                if expansions:
                    if leaf and not isinstance(leaf, list):
                        leaf = [leaf]

                matched_leaf = self.matchLeaf(leaf, value)
                if matched_leaf:
                    target_node = nextNode
                    self.pop_leaf(nextNode.leaf, matched_leaf)
                    self.pop_leaf(leaf, matched_leaf)
                    return leaf, target_node
        return leaf, target_node

    def DeletePath(self, path):
        if not path or path == self.separate_char or path[0] != self.separate_char:
            self.logger.error("path %s is invalid")
            return None, None
        target_node, father_node = self.delete_path(
            self.splitPath(path, self.separate_char))
        return target_node, father_node

    def delete_path(self, elements):
        father_node = self
        target_node = None
        if len(elements) == 1:
            if self.edges and elements[0] in self.edges:
                self.edges.pop(elements[0])
            return father_node.edges, father_node

        el, elements = elements[0], elements[1:]
        if el in self.edges:
            nextNode = self.edges[el]
            if nextNode:
                target_node, father_node = nextNode.delete_path(elements)
        return target_node, father_node

    def SetPathExtraData(self, path, extra_data):
        node = self.FindPath(path)
        if node:
            node.extra_data = extra_data
            return True
        return False

    @staticmethod
    def matchLeaf(leafs, value):
        for leaf in leafs:
            if leaf and leaf.value == value:
                return leaf
        return None

    @staticmethod
    def maxOrderLeaf(*leafs_list):
        temp = {}
        for leafs in leafs_list:
            for leaf in leafs:
                if leaf:
                    temp[leaf.order] = leaf
        return sorted(temp.items(), key=lambda t: t[0], reverse=True)[0][1]

    @staticmethod
    def extensionForPath(path):
        try:
            dotPosition = path.rindex(".")
            if dotPosition != -1:
                return path[:dotPosition], path[dotPosition:]
        except Exception as e:
            return "", ""

    @staticmethod
    def splitPath(path, separate_char="/"):
        elements = path.split(separate_char)
        if elements[0] == "":
            elements = elements[1:]
        if elements[len(elements) - 1] == "":
            elements = elements[:len(elements) - 1]
        return elements

    def stripExtensionFromLastSegment(self, segments):
        if len(segments) == 0:
            return ""
        lastSegment = segments[len(segments) - 1]
        prefix, extension = self.extensionForPath(lastSegment)
        if extension != "":
            segments[len(segments) - 1] = prefix
        return extension

    @staticmethod
    def showObj(obj):
        printer.pprint(obj.__dict__)
        print("----------------------------------------------")

    @staticmethod
    def listUnique(v):
        if not v:
            return list()
        v_unique = list(set(v))
        v_unique.sort(key=v.index)
        return v_unique

    @staticmethod
    def contain(list_a, list_b):
        """return if list a contain list b """
        ret = [False for i in list_b if i not in list_a]
        return False if ret else True

    def makepath(self, *args):
        return self.separate_char.join(args)


def found(n, p, val):
    leafs = n.Find(p)
    if not leafs:
        print("Didn't find: %s" % p)
        return False

    for leaf in leafs:
        if leaf.value == val:
            return True

    for leaf in leafs:
        if leaf.value != val:
            print("%s: value (actual) %s != %s (expected)" % (
                p, leaf.value, val))
    return False


def notfound(n, p, value=None):
    leafs = n.Find(p)
    if leafs:
        for leaf in leafs:
            if leaf.value == value:
                print("Should not have found: %s" % p)
                return False
    return True


def found_path(n, path):
    node = n.FindPath(path)
    if not node:
        print("%s not found != found (expected)")


def notfound_path(n, path):
    node = n.FindPath(path)
    if node:
        print("Should not have found path: %s" % path)


def Testing():
    print("\n============ TestColon ============")
    n = Tree()
    n.Add("/", "root", extra_data={"test": "just a test"})
    n.Add("/", "root1")

    n.Add("/a", None)
    n.Add("/a", "a")
    n.Add("/a", "aa")
    n.Add("/a", "aaa")

    n.Add("/a/b", "b")
    n.Add("/a/b", "bb")
    n.Add("/a/b", "bbb")

    n.Add("/a/b/c", "c")
    n.Add("/a/b/c", "cc")
    n.Add("/a/b/c", "ccc")

    n.Add("/a/d", "d")
    n.Add("/a/d", "dd")
    n.Add("/a/d", "ddd")

    n.Add("/a/d/e", "e")
    n.Add("/a/d/e", "ee")
    n.Add("/a/d/e", "eee")

    n.Add("/f/g/h", "h")
    n.Add("/f/g/h", "hh")
    n.Add("/f/g/h", "hhh")

    n.SetPathExtraData("/a", {"test": "hi"})

    found(n, "/", "root")
    found(n, "/", "root1")
    found(n, "/a", None)
    found(n, "/a", "a")
    found(n, "/a", "aa")
    found(n, "/a", "aaa")
    found(n, "/a/b", "b")
    found(n, "/a/b", "bb")
    found(n, "/a/b", "bbb")
    found(n, "/a/b/c", "c")
    found(n, "/a/b/c", "cc")
    found(n, "/a/b/c", "ccc")
    found(n, "/a/d", "d")
    found(n, "/a/d", "dd")
    found(n, "/a/d", "ddd")
    found(n, "/a/d/e", "e")
    found(n, "/a/d/e", "ee")
    found(n, "/a/d/e", "eee")
    found(n, "/f/g/h", "h")
    found(n, "/f/g/h", "hh")
    found(n, "/f/g/h", "hhh")

    notfound(n, "/a", "!a")
    notfound(n, "/a/e", "!a")

    n.DeleteLeaf("/", "root")
    notfound(n, "/", "root")

    n.DeleteLeaf("/a", "a")
    notfound(n, "/a", "a")
    found(n, "/a", "aa")
    found(n, "/a", "aaa")

    n.DeleteLeaf("/a/b", "b")
    notfound(n, "/a/b", "b")
    found(n, "/a/b", "bb")
    found(n, "/a/b", "bbb")

    n.DeleteLeaf("/a/b", "b")
    notfound(n, "/a/g/h", "h")

    n.DeletePath("/a")
    notfound_path(n, "/a")
    notfound_path(n, "/a/b")
    notfound_path(n, "/a/b/c")
    notfound_path(n, "/a/d")
    notfound_path(n, "/a/d/e")

    n.DeletePath("/f/g/h")
    notfound_path(n, "/f/g/h")
    found_path(n, "/f")
    found_path(n, "/f/g")

    n.DeletePath("/f")
    notfound_path(n, "/f")
    notfound_path(n, "/f/g")
    notfound_path(n, "/f/g/h")


def Testing_other_split_char():
    print("\n============ TestColon With Other Split Char  ============")
    n = Tree(separate_char="|")
    n.Add("|", "root", extra_data={"test": "just a test"})
    n.Add("|", "root1")

    n.Add("|a", None)
    n.Add("|a", "a")
    n.Add("|a", "aa")
    n.Add("|a", "aaa")

    n.Add("|a|b", "b")
    n.Add("|a|b", "bb")
    n.Add("|a|b", "bbb")

    n.Add("|a|b|c", "c")
    n.Add("|a|b|c", "cc")
    n.Add("|a|b|c", "ccc")

    n.Add("|a|d", "d")
    n.Add("|a|d", "dd")
    n.Add("|a|d", "ddd")

    n.Add("|a|d|e", "e")
    n.Add("|a|d|e", "ee")
    n.Add("|a|d|e", "eee")

    n.Add("|f|g|h", "h")
    n.Add("|f|g|h", "hh")
    n.Add("|f|g|h", "hhh")

    n.SetPathExtraData("|a", {"test": "hi"})

    found(n, "|", "root")
    found(n, "|", "root1")
    found(n, "|a", None)
    found(n, "|a", "a")
    found(n, "|a", "aa")
    found(n, "|a", "aaa")
    found(n, "|a|b", "b")
    found(n, "|a|b", "bb")
    found(n, "|a|b", "bbb")
    found(n, "|a|b|c", "c")
    found(n, "|a|b|c", "cc")
    found(n, "|a|b|c", "ccc")
    found(n, "|a|d", "d")
    found(n, "|a|d", "dd")
    found(n, "|a|d", "ddd")
    found(n, "|a|d|e", "e")
    found(n, "|a|d|e", "ee")
    found(n, "|a|d|e", "eee")
    found(n, "|f|g|h", "h")
    found(n, "|f|g|h", "hh")
    found(n, "|f|g|h", "hhh")

    notfound(n, "|a", "!a")
    notfound(n, "|a|e", "!a")

    n.DeleteLeaf("|", "root")
    notfound(n, "|", "root")

    n.DeleteLeaf("|a", "a")
    notfound(n, "|a", "a")
    found(n, "|a", "aa")
    found(n, "|a", "aaa")

    n.DeleteLeaf("|a|b", "b")
    notfound(n, "|a|b", "b")
    found(n, "|a|b", "bb")
    found(n, "|a|b", "bbb")

    n.DeleteLeaf("|a|b", "b")
    notfound(n, "|a|g|h", "h")

    n.DeletePath("|a")
    notfound_path(n, "|a")
    notfound_path(n, "|a|b")
    notfound_path(n, "|a|b|c")
    notfound_path(n, "|a|d")
    notfound_path(n, "|a|d|e")

    n.DeletePath("|f|g|h")
    notfound_path(n, "|f|g|h")
    found_path(n, "|f")
    found_path(n, "|f|g")

    n.DeletePath("|f")
    notfound_path(n, "|f")
    notfound_path(n, "|f|g")
    notfound_path(n, "|f|g|h")


if __name__ == "__main__":
    Testing()
    Testing_other_split_char()
