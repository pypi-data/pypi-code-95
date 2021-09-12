import json

from pathlib import Path
from typing import Generator, Iterable, Union, overload


@overload
def deduplicate(values: list) -> list:
    """リストから重複を取り除きます。

    この関数はset(values)で順番を破壊したくない場合などに使用します。

    Args:
        values (list): 対象のリストです。

    Returns:
        list: 重複を除去したリストです。
    """
    ...


@overload
def deduplicate(values: tuple) -> tuple:
    """タプルから重複を取り除きます。

    この関数はset(values)で順番を破壊したくない場合などに使用します。

    Args:
        values (tuple): 対象のタプルです。

    Returns:
        tuple: 重複を除去したタプルです。
    """
    ...


def deduplicate(values: Union[list, tuple]) -> Union[list, tuple]:
    f = type(values)
    if f not in (list, tuple):
        msg = f'(list, tuple)いずれかの型である必要があります。'
        raise TypeError(msg)
    res = sorted(set(values), key=values.index)
    return f(res)


def load_json(file: Union[str, Path], encoding: str = 'utf-8', **kwargs) -> Union[dict, list]:
    """json形式のファイルを読み込み、jsonデータを返します。

    キーワード引数にはjson.loadで使用できる引数を与えることができます。

    Args:
        file (Path): json形式のファイルです。
        encoding (str, optional): ファイルのエンコードです。指定しない場合utf-8で扱います。

    Raises:
        FileNotFoundError: ファイルが存在しないかフォルダの場合に投げられます。

    Returns:
        Union[dict, list]: 読み込んだJSONです。
    """
    file = setup_path(file)
    if not file.is_file():
        msg = f'{file}は存在しないかファイルではありません。'
        raise FileNotFoundError(msg)
    with open(file, 'r', encoding=encoding) as f:
        kwargs['fp'] = f
        return json.load(**kwargs)


def read_lines(file: Union[str, Path], ignore_blankline: bool = False, **kwargs) -> Generator[str, None, None]:
    """ファイルを読み込み、1行ずつ返すジェネレータです。

    行右端の改行を自動で除去します。
    
    キーワード引数にはopenで使用できる引数を与えることができますが、modeはrで固定されます。
    encodingは指定しなかった場合utf-8になります。

    Args:
        file (Union[str, Path]): 読み込むファイルです。
        ignore_blankline (bool, optional): line.strip()したときに空文字になる行を無視します。

    Yields:
        Generator[str, None, None]: ファイルの行です。
    """
    file = setup_path(file)
    kwargs['file'] = file
    kwargs['mode'] = 'r'
    if kwargs.get('encoding') is None:
        kwargs['encoding'] = 'utf-8'
    with open(**kwargs) as f:
        gen = map(lambda x: x.rstrip('\n'), f)
        if ignore_blankline:
            gen = filter(lambda x: x.strip(), gen)
        for line in gen:
            yield line


def save_json(file: Union[str, Path], data: Union[dict, list], encoding: str = 'utf-8', **kwargs):
    """指定したファイルにデータをjson形式で書き出します。

    キーワード引数にはjson.dumpで使用できる引数を与えることができます。

    Args:
        file (Path): 出力先のファイルです。
        data (Union[list,dict]): 出力するデータです。
        encoding (str): ファイルのエンコードです。指定しない場合utf-8で扱います。
    """
    file = setup_path(file)
    with open(file, 'w', encoding=encoding) as f:
        kwargs['fp'] = f
        kwargs['obj'] = data
        json.dump(**kwargs)


def setup_path(path: Union[str, Path], is_dir: bool = False) -> Path:
    """親ディレクトリの存在を確認、生成、保証しパスを返します。

    is_dirがTrueの場合にはpathを生成します。

    Args:
        path (Union[str, Path]): 使用したいパスです。
        is_dir (bool, optional): パスがディレクトリかどうかです。

    Returns:
        Path: 使用可能なパスです。
    """
    if not isinstance(path, Path):
        path = Path(path)
    if is_dir:
        p = path
    else:
        p = path.parent

    if not p.exists():
        p.mkdir(parents=True)
    return path


def write_lines(file: Union[str, Path], lines: Iterable, **kwargs):
    """ファイルにlinesを１行ずつ書き出します。

    各行の改行、空白記号はそのまま保持されます。
    そのためlen(lines)とfileに書き出された行数は一致しない場合があります。

    キーワード引数にはopenで使用できる引数を与えることができます。
    modeは指定されていない場合はwになります。
    またmodeが適正かどうかはopen文でチェックされるので、rなどを与えると例外が発生します。
    encodingは指定しなかった場合utf-8になります。

    Args:
        file (Union[str, Path]): 書き出し先のファイルです。
        lines (Iterable): 書き出す行です。
    """
    file = setup_path(file)
    kwargs['file'] = file
    if kwargs.get('mode') is None:
        kwargs['mode'] = 'w'
    if kwargs.get('encoding') is None:
        kwargs['encoding'] = 'utf-8'
    with open(**kwargs) as f:
        for i, line in enumerate(map(str, lines)):
            if i:
                line = f'\n{line}'
            f.write(line)
