from typing import Any, Generator, Optional, Tuple


def get_dict_keys_position(dict_: dict, *, position: Optional[list] = None) -> Generator[Tuple[Any, Any, Optional[list]], None, None]:
    """辞書のキー、値、辞書内の位置を返します。

    値が辞書の場合、positionにはキーの名前が格納され、階層を示します。
    値が辞書以外の場合、positionはNoneになります。

    Args:
        dict_ (dict): キーの位置を取得したい辞書です。
        position (Optional[list], optional): 辞書内の階層です。

    Yields:
        Generator[Tuple[Any, Any, Optional[list]], None, None]: キー、値、位置のタプルです。

    Examples:
    >>> dict_ = {
    ...     'name': 'Otsuhachi',
    ...     'data': {
    ...         'age': 28,
    ...         'H_W': {
    ...             'height': 167,
    ...             'weight': 74
    ...         }
    ...     },
    ... }
    >>>
    >>> for kvp in get_dict_keys_position(dict_):
    ...     print(kvp)
    ...
    ('name', 'Otsuhachi', None)
    ('age', 28, ['data'])
    ('height', 167, ['data', 'H_W'])
    ('weight', 74, ['data', 'H_W'])
    """
    for k, v in dict_.items():
        if isinstance(v, dict):
            if position is None:
                position = []
            yield from get_dict_keys_position(v, position=position + [k])
        else:
            yield (k, v, position)


def support_json_dump(o: Any):
    """JSONで変換できないオブジェクトをstrとして返します。

    to_jsonメソッドを定義していればそちらを優先して使用します。

    Args:
        o (Any): JSONで変換できないオブジェクトです。

    Returns:
        str: str(o)です。
    """
    if hasattr(o, 'to_json'):
        return o.to_json()
    return str(o)
