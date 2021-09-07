from typing import Callable, Optional, Union
import json
from copy import deepcopy
from io import StringIO
from .struct import *
from ._tools import *
from ._decorator import *
from ._collections import *
from ._ntype import *
from UniversalParser.xml import odict as XmlParser
from UniversalParser.xml.unparser import unparse_dict
from UniversalParser.html import odict as HTMLParser

__all__ = [
    'ChainManager',
]

class ChainManager:

    SEARCH_ATTR_KEY: str = 'id'

    def __init__(self
            , xml_data: str # xml
            , *args
            , data_switch: int = ParserType.XML
            , universal_data: str = None # json/dict/yaml/...
            , analysis_text: bool = True
            , open_cdata: bool = False
            , open_comment: bool = False
            , encoding: str = None
            , namespace_separator: str = None
            , analysis_mode: int = AnalysisMode.RECURSION_OLD
            , combine_cdata: bool = True
            , include_comment: bool = False
            , include_loc: bool = False # Compatible with JSON
            , convert_charrefs: bool = True
            , **kwargs
        ) -> None:

        self.data_switch = data_switch # choice analysis obj type, default: ParserType.XML
        self.encoding = encoding
        self.open_comment = open_comment
        self.open_cdata = open_cdata
        self.include_comment = include_comment
        self.combine_cdata = combine_cdata
        self.analysis_text = analysis_text
        self.namespace_separator = namespace_separator
        self.include_loc = include_loc
        self.xml_declare = None

        self.attr_prefix = kwargs['attr_prefix'] if 'attr_prefix' in kwargs else ATTR_PREFIX
        self.cdata_key = kwargs['cdata_key'] if 'cdata_key' in kwargs else CDATA_KEY
        self.real_cdata_key = kwargs['real_cdata_key'] if 'real_cdata_key' in kwargs else REAL_CDATA_KEY
        self.cdata_self_key = kwargs['cdata_self_key'] if 'cdata_self_key' in kwargs else CDATA_SELF_KEY
        self.comment_key = kwargs['comment_key'] if 'comment_key' in kwargs else COMMENT_KEY
        self.cdata_separator = kwargs['cdata_separator'] if 'cdata_separator' in kwargs else CDATA_SEPARATOR
        self.loc_key = kwargs['loc_key'] if 'loc_key' in kwargs else LOC_KEY
        ChainDict.cdata_key = self.real_cdata_key
        ChainDict.switch_loc = include_loc
        self.loc_attr = f'{self.attr_prefix}{self.loc_key}'
        
        if ParserType.XML == data_switch:
            temp_data, self.xml_declare = XmlParser.parse_odict(
                xml_data
                , encoding = self.encoding
                , namespace_separator = self.namespace_separator
                , attr_prefix = self.attr_prefix
                , cdata_key = self.cdata_key
                , cdata_self_key = self.cdata_self_key 
                , comment_key = self.comment_key
                , combine_cdata = combine_cdata
                , include_comment = include_comment
                , include_loc = include_loc
                , cdata_separator = self.cdata_separator
            )
        elif ParserType.HTML == data_switch:
            temp_data = HTMLParser.parse_odict(
                universal_data
                , convert_charrefs = convert_charrefs
                , attr_prefix = self.attr_prefix
                , cdata_key = self.cdata_key
                , comment_key = self.comment_key
                , include_comment = self.include_comment
                , cdata_separator = self.cdata_separator
                , loc_key = self.loc_key
                , include_loc = include_loc
            )
        elif ParserType.JSON == data_switch:
            temp_data = json.loads(universal_data)
        elif ParserType.DICT == data_switch:
            temp_data = universal_data
        elif ParserType.YAML == data_switch:
            try:
                import yaml
            except:
                raise ImportError('If you want to use this function, please `pip install yaml`.')
            else:
                temp_data = yaml.load(universal_data, Loader=yaml.FullLoader)
        else:
            raise DocTypeError('Unknown `universal_data` type.')
            
        self.objects = ChainXML(
            temp_data
            , attr_prefix = self.attr_prefix
            , cdata_key = self.cdata_key
            , real_cdata_key = self.real_cdata_key
            , cdata_self_key = self.cdata_self_key
            , comment_key = self.comment_key
            , cdata_separator = self.cdata_separator
            , loc_key = self.loc_key
            , data_switch = data_switch
            , analysis_text = analysis_text
            , analysis_mode = analysis_mode
            , open_cdata = open_cdata
            , open_comment = open_comment
        )

        self.document = self.xml = self.objects.xml

        self._attr_searcher = self.objects._attr_searcher
        self._reverse_attr_name = self.objects._reverse_attr_name
        self._id_nodes = self.objects._id_nodes
        self._id_tags = self.objects._id_tags
        self._tag_ids = self.objects._tag_ids
        self._text_ids = self.objects._text_ids
        self._contrast_ids = self.objects._contrast_ids
        self._comment_ids = self.objects._comment_ids
        self._cdata_ids = self.objects._cdata_ids

        self.get_tag = self.objects.get_tag
        self.get_parent = self.objects.get_parent
        self.get_children = self.objects.get_children
        self.get_siblings = self.objects.get_siblings
        self.get_ancestor = self.objects.get_ancestor
        self.get_descendants = self.objects.get_descendants
        self.get_attr_names = self.objects.get_attr_names
        self.find_text = self.objects.find_text

        self.exists = self.objects.exists
        self.is_parent_exist = self.objects.is_parent_exist

    @limit_one
    def find_nodes_by_attrs(self, one_=False, **kwargs) -> Union[List[ChainDict], ChainDict]:

        if len(kwargs) < 1:
            raise KeywordAttrsError('Keyword parameters must be passed in.')

        conditions = set([f'{k}={v}' for k, v in kwargs.items()])
        match_cons = []
        for sk in list(self._attr_searcher.keys()):
            if sk in conditions:
                match_cons.append(sk)

        if len(match_cons) != len(conditions):
            return []

        len_match_cons = len(match_cons)
        if 0 == len_match_cons:
            return []
        elif 1 == len_match_cons:
            obj = self._attr_searcher[match_cons[0]]
            if obj['count'] > 1:
                return [self._id_nodes[_t] for _t in obj['nodes']]
            else:
                return [self._id_nodes[obj['nodes'][0]], ]
        else:
            objs = find_intersection([self._attr_searcher[t]['nodes'] for t in match_cons])
            if 0 == len(objs):
                return []
            elif 1 == len(objs):
                return [self._id_nodes[objs[0]], ]
            else:
                return [self._id_nodes[_t] for _t in objs]

    def __matmul__(self, attrs: Union[dict, str]) -> ChainExpressionManager: # @
        ChainExpressionManager.SEARCH_ATTR_KEY = self.SEARCH_ATTR_KEY
        if isinstance(attrs, dict):
            nodes = self.find_nodes_by_attrs(**attrs)
        elif isinstance(attrs, str):
            nodes = self.find_nodes_by_attrs(**{self.SEARCH_ATTR_KEY: attrs})
        else:
            raise TypeError('`attrs` must be dict or str.')
        chainExpressionManager = ChainExpressionManager(self, self.objects, nodes)
        return chainExpressionManager

    def find_node_by_attrs(self, **kwargs) -> ChainDict:
        return self.find_nodes_by_attrs(one_=True, **kwargs)

    @limit_one
    def find_nodes_by_indexs(self, indexs: List[int], one_=False, **kwargs) -> Union[List[ChainDict], ChainDict]:
        nodes = self.find_nodes_by_attrs(**kwargs)
        len_nodes = len(nodes)
        return_nodes = []
        for index in indexs:
            if 0 <= index < len_nodes:
                return_nodes.append(nodes[index])
        return return_nodes

    @limit_one
    def find_nodes_by_tag(self, tag: str, one_=False) -> Union[List[ChainDict], ChainDict]:
        nodes = []
        if tag in self._tag_ids:
            for _1 in [self._id_nodes[_id] for _id in self._tag_ids[tag]]:
                if isinstance(_1, ChainDict):
                    nodes.append(_1)
                elif isinstance(_1, list):
                    pass
        return nodes

    def __or__(self, tag) -> ChainExpressionManager: # |
        nodes = self.find_nodes_by_tag(tag)
        chainExpressionManager = ChainExpressionManager(self, self.objects, nodes)
        return chainExpressionManager

    @limit_one
    def find_nodes_by_comment(self, comment: str, one_=False) -> Union[List[ChainDict], ChainDict]:
        nodes = []
        if comment in self._comment_ids:
            for _1 in [self._id_nodes[_id] for _id in set(self._comment_ids[comment])]:
                nodes.append(_1)
        return nodes

    def __floordiv__(self, comment) -> ChainExpressionManager: # //
        nodes = self.find_nodes_by_comment(comment)
        chainExpressionManager = ChainExpressionManager(self, self.objects, nodes)
        return chainExpressionManager

    @limit_one
    def find_nodes_by_cdata(self, cdata: str, one_=False) -> Union[List[ChainDict], ChainDict]:
        nodes = []
        if cdata in self._cdata_ids:
            for _1 in [self._id_nodes[_id] for _id in set(self._cdata_ids[cdata])]:
                nodes.append(_1)
        return nodes

    def __mod__(self, cdata) -> ChainExpressionManager: # %
        nodes = self.find_nodes_by_cdata(cdata)
        chainExpressionManager = ChainExpressionManager(self, self.objects, nodes)
        return chainExpressionManager
    
    @limit_one
    def find_nodes_by_tag_and_attrs(self, tag_: str=None, one_=False, **kwargs) -> Union[List[ChainDict], ChainDict]:

        if tag_ is not None and tag_ not in self._tag_ids:
            return []

        conditions = set([f'{k}={v}' for k, v in kwargs.items()])
        match_cons = []
        for sk in list(self._attr_searcher.keys()):
            if sk in conditions:
                match_cons.append(sk)

        if len(match_cons) != len(conditions):
            if 0 != len(conditions):
                return []
                
        len_match_cons = len(match_cons)
        if 0 == len_match_cons and 0 != len(conditions):
            return []
        else:
            if tag_ is not None:
                tag_ids = [id(_1) for _1 in self.find_nodes_by_tag(tag_)]
                objs = find_intersection([tag_ids] + [self._attr_searcher[t]['nodes'] for t in match_cons])
            else:
                objs = find_intersection([self._attr_searcher[t]['nodes'] for t in match_cons])

            if 0 == len(objs):
                return []
            elif 1 == len(objs):
                return [self._id_nodes[objs[0]], ]
            else:
                return [self._id_nodes[_t] for _t in objs]

    @limit_one
    def find_nodes_by_tag_text_attrs(self, tag_: str=None, text_: str=None, one_=False, **kwargs) -> Union[List[ChainDict], ChainDict]:
        tag_ids = None
        text_ids = None
        attr_ids = None

        if tag_ is not None:
            tag_ids = [id(_1) for _1 in self.find_nodes_by_tag(tag_)]
        if text_ is not None:
            text_ids = [id(_1) for _1 in self.find_nodes_by_text(text_)]
        if len(kwargs) > 0:
            attr_ids = [id(_1) for _1 in self.find_nodes_by_attrs(**kwargs)]

        node_ids = find_intersection([_1 for _1 in (tag_ids, text_ids, attr_ids) if _1 is not None])
        return [self._id_nodes[node_id] for node_id in node_ids]

    @limit_one
    def find_nodes_by_text(self, text: str, one_=True) -> Union[List[ChainDict], ChainDict]:
        if not self.analysis_text:
            raise EnvironmentError('If you want to use this way, please set `analysis_text=True`')
        if text in self._text_ids:
            return [self._id_nodes[_1] for _1 in self._text_ids[text]]
        return []

    def __truediv__(self, text) -> ChainExpressionManager: # /
        nodes = self.find_nodes_by_text(text)
        chainExpressionManager = ChainExpressionManager(self, self.objects, nodes)
        return chainExpressionManager

    def find_text_by_attrs(self, *args, text_type: int=TextType.STR, format_func: Callable=lambda x:x, **kwargs) -> str:
        node = self.find_nodes_by_attrs(*args, one_=True, **kwargs)
        text = self.find_text(node, format_func)
        if TextType.STR == text_type:
            return str(text)
        elif TextType.FLOAT == text_type:
            return float(text)
        elif TextType.INT == text_type:
            return int(text)
        else:
            return text

    def __find_constraint_node(self
            , unique_node: Optional[ChainDict] = None
            , find_func: Optional[Callable] = None
            , constraint: Optional[Dict[str, Any]] = None
        ) -> int:
        
        unique_node_id = None
        if unique_node is not None:
            if isinstance(unique_node, ChainDict):
                unique_node_id = id(unique_node)
            else:
                raise KeywordAttrsError('`unique_node` must be type of ChainDict.')

        if unique_node_id is None:
            if constraint is not None and isinstance(constraint, dict):
                if 'args' not in constraint or 'kwargs' not in constraint:
                    raise KeywordAttrsError('`args` and `kwargs` must in constraint.')
                find_func = find_func if find_func is not None else self.find_nodes_by_tag_text_attrs
                node = find_func(*constraint['args'], **constraint['kwargs'], one_=True)
                unique_node_id = id(node)
            else:
                raise KeywordAttrsError('`constraint` must be assign.')

        if unique_node_id is None:
            raise NoNodesFound('Constraint node not found.')

        return unique_node_id

    @limit_one
    def find_nodes_with_sibling_ancestor(self
            , unique_node: Optional[ChainDict] = None
            , *args
            , tag_: str = None
            , text_: str = None
            , one_=False
            , find_func: Optional[Callable] = None # default: find_nodes_by_tag_text_attrs
            , constraint: Optional[Dict[str, Any]] = None # {'args': [], 'kwargs': {}}
            , **kwargs
        ) -> Union[List[ChainDict], ChainDict]:

        unique_node_id = self.__find_constraint_node(unique_node, find_func, constraint)

        t_node_ids = [id(_1) for _1 in self.find_nodes_by_tag_text_attrs(tag_=tag_, text_=text_, *args, **kwargs)]
        if len(t_node_ids) <= 0:
            return []

        nodes = []
        for t_node_id in t_node_ids:
            for _1 in self.objects.sibling_ancestor(t_node_id):
                if unique_node_id in _1:
                    nodes.append(self._id_nodes[t_node_id])
                    break
        return nodes

    @limit_one
    def find_nodes_with_ancestor(self
            , unique_node: Optional[ChainDict] = None
            , *args
            , tag_: str = None
            , text_: str = None
            , one_=False
            , find_func: Optional[Callable] = None # default: find_nodes_by_tag_text_attrs
            , constraint: Optional[Dict[str, Any]] = None # {'args': [], 'kwargs': {}}
            , **kwargs
        ) -> Union[List[ChainDict], ChainDict]:

        unique_node_id = self.__find_constraint_node(unique_node, find_func, constraint)

        t_node_ids = [id(_1) for _1 in self.find_nodes_by_tag_text_attrs(tag_=tag_, text_=text_, *args, **kwargs)]
        if len(t_node_ids) <= 0:
            return []

        nodes = []
        for t_node_id in t_node_ids:
            for _1 in self.objects.ancestor(t_node_id):
                if unique_node_id in _1:
                    nodes.append(self._id_nodes[t_node_id])
                    break
        return nodes

    @limit_one
    def find_nodes_with_descendants(self
            , unique_node: Optional[ChainDict] = None
            , *args
            , tag_: str = None
            , text_: str = None
            , one_=False
            , find_func: Optional[Callable] = None # default: find_nodes_by_tag_text_attrs
            , constraint: Optional[Dict[str, Any]] = None # {'args': [], 'kwargs': {}}
            , **kwargs
        ) -> Union[List[ChainDict], ChainDict]:
        
        unique_node_id = self.__find_constraint_node(unique_node, find_func, constraint)

        t_node_ids = [id(_1) for _1 in self.find_nodes_by_tag_text_attrs(tag_=tag_, text_=text_, *args, **kwargs)]
        if len(t_node_ids) <= 0:
            return []

        nodes = []
        for t_node_id in t_node_ids:
            if unique_node_id in self.objects.descendants(t_node_id):
                nodes.append(self._id_nodes[t_node_id])
        return nodes

    def popitem(self, obj: ChainDict):
        self.objects.signal_del_node_base(obj)

    def pop_node_by_attrs(self, **kwargs):
        obj = self.find_nodes_by_attrs(one_=True, **kwargs)
        return self.popitem(obj)

    def pop_nodes_by_attrs(self, **kwargs):
        objs = self.find_nodes_by_attrs(**kwargs)
        for obj in objs:
            self.popitem(obj)

    def insert_attrs(self, node, *args, **kwargs) -> None:
        for attr_name, value in args+tuple(kwargs.items()):
            if attr_name not in node:
                node[attr_name] = value
                self.objects.signal_add_attr_base(node, attr_name, value)

    def insert_comment(self, node: ChainDict, comment: str) -> None:
        if not isinstance(node, ChainDict):
            raise TypeError('Only support `ChainDict` node.')
        if self.open_comment and self.include_comment:
            if self.comment_key in node:
                node[self.comment_key].append(comment)
            else:
                node[self.comment_key] = [comment, ]
            self.objects.registry_comment_ids(comment, node)
        else:
            raise EnvironmentError('Must set `open_comment=True` and `include_comment=True`.')

    def insert_cdata(self, node: ChainDict, cdata: str):
        if not isinstance(node, ChainDict):
            raise TypeError('Only support `ChainDict` node.')
        if not self.combine_cdata and self.open_cdata:
            if self.cdata_self_key in node:
                node[self.cdata_self_key].append(cdata)
            else:
                node[self.cdata_self_key] = [cdata, ]
            self.objects.registry_cdata_ids(cdata, node)
        else:
            raise EnvironmentError('Must set `combine_cdata=False` and `open_cdata=True`.')

    def update_attr(self, node: ChainDict, attr_name: str, new_value: Any) -> Tuple[str, str]:
        if attr_name in node:
            old_search_key = f'{attr_name}={node[attr_name]}'
            return_v = (attr_name, node[attr_name])
            node[attr_name] = new_value
            new_search_key = f'{attr_name}={new_value}'
            self.objects.signal_modify_attr(old_search_key, new_search_key, node)
            return return_v
        else:
            raise UpdateError('Unable to update this node, check whether the attribute exists.')

    def del_attr(self, node: ChainDict, attr_name: str) -> Tuple[str, str]:
        attr_value = node[attr_name]
        return_v = (attr_name, attr_value)
        node.pop(attr_name)
        self.objects.signal_del_attr_base(node, attr_name, attr_value)
        return return_v

    def batch_del_attr(self, node: ChainDict, *args) -> List[Tuple[str, str]]:
        return_vs = []
        for attr_name in args:
            return_vs.append(self.del_attr(node, attr_name))
        return return_vs

    def batch_update_attrs(self, node, *args, **kwargs) -> List[Tuple[str, str]]:
        if len(args) < 1 and len(kwargs) < 1:
            raise KeywordAttrsError('Parameters or keyword parameters must be passed in.')
        return_vs = []
        for attr_name, value in args+tuple(kwargs.items()):
            return_vs.append(self.update_attr(node, attr_name, value))
        return return_vs
        
    def update_text(self, node: ChainDict, new_text: Any) -> str:
        if self.real_cdata_key in node:
            old_text = node[self.real_cdata_key]
            node[self.real_cdata_key] = new_text
            self.objects.signal_modify_text(old_text, new_text, node)
            return old_text
        else:
            raise UpdateError('Unable to update this node, `text_` is not found.')

    def clear_text(self, node: ChainDict) -> str:
        return self.update_text(node, '')

    def batch_clear_text(self, nodes: List[ChainDict]) -> List[str]:
        old_values = []
        for node in nodes:
            old_values.append(self.update_text(node, ''))
        return old_values

    def _reset_locs(self, node: Union[ChainDict, List[ChainDict]]) -> None:
        start = 0
        nodes = []
        if isinstance(node, ChainDict):
            nodes = self.get_children(node)
        elif isinstance(node, list):
            parent_node = self.get_parent(node)
            nodes = self.get_children(parent_node)
        nodes.sort(key=lambda x: int(x[self.loc_key]), reverse=False)
        for t_node in nodes:
            self.update_attr(t_node, self.loc_key, str(start))
            start += 1

    def _insert_list(self, node: list, tag: str='', attrs={}, text: str=''):
        inner_node = ChainDict(self.objects)
        self.insert_attrs(inner_node, **attrs)
        self.insert_attrs(inner_node, **{self.loc_key: self.objects._get_last_loc(node)})
        inner_node[self.real_cdata_key] = text
        node.append(inner_node)
        self.objects.signal_add_node(inner_node, node, tag=tag, text='')
        return inner_node
                
    def insert(self, node: Union[ChainDict, List[ChainDict]], tag: str='', attrs={}, text: str='') -> ChainDict:
        if isinstance(node, ChainDict):
            if tag not in node:
                insert_node = ChainDict(self.objects)
                insert_node[self.real_cdata_key] = ''
                inner_node = ChainDict(self.objects)
                self.insert_attrs(inner_node, **attrs)
                self.insert_attrs(inner_node, **{self.loc_key: self.objects._get_last_loc(node)})
                inner_node[self.real_cdata_key] = text
                insert_node[tag] = inner_node
                node.update(insert_node)
                self.objects.signal_add_node(inner_node, insert_node, tag=tag, text=text)
                self.objects.signal_add_node(insert_node, node, tag=tag, text='')
                return inner_node
            else:
                temp_node = node[tag]
                if isinstance(temp_node, ChainDict):
                    temp_list = []
                    node[tag] = temp_list
                    temp_list.append(temp_node)
                    self.objects.signal_add_node(temp_list, node, tag=tag)
                    self.objects.signal_move_node(temp_node, to_node=temp_list)
                    return self._insert_list(temp_list, tag=tag, attrs=attrs, text=text)
                elif isinstance(temp_node, list):
                    return self._insert_list(temp_node, tag=tag, attrs=attrs, text=text)
        elif isinstance(node, list):
            if self.get_tag(node) != tag:
                raise AddNodeError('`tag` error.')
            return self._insert_list(node, tag=tag, attrs=attrs, text=text)
        else:
            raise AddNodeError('Add node error, obj must be `ChainDict` type or `List` type.')
        self._reset_locs(node)

    def move(self, move_node: ChainDict, to_node: ChainDict, loc: int=None, _freshen: bool=True) -> None:
        from_node = self.get_parent(move_node)
        tag = self.get_tag(move_node)
        if id(from_node) == id(to_node):
            raise MoveError("`from_node` can't be the same as `to_node`.")
        if tag not in from_node:
            raise NoNodesFound('`from_node` error.')
        else:
            if isinstance(from_node[tag], ChainDict):
                from_node.pop(tag)
            else:
                from_node[tag].remove(move_node)
                from_node = from_node[tag]
            
            if isinstance(to_node, ChainDict):
                if tag not in to_node:
                    self.update_attr(move_node, self.loc_key, str(loc) if loc is not None else self.objects._get_last_loc(to_node))
                    to_node[tag] = move_node
                else:
                    if isinstance(to_node[tag], ChainDict):
                        temp_node = to_node[tag]
                        temp_list = []
                        to_node[tag] = temp_list
                        temp_list.append(temp_node)
                        self.objects.signal_add_node(temp_list, to_node, tag=tag)
                        self.objects.signal_move_node(temp_node, to_node=temp_list)
                        temp_list.append(move_node)
                        to_node = temp_list
                    else:
                        self.update_attr(move_node, self.loc_key, str(loc) if loc is not None else self.objects._get_last_loc(to_node[tag]))
                        to_node[tag].append(move_node)
            else:
                self.update_attr(move_node, self.loc_key, str(loc) if loc is not None else self.objects._get_last_loc(to_node))
                to_node.append(move_node)
                
        self.objects.signal_move_node(move_node, to_node=to_node)
        if _freshen:
            self._reset_locs(from_node)
            self._reset_locs(to_node)

    def pan_up(self, pan_node: ChainDict, up_step: int=0, top: bool=False) -> None:
        if not isinstance(pan_node, ChainDict):
            raise TypeError('`pan_node` must be `ChainDict`.')
        if not (isinstance(up_step, int) and up_step>=0):
            raise TypeError("`up_step` must be `int`, and it's value must be greater than or equal to 0.")

        pan_node_loc = int(pan_node[self.loc_key])
        new_loc = pan_node_loc - up_step
        if new_loc < 0:
            new_loc = 0

        if top: new_loc = 0
        
        change_nodes = sorted(filter(lambda x:int(x[self.loc_key])>=new_loc, self.get_siblings(pan_node)), key=lambda x:int(x[self.loc_key]), reverse=False)
        for i, node in enumerate(change_nodes):
            self.update_attr(node, self.loc_key, str(new_loc+i+1))
        
        self.update_attr(pan_node, self.loc_key, str(new_loc))
    
    def pan_down(self, pan_node: ChainDict, down_step: int=0, bottom: bool=False):
        if not isinstance(pan_node, ChainDict):
            raise TypeError('`pan_node` must be `ChainDict`.')
        if not (isinstance(down_step, int) and down_step>=0):
            raise TypeError("`down_step` must be `int`, and it's value must be greater than or equal to 0.")

        pan_node_loc = int(pan_node[self.loc_key])
        new_loc = pan_node_loc + down_step

        subling_nodes = self.get_siblings(pan_node)
        max_loc = len(subling_nodes)

        if new_loc > max_loc:
            new_loc = max_loc

        if bottom: new_loc = max_loc
        
        change_nodes = sorted(filter(lambda x:int(x[self.loc_key])<=new_loc, subling_nodes), key=lambda x:int(x[self.loc_key]), reverse=False)
        for i, node in enumerate(change_nodes):
            self.update_attr(node, self.loc_key, str(i))
        
        self.update_attr(pan_node, self.loc_key, str(new_loc))

    def swap(self, node1: ChainDict, node2: ChainDict) -> None:
        if not (isinstance(node1, ChainDict) and isinstance(node2, ChainDict)):
            raise TypeError('`node1` and `node2` must be `ChainDict`.')

        node1_loc = node1[self.loc_key]
        self.update_attr(node1, self.loc_key, node2[self.loc_key])
        self.update_attr(node2, self.loc_key, node1_loc)

        if id(self.get_parent(node1)) != id(self.get_parent(node2)):
            node1_loc = node1[self.loc_key]
            node2_loc = node2[self.loc_key]

            node1_parent = self.get_parent(node1)
            self.move(node1, self.get_parent(node2), node1_loc, False)
            self.update_attr(node2, self.loc_key, node2_loc)
            self.move(node2, node1_parent, node2_loc, False)

            self._reset_locs(self.get_parent(node1))
            self._reset_locs(self.get_parent(node2))

    def copy_to(self, aim_node: Union[ChainDict], node_data: Union[ChainDict, List[ChainDict]]) -> None:
        if isinstance(node_data, list):
            for _data in node_data:
                self.objects._revert_data(False)
                temp_node = deepcopy(_data)
                self.objects._revert_data()
                datas = {self.get_tag(_data): temp_node}
                self.objects._build_by_copy(datas, aim_node)
        else:
            self.objects._revert_data(False)
            temp_node = deepcopy(node_data)
            self.objects._revert_data()
            datas = {self.get_tag(node_data): temp_node}
            self.objects._build_by_copy(datas, aim_node)
        
        self._reset_locs(aim_node)

    def insert_xmlstring(self
            , aim_node: ChainDict
            , xml_str: str
            , attr_prefix: str = ATTR_PREFIX
            , cdata_key: str = CDATA_KEY
            , cdata_self_key: str = CDATA_SELF_KEY
            , comment_key: str = COMMENT_KEY
            , loc_key: str = LOC_KEY
            , cdata_separator: str = CDATA_SEPARATOR
            , combine_cdata: bool = True
            , include_comment: bool = False
            , include_loc: bool = True
        ) -> None:
        if not isinstance(aim_node, ChainDict):
            raise TypeError('Only support `ChainDict` type.')
        doc = XmlParser.parse_odict(
            xml_str
            , encoding = None
            , namespace_separator = None
            , attr_prefix = attr_prefix
            , cdata_key = cdata_key
            , cdata_self_key = cdata_self_key
            , comment_key = comment_key
            , combine_cdata = combine_cdata
            , include_comment = include_comment
            , cdata_separator = cdata_separator
            , loc_key = loc_key
            , include_loc = include_loc
        )
        self.objects._build_by_copy(doc[0], aim_node)
        self._reset_locs(aim_node)

    def clear_node_content(self, node: ChainDict) -> None:
        if not isinstance(node, ChainDict):
            raise TypeError('Only support `ChainDict` type.')
        self.clear_text(node)
        for ch in self.get_children(node):
            self.popitem(ch)
    
    def clear_node_attrs(self, node: ChainDict) -> None:
        if not isinstance(node, ChainDict):
            raise TypeError('Only support `ChainDict` type.')
        for attr_name in self.get_attr_names(node):
            self.del_attr(node, attr_name)

    def clear_node(self, node: ChainDict) -> None:
        self.clear_node_content(node)
        self.clear_node_attrs(node)

    def get_xml_data(self) -> str:
        self.objects._revert_data(forward=False)
        output = StringIO()
        unparse_dict(
            self.xml
            , xml_declare = self.xml_declare
            , out_stream = output
            , encoding = self.encoding
            , attr_prefix = self.attr_prefix
            , cdata_key = self.cdata_key
            , cdata_self_key = self.cdata_self_key
            , comment_key = self.comment_key
            , cdata_separator = self.cdata_separator
            , loc_key = self.loc_key
        )
        self.objects._revert_data()
        return output.getvalue()

    def save_as_xml(self, path: str = 'output.xml', encoding='utf-8', distinct: bool=True) -> None:
        self.objects._revert_data(forward=False)
        with open(path, 'w', encoding=encoding) as fp:
            unparse_dict(
                self.xml
                , xml_declare = self.xml_declare
                , out_stream = fp
                , encoding = self.encoding
                , attr_prefix = self.attr_prefix
                , cdata_key = self.cdata_key
                , cdata_self_key = self.cdata_self_key
                , comment_key = self.comment_key
                , cdata_separator = self.cdata_separator
                , loc_key = self.loc_key
                , distinct = distinct
            )
        self.objects._revert_data()

    def save_as_json(self
            , path: str = 'output.json'
            , encoding = 'utf-8'
            , ensure_ascii: bool = True
            , indent = None
            , ori = False
        ) -> None:
        if ori:
            self.objects._revert_data(forward=False)
        with open(path, 'w', encoding=encoding) as fp:
            json.dump(self.xml, fp, ensure_ascii=ensure_ascii, indent=indent)
        if ori:
            self.objects._revert_data()
