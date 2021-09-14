"""
将平铺的（child, parent）形式的数据转为树状结构，借此进行层次数据呈现与后续处理

"""
from collections import deque
from typing import List


class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)


class FlatRelationToTree:
    def __init__(self, relations: List[dict]):
        self.relations = relations
        self.all_nodes = {rel["_id"]: Node(value=rel) for rel in self.relations}
        for rel in self.relations:
            if rel["parent_id"] is not None:
                self.all_nodes[rel["parent_id"]].add_child(self.all_nodes[rel["_id"]])
        self.root_nodes = [
            node
            for idx, node in self.all_nodes.items()
            if node.value["parent_id"] is None
        ]
        self.id_to_parent = dict()
        for rel in self.relations:
            self.id_to_parent.update({rel["_id"]: rel["parent_id"]})

    def find_all_ancestors(self, node_id: int):
        parent_id = node_id
        ids_order = deque()
        while parent_id is not None:
            ids_order.appendleft(parent_id)
            parent_id = self.id_to_parent[parent_id]
        return "-".join([self.all_nodes[idx].value["name"] for idx in ids_order])

    def all_whole_chains(self):
        whole_cont = []
        for rel in self.relations:
            whole_cont.append(self.find_all_ancestors(rel["_id"]))
        return sorted(whole_cont)

    def id_to_whole_chain(self):
        return {idx: self.find_all_ancestors(node_id=idx) for idx in self.id_to_parent}
