# Huffman Code
# Method : Greedy
# input  : list of probability
# output : binary huffman code of input strings
# Using  :
#          p = [0.131538, 0.45865, 0.218959, 0.034572, 0.156281]
#          huffman_code(p)


class Node:
    def __init__(self, l, r, p, idx):
        self.left = l
        self.right = r
        self.p = p
        self.code = ''
        self.idx = idx   # index for output answers

    def check_leaf(self):   # check whether the node is leaf node
        if self.left is None and self.right is None:
            return True
        return False


def Huffman(n, p_list):
    """
    Use possibilities to build the Huffman Tree
    :param p_list: input possibilities
    :return subtree_list[0]: root node of the Tree
    """
    subtree_list = []

    # initial every node as a subtree
    for idx, p in enumerate(p_list):
        subtree_list.append(Node(None, None, p, idx))       # leaf node has no child

    # if only one input possibility, build a tree with only one left leaf
    if n == 1:
        new_node = Node(subtree_list[0], None, subtree_list[0].p, None)
        return new_node

    # build huffman tree
    while len(subtree_list) > 1:
        # sort nodes by possibility
        subtree_list.sort(key=lambda x: x.p)

        # pick up the nodes with the least 2 possibilities to create a new subtree
        tree_left = subtree_list.pop(0)
        tree_right = subtree_list.pop(0)

        new_node = Node(tree_left, tree_right, tree_left.p + tree_right.p, None)       # no index for non-leaf nodes
        subtree_list.append(new_node)

    return subtree_list[0]      # return the root node


def WalkTree(root):
    """
    Code the leaf nodes of Huffman Tree
    :param root: root node of Huffman Tree
    :return ans_list: leaf nodes with code of Huffman Tree
    """
    node_list = [root]
    ans_list = []
    while len(node_list) > 0:
        # get current father node
        cur_node = node_list.pop(0)

        # code of the child is code of father + left(0)/right(1)
        if cur_node.left is not None:
            add_node = cur_node.left
            add_node.code = cur_node.code + '0'
            node_list.append(add_node)
        if cur_node.right is not None:
            add_node = cur_node.right
            add_node.code = cur_node.code + '1'
            node_list.append(add_node)

        # if cur_node is leaf, add to ans_list
        if cur_node.check_leaf():
            ans_list.append(cur_node)
    return ans_list


def huffman_code(p_list):
    root = Huffman(len(p_list), p_list)
    ans_list = WalkTree(root)

    # print answer
    ans_list.sort(key=lambda x: x.idx)
    for i in range(len(p_list)):
        print(ans_list[i].code)


if __name__ == '__main__':
    p = [0.131538, 0.45865, 0.218959, 0.034572, 0.156281]
    huffman_code(p)


