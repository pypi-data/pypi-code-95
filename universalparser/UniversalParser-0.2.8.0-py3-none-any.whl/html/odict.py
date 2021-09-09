from html.parser import HTMLParser
from collections import OrderedDict
from typing import List
from UniversalParser._ntype import *
from ._ntype import *

class UPHTMLParser(HTMLParser):

    def __init__(self, *
            , convert_charrefs: bool
            , attr_prefix: str = ATTR_PREFIX
            , cdata_key: str = CDATA_KEY
            , comment_key: str = COMMENT_KEY
            , include_comment: bool = False
            , cdata_separator: str = CDATA_SEPARATOR
            , loc_key: str = LOC_KEY
            , include_loc: bool = False
        ) -> None:
        super().__init__(convert_charrefs=convert_charrefs)

        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.cdata_separator = cdata_separator
        self.include_comment = include_comment
        self.comment_key = comment_key
        self.include_loc = include_loc
        self.loc_key = loc_key

        self.documentation: OrderedDict = OrderedDict({})
        self.stack_nodes: List[OrderedDict] = [[self.documentation, [], 0], ]
        self.temp_loc: int = 0
        self.flag_out: int = 0

    def handle_starttag(self, tag, attrs):
        if 0 == self.flag_out: # only in.
            self.temp_loc = 0
        current_node = self.stack_nodes[-1][0]
        node = OrderedDict({})
        self.stack_nodes.append([node, [], self.temp_loc])
        for attr_name, attr_value in attrs:
            node[f'{self.attr_prefix}{attr_name}'] = attr_value
        if self.include_loc:
            node[f'{self.attr_prefix}{self.loc_key}'] = f'{self.temp_loc}'
        if tag in current_node:
            sub_node = current_node[tag]
            if isinstance(sub_node, OrderedDict):
                current_node[tag] = [sub_node, node, ]
            elif isinstance(sub_node, list):
                current_node[tag].append(node)
        else:
            current_node.update(OrderedDict({tag: node}))
        self.flag_out = 0

        if tag in HTML_SINGLE_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.stack_nodes.pop()
        node[0][self.cdata_key] = self.cdata_separator.join(node[1])

        self.flag_out = 1
        self.temp_loc = f'{int(node[2])+1}'

    def handle_startendtag(self, tag, attrs):
        if 0 == self.flag_out:
            self.temp_loc = 0
        current_node = self.stack_nodes[-1][0]
        node = OrderedDict({})
        self.stack_nodes.append([node, [], self.temp_loc])
        for attr_name, attr_value in attrs:
            node[f'{self.attr_prefix}{attr_name}'] = attr_value
        if self.include_loc:
            node[f'{self.attr_prefix}{self.loc_key}'] = f'{self.temp_loc}'
        if tag in current_node:
            sub_node = current_node[tag]
            if isinstance(sub_node, OrderedDict):
                current_node[tag] = [sub_node, node, ]
            elif isinstance(sub_node, list):
                current_node[tag].append(node)
        else:
            current_node.update(OrderedDict({tag: node}))
        self.flag_out = 0
        self.handle_endtag(tag)

    def handle_data(self, data):
        t_data = data.strip()
        if t_data:
            self.stack_nodes[-1][1].append(t_data)

    # def handle_entityref(self, name):
    #     ...

    def handle_comment(self, data):
        if self.include_comment:
            node = self.stack_nodes[-1][0]
            if self.comment_key in node:
                node[self.comment_key].append(data.strip())
            else:
                node[self.comment_key] = [data.strip(), ]

def parse_odict(html_data: str
        , convert_charrefs: bool = True
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , comment_key: str = COMMENT_KEY
        , include_comment: bool = False
        , cdata_separator: str = CDATA_SEPARATOR
        , loc_key: str = LOC_KEY
        , include_loc: bool = False
    ) -> OrderedDict:

    parser = UPHTMLParser(convert_charrefs=convert_charrefs
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , comment_key = comment_key
        , include_comment = include_comment
        , cdata_separator = cdata_separator
        , loc_key = loc_key
        , include_loc = include_loc
    )
    parser.feed(html_data)
    html = parser.documentation
    parser.close()
    return html
