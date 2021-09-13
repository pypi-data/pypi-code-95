# 计算文本/文件的MD5值

import hashlib
import os


def hash(input, algorithm):
    """对输入的文本/文件进行HASH

    :param input: 文本/文件
    :type input: str
    :param algorithm: 算法类型：md5/sha1/sha256/sha512
    :type algorithm: str
    :raises TypeError: 类型错误
    :return: 哈希结果
    :rtype: str
    """
    atype = algorithm.lower()
    if atype == 'md5':
        h = hashlib.md5()
    elif atype == 'sha1':
        h = hashlib.sha1()
    elif atype == 'sha256':
        h = hashlib.sha256()
    elif atype == 'sha512':
        h = hashlib.sha512()
    else:
        raise TypeError('Only Support md5/sha1/sha256/sha512.')

    if os.path.isfile(input):
        return _get_md5_of_file(h, input)
    else:
        return _get_hash_of_txt(h, input)


def _get_hash_of_txt(hash, txt):
    hash.update(txt.encode('utf-8'))
    return hash.hexdigest()


def _get_md5_of_file(hash, filepath):
    """获取文件MD5

    :param hash: [description]
    :type hash: bool
    :param filepath: [description]
    :type filepath: [type]
    :return: [description]
    :rtype: [type]
    """
    block_size = 2 * 10
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            hash.update(data)

    return hash.hexdigest()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('f')
    parser.add_argument('-t', help='md5/sha1/sha256/sha512')

    args = parser.parse_args()
    if os.path.isdir(args.f):
        for root, _, files in os.walk(args.f):
            for file in files:
                path = os.path.join(root, file)
                print('{}({}) = {}'.format(args.t, path, hash(path, args.t)))
    else:
        print(hash(args.f, args.t))
