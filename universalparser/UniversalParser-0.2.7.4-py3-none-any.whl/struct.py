from ._rely import *
from ._ntype import *
from ._exception import *
from ._collections import *
from collections import deque
from typing import Any, Callable, Dict, List, OrderedDict as Type_OrderedDict, Tuple, Union
# import warnings

class ChainXML:

    xml = None

    def __init__(self
            , doc: Union[Type_OrderedDict, dict]
            , attr_prefix: str = ATTR_PREFIX
            , cdata_key: str = CDATA_KEY
            , real_cdata_key: str = REAL_CDATA_KEY
            , cdata_self_key: str = CDATA_SELF_KEY
            , comment_key: str = COMMENT_KEY
            , cdata_separator: str = CDATA_SEPARATOR
            , loc_key: str = LOC_KEY
            , data_switch: int = ParserType.XML
            , analysis_text: bool = True
            , open_cdata: bool = True
            , open_comment: bool = True
            , analysis_mode: int = AnalysisMode.RECURSION_OLD
        ) -> None:

        if data_switch in [ParserType.XML, ParserType.HTML, ]:
            if not isinstance(doc, OrderedDict) or 1 != len(doc):
                raise DocTypeError('`doc` type error. Only be one root.')
        elif data_switch in [ParserType.DICT, ParserType.YAML, ParserType.JSON, ]:
            if not isinstance(doc, dict):
                raise DocTypeError('`doc` type error.')
            if len(doc) < 0:
                raise DocTypeError('`doc` type error. Must be greater than or equal to one root.')
            elif 1 != len(doc):
                doc = {'root': doc}
                # warnings.warn('`doc` is greater than one root, the results may not be satisfactory. Auto add `root` node.')
        else:
            raise DocTypeError('Unknown `doc` type.')

        self.doc = doc
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.real_cdata_key = real_cdata_key
        self.cdata_self_key = cdata_self_key
        self.comment_key = comment_key
        self.loc_key = loc_key
        self.cdata_separator = cdata_separator
        self.loc_attr_name = f'{attr_prefix}{loc_key}'
        ChainDict.cdata_key = self.real_cdata_key
        self.analysis_text = analysis_text
        self.open_cdata = open_cdata
        self.open_comment = open_comment

        self._attr_searcher = {}
        self._reverse_attr_name = {}
        self._id_nodes = {}
        self._id_tags = {}
        self._tag_ids = {}
        self._text_ids = {}
        self._textids = []
        self._contrast_ids = {}
        self._comment_ids = {}
        self._cdata_ids = {}
        self.xml = ChainDict(self) # ori xml-dict

        if AnalysisMode.RECURSION_OLD == analysis_mode:
            self._build_chain_by_recursion(self.doc, self.xml)
        elif AnalysisMode.RECOMMEND == analysis_mode:
            self._build_chain_recommend(self.doc, self.xml) # Extra support CDATA(not the same as text.) and comment.
        elif AnalysisMode.DIRECT == analysis_mode:
            self._build_chain_direct(self.doc, self.xml) # future.
        else:
            raise AnalysisTypeError('Analysis type error. Please choice one of exist types.')

    def registry_id_nodes(self, node: Any) -> None:
        self._id_nodes[id(node)] = node

    def remove_id_nodes(self, node: Any) -> None:
        if id(node) in self._id_nodes:
            self._id_nodes.pop(id(node))
        else:
            raise Exception('Node has been removed.')

    def registry_contrast_ids(self, sub_node: Any, node: ChainDict) -> None:
        self._contrast_ids[id(sub_node)] = id(node)

    def remove_contrast_ids(self, sub_node: Any) -> None:
        if id(sub_node) in self._contrast_ids:
            self._contrast_ids.pop(id(sub_node))
        else:
            raise Exception('Property has been removed.')

    def modify_contrast_ids(self, sub_node: Any, node: ChainDict) -> None:
        if id(sub_node) in self._contrast_ids:
            self._contrast_ids[id(sub_node)] = id(node)
        else:
            raise Exception('Property does not exist.')

    def registry_text_ids(self, text: str, node: Any) -> None:
        if self.analysis_text:
            if text in self._text_ids:
                if id(node) not in self._text_ids[text]:
                    self._text_ids[text].append(id(node))
                    self._textids.append(id(node))
                else:
                    raise Exception('Fatal error in parser! Do not re register.')
            else:
                self._text_ids[text] = [id(node), ]
                self._textids.append(id(node))
        else:
            if id(node) not in self._textids:
                self._textids.append(id(node))

    def registry_comment_ids(self, comments: List[str], node: Any) -> None:
        if self.open_comment:
            for comment in comments:
                if comment in self._comment_ids:
                    if id(node) not in self._comment_ids[comment]:
                        self._comment_ids[comment].append(id(node))
                    # else: # distinct
                    #     raise Exception('Fatal error in parser! Do not re register.')
                else:
                    self._comment_ids[comment] = [id(node), ]

    def registry_cdata_ids(self, cdatas: List[str], node: Any) -> None:
        if self.open_cdata:
            for cdata in cdatas:
                if cdata in self._cdata_ids:
                    if id(node) not in self._cdata_ids[cdata]:
                        self._cdata_ids[cdata].append(id(node))
                    # else: # distinct
                    #     raise Exception('Fatal error in parser! Do not re register.')
                else:
                    self._cdata_ids[cdata] = [id(node), ]

    def remove_text_ids(self, text: str, node: Any) -> None:
        if self.analysis_text:
            if text in self._text_ids:

                if id(node) in self._text_ids[text]:
                    self._text_ids[text].remove(id(node))
                    self._textids.remove(id(node))

                    if 0 == len(self._text_ids[text]):
                        self._text_ids.pop(text)
                else:
                    raise Exception('Property has been removed.')
            else:
                raise Exception('Property has been removed.')
        else:
            if id(node) in self._textids:
                self._textids.remove(id(node))

    def modify_text_ids(self, old_text: str, new_text: str, node: Any) -> None:
        self.remove_text_ids(old_text, node)
        self.registry_text_ids(new_text, node)

    def registry_id_tags(self, node: Any, tag: str) -> None:
        self._id_tags[id(node)] = tag

    def remove_id_tags(self, node: Any, tag: str) -> None:
        if id(node) in self._id_tags:
            self._id_tags.pop(id(node))
        else:
            raise Exception('Tag has been removed.')
    
    def modify_id_tags(self, node: Any, old_tag: str, new_tag: str) -> None:
        self.remove_id_tags(node, old_tag)
        self.registry_id_tags(node, new_tag)

    def registry_tag_ids(self, tag: str, node: Any) -> None:
        if tag in self._tag_ids:
            if id(node) not in self._tag_ids[tag]:
                self._tag_ids[tag].append(id(node))
            else:
                raise Exception('Fatal error in parser! Do not re register.')
        else:
            self._tag_ids[tag] = [id(node), ]

    def remove_tag_ids(self, tag: str, node: Any) -> None:
        if tag in self._tag_ids:
            if id(node) in self._tag_ids[tag]:
                self._tag_ids[tag].remove(id(node))

                if 0 == len(self._tag_ids[tag]):
                    self._tag_ids.pop(tag)
            else:
                raise Exception('Tag has been removed.')
        else:
            raise Exception('Tag has been removed.')
    
    def modify_tag_ids(self, tag: str, old_node: Any, new_node: Any) -> None:
        self.remove_tag_ids(tag, old_node)
        self.registry_tag_ids(tag, new_node)

    def registry_attr_searcher(self, search_key: str, node: Any) -> None:
        if search_key in self._attr_searcher:
            if id(node) not in self._attr_searcher[search_key]['nodes']:
                self._attr_searcher[search_key]['nodes'].append(id(node))
                self._attr_searcher[search_key]['count'] += 1
            else:
                raise Exception('Fatal error in parser! Do not re register.')
        else:
            self._attr_searcher[search_key] = {
                'count': 1,
                'nodes': [id(node), ]
            }

    def remove_attr_searcher(self, search_key: str, node: Any) -> None:
        if search_key in self._attr_searcher:
            if id(node) in self._attr_searcher[search_key]['nodes']:
                self._attr_searcher[search_key]['nodes'].remove(id(node))
                self._attr_searcher[search_key]['count'] -= 1
                if 0 == self._attr_searcher[search_key]['count']:
                    self._attr_searcher.pop(search_key)
            else:
                raise Exception('Property has been removed.')
        else:
            raise Exception('Property has been removed.')

    def modify_attr_searcher(self, old_search_key: str, new_search_key: str, node: Any) -> None:
        self.remove_attr_searcher(old_search_key, node)
        self.registry_attr_searcher(new_search_key, node)

    def registry_reverse_attr_name(self, new_old: Tuple[str, str], node: Any) -> None:
        if new_old not in self._reverse_attr_name:
            self._reverse_attr_name[new_old] = [id(node), ]
        else:
            if id(node) not in self._reverse_attr_name[new_old]:
                self._reverse_attr_name[new_old].append(id(node))
            else:
                raise Exception('Fatal error in parser! Do not re register.')

    def remove_reverse_attr_name(self, new_old: Tuple[str, str], node: Any) -> None:
        if new_old in self._reverse_attr_name:
            if id(node) in self._reverse_attr_name[new_old]:
                self._reverse_attr_name[new_old].remove(id(node))
                if 0 == len(self._reverse_attr_name[new_old]):
                    self._reverse_attr_name.pop(new_old)
            else:
                raise Exception('Property has been removed.')
        else:
            raise Exception('Property has been removed.')

    def modify_reverse_attr_name(self, o_new_old: Tuple[str, str], n_new_old: str, node: Any) -> None:
        self.remove_reverse_attr_name(o_new_old, node)
        self.registry_reverse_attr_name(n_new_old, node)

    def _get_searchkeys_by_nodeid(self, node_id: int) -> str:
        search_keys = []
        for search_key, obj in self._attr_searcher.items():
            if node_id in obj['nodes']:
                search_keys.append(search_key)
        return search_keys

    def _get_newolds_by_nodeid(self, node_id: int) -> Tuple[str, str]:
        new_olds = []
        for new_old, node_ids in self._reverse_attr_name.items():
            if node_id in node_ids:
                new_olds.append(new_old)
        return new_olds

    def signal_del_node_base(self, node: Any) -> None:
        stack = [id(node), *self.descendants(id(node))]
        while stack:
            pop_node_id = stack.pop()
            pop_node = self._id_nodes[pop_node_id]
            parent_node = self._id_nodes[self.parent(pop_node_id)]

            search_keys = self._get_searchkeys_by_nodeid(pop_node_id)
            tag = self.get_tag(pop_node)
            new_olds = self._get_newolds_by_nodeid(pop_node_id)

            if isinstance(pop_node, ChainDict):
                text = pop_node[self.real_cdata_key]
                self.remove_text_ids(text, pop_node)

            if isinstance(parent_node, list):
                parent_node.remove(pop_node)
            else:
                if isinstance(parent_node[tag], ChainDict):
                    parent_node.pop(tag)
                elif isinstance(parent_node[tag], list):
                    parent_node[tag].remove(pop_node)
                else:
                    raise PopError("Pop node error, obj must be `ChainDict` type, and obj's parent node-type must be `ChainDict` or `list`.")

            for search_key in search_keys:
                self.remove_attr_searcher(search_key, pop_node)
            for new_old in new_olds:
                self.remove_reverse_attr_name(new_old, pop_node)
            self.remove_id_nodes(pop_node)
            self.remove_id_tags(pop_node, tag)
            self.remove_tag_ids(tag, pop_node)
            self.remove_contrast_ids(pop_node)
        
    def signal_add_node(self, sub_node: Any, node: Any, tag: str=None, text: str=None) -> None:
        self.registry_id_nodes(sub_node)
        self.registry_id_tags(sub_node, tag)
        self.registry_contrast_ids(sub_node, node)
        if tag is not None:
            self.registry_tag_ids(tag, sub_node)
        if text is not None:
            self.registry_text_ids(text, sub_node)

    def signal_move_node(self, move_node: ChainDict, to_node: ChainDict) -> None:
        from_node = self.get_parent(move_node)
        if id(from_node) == id(to_node):
            raise MoveError("`from_node` can't be the same as `to_node`.")
        self._contrast_ids[id(move_node)] = id(to_node)

    def signal_add_attr_base(self, node: Any, attr_name: str, attr_value: str) -> None:
        new_old = (attr_name, f'{self.attr_prefix}{attr_name}')
        search_key = f'{attr_name}={attr_value}'
        self.registry_reverse_attr_name(new_old, node)
        self.registry_attr_searcher(search_key, node)

    def signal_add_attr(self, node: Any, new_old: Tuple[str, str], search_key: str) -> None:
        self.registry_reverse_attr_name(new_old, node)
        self.registry_attr_searcher(search_key, node)

    def signal_modify_attr(self, old_search_key: str, new_search_key: str, node: Any):
        self.modify_attr_searcher(old_search_key, new_search_key, node)

    def signal_del_attr_base(self, node: Any, attr_name: str, attr_value: str) -> None:
        new_old = (attr_name, f'{self.attr_prefix}{attr_name}')
        search_key = f'{attr_name}={attr_value}'
        self.remove_reverse_attr_name(new_old, node)
        self.remove_attr_searcher(search_key, node)

    def signal_modify_text(self, old_text: str, new_text: str, node: Any) -> None:
        self.modify_text_ids(old_text, new_text, node)

    def _get_last_loc(self, node: ChainDict) -> str:
        max_loc = -1
        for child in self.get_children(node):
            if self.loc_key in child:
                if max_loc < int(child[self.loc_key]):
                    max_loc = int(child[self.loc_key])
        if max_loc != -1:
            return str(max_loc+1)
        else:
            return '0'

    def _build_chain_by_recursion(self, sub_node_v: Union[str, list, dict], parent_node: ChainDict = None, tag: str=None, flag: bool=False) -> None:

        self.registry_id_nodes(parent_node)

        if tag is None:
            if isinstance(sub_node_v, dict):
                for _tag, _sub_node_v in sub_node_v.items():
                    self._build_chain_by_recursion(_sub_node_v, parent_node, _tag)
                return
            else:
                raise DocTypeError('The XML document is malformed.')

        if tag.startswith(self.attr_prefix):
            new_old = (tag[len(self.attr_prefix):], tag)
            search_key = f'{new_old[0]}={sub_node_v}'
            parent_node[new_old[0]] = sub_node_v
            self.signal_add_attr(parent_node, new_old, search_key)
            
        elif self.cdata_key == tag:
            parent_node[self.real_cdata_key] = sub_node_v
            self.registry_text_ids(sub_node_v, parent_node)
            
        else:
            if sub_node_v is None:
                if not flag:
                    insert_node = ChainDict(self)
                    insert_node[self.real_cdata_key] = ''
                    parent_node[tag] = insert_node
                    self.signal_add_node(insert_node, parent_node, tag, '')

            elif isinstance(sub_node_v, dict):
                temp_node = ChainDict(self)
                
                if not flag:
                    parent_node[tag] = temp_node

                for _tag, _sub_node_v in sub_node_v.items():
                    if flag:
                        self._build_chain_by_recursion(_sub_node_v, parent_node, _tag)
                    else:
                        self._build_chain_by_recursion(_sub_node_v, temp_node, _tag)
                
                if not flag:
                    if self.real_cdata_key not in temp_node:
                        temp_node[self.real_cdata_key] = ''
                        self.signal_add_node(temp_node, parent_node, tag=tag, text='')
                    else:
                        self.signal_add_node(temp_node, parent_node, tag=tag)

            elif isinstance(sub_node_v, (list, tuple)):
                temp_list = []
                self.signal_add_node(temp_list, parent_node, tag=tag)

                for sub_node in sub_node_v:
                    temp_node = ChainDict(self)
                    temp_list.append(temp_node)

                    self._build_chain_by_recursion(sub_node, temp_node, tag, True)

                    if self.real_cdata_key not in temp_node:
                        temp_node[self.real_cdata_key] = ''
                        self.signal_add_node(temp_node, temp_list, tag, '')
                    else:
                        self.signal_add_node(temp_node, temp_list, tag)
                parent_node[tag] = temp_list
                
            else:
                if flag:
                    parent_node[self.real_cdata_key] = sub_node_v
                    self.registry_text_ids(sub_node_v, parent_node)
                else:
                    temp_node = ChainDict(self)
                    temp_node[self.real_cdata_key] = sub_node_v
                    self.signal_add_node(temp_node, parent_node, tag, sub_node_v)
                    parent_node[tag] = temp_node

    def _build_chain_recommend(self, datas: Union[dict, list], root_node: ChainDict) -> None:
        root_data = list(datas.items())[0]
        queue = deque([[root_data[0], root_data[1], root_node]])
        while queue:
            pop_obj = queue.popleft()
            pop_tag = pop_obj[0]
            pop_node = pop_obj[1]
            parent_node = pop_obj[2]
            self.registry_id_nodes(parent_node) # Only effect to first node.
            sub_nodes = []
            temp_node = ChainDict(self)

            for tag, value in pop_node.items():
                if tag.startswith(self.attr_prefix):
                    attr_name = tag[len(self.attr_prefix):]
                    temp_node[attr_name] = value
                    self.signal_add_attr_base(temp_node, attr_name, value)
                elif self.cdata_key == tag:
                    temp_node[self.real_cdata_key] = value
                    self.registry_text_ids(value, temp_node)
                elif self.cdata_self_key == tag:
                    temp_node[self.cdata_self_key] = value
                    self.registry_cdata_ids(value, temp_node)
                elif self.comment_key == tag:
                    temp_node[self.comment_key] = value # value: List
                    self.registry_comment_ids(value, temp_node)
                else:
                    if isinstance(value, dict):
                        sub_nodes.append([tag, value, temp_node])
                    elif isinstance(value, (list, tuple)):
                        sub_nodes.extend([[tag, _1, temp_node] for _1 in value])
                    else:
                        raise TypeError('Unknown status')

            if pop_tag not in parent_node:
                parent_node[pop_tag] = temp_node
                self.signal_add_node(temp_node, parent_node, tag=pop_tag)
            else:
                if isinstance(parent_node[pop_tag], ChainDict):
                    t_node = parent_node[pop_tag]
                    temp_list = []
                    parent_node[pop_tag] = temp_list
                    temp_list.append(t_node)
                    self.signal_add_node(temp_list, parent_node, tag=pop_tag)
                    self.signal_move_node(t_node, to_node=temp_list)
                    temp_list.append(temp_node)
                    self.signal_add_node(temp_node, temp_list, tag=pop_tag)
                elif isinstance(parent_node[pop_tag], list):
                    parent_node[pop_tag].append(temp_node)
                    self.signal_add_node(temp_node, parent_node[pop_tag], tag=pop_tag)
                else:
                    raise TypeError('Unknown type.')
            
            queue.extendleft(reversed(sub_nodes))

    def _build_chain_direct(self, datas: dict, root: ChainDict) -> None:
        return

    def _build_by_copy(self, datas: Union[dict, list], root_node: ChainDict) -> None:
        queue = deque([])
        if isinstance(datas, dict):
            for _tag, _node in datas.items():
                if isinstance(_node, dict):
                    queue.append([_tag, _node, root_node])
                elif isinstance(_node, list):
                    queue.extendleft([[_tag, _1, root_node] for _1 in reversed(_node)])
                else:
                    raise TypeError('Only support `dict`.')
        else:
            raise TypeError('Only support `dict`.')

        while queue:
            pop_obj = queue.popleft()
            pop_tag = pop_obj[0]
            pop_node = pop_obj[1]
            parent_node = pop_obj[2]
            self.registry_id_nodes(parent_node) # Only effect to first node.
            sub_nodes = []
            temp_node = ChainDict(self)

            for tag, value in pop_node.items():
                if tag.startswith(self.attr_prefix):
                    if tag == self.loc_attr_name:
                        loc_value = self._get_last_loc(parent_node)
                        temp_node[self.loc_key] = loc_value
                        self.signal_add_attr_base(temp_node, self.loc_key, loc_value)
                    else:
                        attr_name = tag[len(self.attr_prefix):]
                        temp_node[attr_name] = value
                        self.signal_add_attr_base(temp_node, attr_name, value)
                elif self.cdata_key == tag:
                    temp_node[self.real_cdata_key] = value
                    self.registry_text_ids(value, temp_node)
                elif self.cdata_self_key == tag:
                    temp_node[self.cdata_self_key] = value
                    self.registry_cdata_ids(value, temp_node)
                elif self.comment_key == tag:
                    temp_node[self.comment_key] = value
                    self.registry_comment_ids(value, temp_node)
                else:
                    if isinstance(value, dict):
                        sub_nodes.append([tag, value, temp_node])
                    elif isinstance(value, (list, tuple)):
                        sub_nodes.extend([[tag, _1, temp_node] for _1 in value])
                    else:
                        raise TypeError('Unknown status')

            if pop_tag not in parent_node:
                parent_node[pop_tag] = temp_node
                self.signal_add_node(temp_node, parent_node, tag=pop_tag)
            else:
                if isinstance(parent_node[pop_tag], ChainDict):
                    t_node = parent_node[pop_tag]
                    temp_list = []
                    parent_node[pop_tag] = temp_list
                    temp_list.append(t_node)
                    self.signal_add_node(temp_list, parent_node, tag=tag)
                    self.signal_move_node(t_node, to_node=temp_list)
                    temp_list.append(temp_node)
                    self.signal_add_node(temp_node, temp_list, tag=pop_tag)
                elif isinstance(parent_node[pop_tag], list):
                    parent_node[pop_tag].append(temp_node)
                    self.signal_add_node(temp_node, parent_node[pop_tag], tag=pop_tag)
                else:
                    raise TypeError('Unknown type.')
            
            queue.extendleft(reversed(sub_nodes))

    def exists(self, node_id: Union[int, ChainDict, list]) -> bool:
        if isinstance(node_id, (ChainDict, list)):
            node_id = id(node_id)
        if node_id in list(self._contrast_ids.keys()) + list(self._contrast_ids.values()):
            return True
        else:
            return False

    def is_parent_exist(self, node_id: Union[int, ChainDict, list]) -> bool:
        if isinstance(node_id, (ChainDict, list)):
            node_id = id(node_id)
        if node_id in self._contrast_ids:
            return True
        else:
            return False

    def parent(self, node_id: int) -> int:
        if self.is_parent_exist(node_id):
            return self._contrast_ids[node_id]
        else:
            if node_id in self._contrast_ids.values():
                return node_id
            else:
                raise NoNodesFound('`node_id` error.')

    def get_parent(self, node: ChainDict) -> ChainDict:
        temp_parent = self._id_nodes[self.parent(id(node))]
        if isinstance(temp_parent, list):
            temp_parent = self.get_parent(temp_parent)
        return temp_parent

    def children(self, p_id: int) -> List[int]:
        children_node_ids = []
        for t_c, t_p in self._contrast_ids.items():
            if t_p == p_id:
                children_node_ids.append(t_c)
        return children_node_ids # mix list and Chaindict, can not directly use.

    def get_children(self, node: ChainDict, combine=True) -> List[ChainDict]:
        temp_list = [self._id_nodes[_1] for _1 in self.children(id(node))]
        if combine:
            result = []
            for obj in temp_list:
                if isinstance(obj, list):
                    result.extend(obj)
                else:
                    result.append(obj)
            return result
        else:
            return temp_list
    
    def siblings(self, node_id: int) -> List[int]:
        p_id = self.parent(node_id)
        # siblings_node_ids = self.children(p_id)
        siblings_node_ids = [id(_) for _ in self.get_children(self._id_nodes[p_id])]
        siblings_node_ids.remove(node_id)
        return siblings_node_ids

    def get_siblings(self, node: ChainDict) -> List[ChainDict]:
        return [self._id_nodes[_1] for _1 in self.siblings(id(node))]

    def sibling_ancestor(self, node_id: int):
        while self.is_parent_exist(node_id):
            yield self.siblings(node_id) + [node_id, ]
            node_id = self.parent(node_id)
            if not self.is_parent_exist(node_id):
                break # root parent can return itself. 
        if self.exists(node_id) and not self.is_parent_exist(node_id):
            yield [node_id, ]

    def descendants(self, node_id: int) -> List[int]:
        nodes = []
        stack = []
        if self.exists(node_id):
            stack.extend(self.children(node_id))
        while stack:
            pop_node_id = stack.pop()
            nodes.append(pop_node_id)
            stack.extend(self.children(pop_node_id))
        return nodes

    def get_descendants(self, node: ChainDict) -> List[ChainDict]:
        return [self._id_nodes[_1] for _1 in self.descendants(id(node))]

    def ancestor(self, node_id: int):
        while self.is_parent_exist(node_id):
            node_id = self.parent(node_id)
            yield [node_id, ]

    def get_ancestor(self, node: ChainDict) -> List[ChainDict]:
        return [self._id_nodes[_1[0]] for _1 in self.ancestor(id(node))]

    def get_tag(self, node: ChainDict) -> str:
        if id(node) in self._id_tags:
            return self._id_tags[id(node)]
        else:
            return self._id_tags[self._contrast_ids[id(node)]]
    
    def get_attr_names(self, node: ChainDict) -> List[str]:
        attr_names = []
        for reverse_name, node_ids in self._reverse_attr_name.items():
            if id(node) in node_ids:
                attr_names.append(reverse_name[0])
        return attr_names

    def find_text(self, node: ChainDict, format_func: Callable=lambda x:x) -> Any:

        if not isinstance(node, ChainDict):
            raise TextNotFound('Text not found.')
        
        if self.real_cdata_key in node:
            return format_func(node[self.real_cdata_key])
        elif isinstance(node, str):
            return format_func(node)
        else:
            raise TextNotFound('Text not found.')

    def _revert_data(self, forward=True):
        for no, node_ids in self._reverse_attr_name.items():
            new_name, old_name = no
            for node_id in node_ids:
                node = self._id_nodes[node_id]
                if forward:
                    node[new_name] = node[old_name]
                    node.pop(old_name)
                else:
                    node[old_name] = node[new_name]
                    node.pop(new_name)

        for node in self._textids:
            node = self._id_nodes[node]
            if forward:
                node[self.real_cdata_key] = node[self.cdata_key]
                node.pop(self.cdata_key)
            else:
                node[self.cdata_key] = node[self.real_cdata_key]
                node.pop(self.real_cdata_key)
